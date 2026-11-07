"""Close production QA routes after the release acceptance attempt."""

from __future__ import annotations

import json
import os
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


POLL_ATTEMPTS = 60
POLL_INTERVAL_SECONDS = 10
ENDPOINT_ATTEMPTS = 12
ENDPOINT_INTERVAL_SECONDS = 5
REQUEST_TIMEOUT_SECONDS = 20
FAILED_DEPLOY_STATUSES = {
    "build_failed",
    "update_failed",
    "pre_deploy_failed",
    "canceled",
    "deactivated",
}
QA_DISABLED_ENDPOINTS = (
    ("POST", "/api/qa/games", {"mode": "HUMAN_VS_HUMAN"}),
    ("DELETE", "/api/qa/runs", None),
)
PUBLIC_ENDPOINTS = (
    "/health",
    "/ready",
    "/",
    "/history.html",
    "/api/history",
    "/tokens.css",
)


def _request_status(request: Request) -> tuple[int | None, bytes]:
    """Return HTTP status/body without exposing request URLs or credentials."""
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return response.status, response.read()
    except HTTPError as exc:
        return exc.code, exc.read()
    except URLError:
        return None, b""


def _decode_json(body: bytes, operation: str) -> dict:
    try:
        value = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise RuntimeError(f"{operation} returned invalid JSON") from None
    if not isinstance(value, dict):
        raise RuntimeError(f"{operation} returned an unexpected JSON shape")
    return value


def _require_status(request: Request, expected: int, operation: str) -> bytes:
    status, body = _request_status(request)
    if status != expected:
        rendered = "no response" if status is None else f"HTTP {status}"
        raise RuntimeError(f"{operation} failed ({rendered})")
    return body


def _disable_qa_flag(service_id: str, api_key: str) -> None:
    """Persist the fail-closed runtime flag without replacing other env vars."""
    from urllib.parse import quote

    url = (
        "https://api.render.com/v1/services/"
        f"{quote(service_id, safe='')}/env-vars/CAROAI_QA_ENABLED"
    )
    request = Request(
        url,
        data=json.dumps({"value": "false"}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        method="PUT",
    )
    _require_status(request, 200, "Render QA-disable configuration update")
    print("Render service variable CAROAI_QA_ENABLED set to false.")


def _trigger_exact_image_deploy(deploy_hook: str, image_ref: str) -> str:
    """Deploy the requested immutable image after the env-var update."""
    parsed = urlsplit(deploy_hook)
    query = parsed.query
    image_query = urlencode({"imgURL": image_ref})
    combined_query = f"{query}&{image_query}" if query else image_query
    url = urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, combined_query, parsed.fragment)
    )
    request = Request(url, headers={"Accept": "application/json"}, method="GET")
    payload = _decode_json(
        _require_status(request, 200, "Render deploy-hook request"),
        "Render deploy hook",
    )
    deploy = payload.get("deploy")
    deploy_id = deploy.get("id") if isinstance(deploy, dict) else None
    if not isinstance(deploy_id, str) or not deploy_id:
        raise RuntimeError("Render deploy hook did not return a deployment ID")
    print(f"Render QA-disable deployment ID: {deploy_id}")
    return deploy_id


def _wait_for_exact_image(
    service_id: str, api_key: str, deploy_id: str, expected_image: str
) -> None:
    from urllib.parse import quote

    url = (
        "https://api.render.com/v1/services/"
        f"{quote(service_id, safe='')}/deploys/{quote(deploy_id, safe='')}"
    )
    request = Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        },
        method="GET",
    )

    for attempt in range(1, POLL_ATTEMPTS + 1):
        status, body = _request_status(request)
        if status == 200:
            payload = _decode_json(body, "Render deployment status")
            deploy_status = payload.get("status")
            image = payload.get("image")
            image_ref = image.get("ref") if isinstance(image, dict) else None
            print(
                f"Render QA-disable deploy status={deploy_status} "
                f"image={image_ref or 'unknown'}"
            )
            if deploy_status == "live":
                if image_ref != expected_image:
                    raise RuntimeError(
                        "Render QA-disable deploy is live with an unexpected image"
                    )
                print("Render confirms the exact full-SHA image is live.")
                return
            if deploy_status in FAILED_DEPLOY_STATUSES:
                raise RuntimeError(
                    f"Render QA-disable deployment ended with {deploy_status}"
                )
        elif status is not None:
            raise RuntimeError(
                f"Could not inspect Render QA-disable deployment (HTTP {status})"
            )

        if attempt < POLL_ATTEMPTS:
            time.sleep(POLL_INTERVAL_SECONDS)

    raise RuntimeError("Timed out waiting for the QA-disabled image to become live")


def _check_endpoint(
    base_url: str,
    method: str,
    path: str,
    expected_status: int,
    payload: dict | None = None,
) -> None:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {}
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = Request(
        f"{base_url}{path}",
        data=body,
        headers=headers,
        method=method,
    )
    last_status = None

    for attempt in range(1, ENDPOINT_ATTEMPTS + 1):
        status, _response_body = _request_status(request)
        last_status = status
        if status == expected_status:
            print(f"{method} {path} verified (HTTP {expected_status}).")
            return
        if attempt < ENDPOINT_ATTEMPTS:
            time.sleep(ENDPOINT_INTERVAL_SECONDS)

    actual = "no response" if last_status is None else f"HTTP {last_status}"
    raise RuntimeError(
        f"{method} {path} expected HTTP {expected_status}, received {actual}"
    )


def _write_summary(
    summary_path: str,
    image_ref: str,
    deploy_id: str,
    acceptance_outcome: str,
) -> None:
    if not summary_path:
        return

    lines = [
        "",
        "### Production QA auto-disable and post-release verification",
        "- Render runtime flag: `CAROAI_QA_ENABLED=false`",
        f"- QA-disable deployment: `{deploy_id}`",
        f"- Verified live image: `{image_ref}`",
        "- QA create and cleanup routes: HTTP 404",
        "- Health, readiness, dashboard, and history endpoints: HTTP 200",
        f"- Gameplay/cleanup acceptance step outcome: `{acceptance_outcome}`",
    ]
    if acceptance_outcome != "success":
        lines.append(
            "- The QA routes were closed, but the earlier acceptance step did "
            "not pass; inspect its logs and use the documented exact-run "
            "recovery procedure if cleanup was incomplete."
        )
    with open(summary_path, "a", encoding="utf-8") as summary:
        summary.write("\n".join(lines) + "\n")


def run_shutdown() -> None:
    """Disable QA, deploy that configuration, and verify production behavior."""
    service_id = os.environ.get("RENDER_SERVICE_ID", "").strip()
    api_key = os.environ.get("RENDER_API_KEY", "")
    deploy_hook = os.environ.get("RENDER_DEPLOY_HOOK", "")
    public_url = os.environ.get("PUBLIC_URL", "").strip()
    image_name = os.environ.get("IMAGE_NAME", "").strip().rstrip("/")
    commit_sha = os.environ.get("GITHUB_SHA", "").strip()
    acceptance_outcome = os.environ.get("QA_ACCEPTANCE_OUTCOME", "unknown")

    required = {
        "RENDER_SERVICE_ID": service_id,
        "RENDER_API_KEY": api_key,
        "RENDER_DEPLOY_HOOK": deploy_hook,
        "PUBLIC_URL": public_url,
        "IMAGE_NAME": image_name,
        "GITHUB_SHA": commit_sha,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing required release configuration: " + ", ".join(missing)
        )

    parsed_url = urlsplit(public_url)
    if (
        parsed_url.scheme != "https"
        or not parsed_url.hostname
        or parsed_url.path
        or parsed_url.query
        or parsed_url.fragment
        or parsed_url.username
        or parsed_url.password
    ):
        raise RuntimeError("PUBLIC_URL must be a clean HTTPS origin")
    if not re.fullmatch(r"[0-9a-f]{40}", commit_sha):
        raise RuntimeError("GITHUB_SHA must be a full 40-character commit SHA")

    base_url = public_url.rstrip("/")
    image_ref = f"{image_name}:{commit_sha}"

    _disable_qa_flag(service_id, api_key)
    deploy_id = _trigger_exact_image_deploy(deploy_hook, image_ref)
    _wait_for_exact_image(service_id, api_key, deploy_id, image_ref)

    for method, path, payload in QA_DISABLED_ENDPOINTS:
        _check_endpoint(base_url, method, path, 404, payload)

    for path in PUBLIC_ENDPOINTS:
        _check_endpoint(base_url, "GET", path, 200)

    _write_summary(
        os.environ.get("GITHUB_STEP_SUMMARY", ""),
        image_ref,
        deploy_id,
        acceptance_outcome,
    )
    print(
        "Production QA auto-disable passed: QA routes return HTTP 404; "
        "ordinary production endpoints remain healthy."
    )
    if acceptance_outcome != "success":
        print(
            "The prior gameplay/cleanup acceptance did not pass. "
            "The QA routes are nevertheless disabled; inspect its run logs."
        )


def main() -> int:
    try:
        run_shutdown()
    except RuntimeError as exc:
        print(f"Production QA auto-disable failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
