"""Unit tests for post-acceptance production QA shutdown."""

import json

import pytest

from scripts import production_qa_shutdown as shutdown


IMAGE_REF = "docker.io/example/caroai:" + ("a" * 40)


class FakeResponse:
    def __init__(self, status, payload=None):
        self.status = status
        self._body = (
            payload
            if isinstance(payload, bytes)
            else json.dumps(payload or {}).encode("utf-8")
        )

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


def configure_environment(monkeypatch, tmp_path):
    values = {
        "RENDER_SERVICE_ID": "srv-test",
        "RENDER_API_KEY": "render-api-key-not-logged",
        "RENDER_DEPLOY_HOOK": "https://api.render.com/deploy/srv-test?key=hook-secret",
        "PUBLIC_URL": "https://caroai.example",
        "IMAGE_NAME": "docker.io/example/caroai",
        "GITHUB_SHA": "a" * 40,
        "QA_ACCEPTANCE_OUTCOME": "success",
        "GITHUB_STEP_SUMMARY": str(tmp_path / "summary.md"),
    }
    for key, value in values.items():
        monkeypatch.setenv(key, value)


def install_successful_render_stub(monkeypatch, *, qa_status=404, image_ref=IMAGE_REF):
    calls = []

    def fake_urlopen(request, timeout):
        del timeout
        method = request.get_method()
        url = request.full_url
        calls.append((method, url, request.data))

        if method == "PUT" and url.endswith("/env-vars/CAROAI_QA_ENABLED"):
            assert json.loads(request.data.decode("utf-8")) == {"value": "false"}
            return FakeResponse(200)
        if method == "GET" and "/deploy/srv-test?" in url:
            assert "imgURL=" in url
            return FakeResponse(200, {"deploy": {"id": "dep-test"}})
        if method == "GET" and url.endswith("/deploys/dep-test"):
            return FakeResponse(
                200,
                {"status": "live", "image": {"ref": image_ref}},
            )
        if url.endswith("/api/qa/games") or url.endswith("/api/qa/runs"):
            return FakeResponse(qa_status)
        if any(url.endswith(path) for path in shutdown.PUBLIC_ENDPOINTS):
            return FakeResponse(200)
        raise AssertionError(f"Unexpected request: {method} {url}")

    monkeypatch.setattr(shutdown, "urlopen", fake_urlopen)
    monkeypatch.setattr(shutdown.time, "sleep", lambda _seconds: None)
    return calls


def test_shutdown_disables_qa_deploys_exact_image_and_verifies_public_routes(
    monkeypatch, tmp_path, capsys
):
    configure_environment(monkeypatch, tmp_path)
    calls = install_successful_render_stub(monkeypatch)

    shutdown.run_shutdown()

    output = capsys.readouterr().out
    summary = (tmp_path / "summary.md").read_text(encoding="utf-8")
    assert "CAROAI_QA_ENABLED=false" in output
    assert "POST /api/qa/games verified (HTTP 404)" in output
    assert "DELETE /api/qa/runs verified (HTTP 404)" in output
    assert "GET /ready verified (HTTP 200)" in output
    assert IMAGE_REF in summary
    assert "QA create and cleanup routes: HTTP 404" in summary
    assert any(
        method == "PUT" and url.endswith("/env-vars/CAROAI_QA_ENABLED")
        for method, url, _data in calls
    )
    assert any(
        method == "GET" and "/deploy/srv-test?" in url and "imgURL=" in url
        for method, url, _data in calls
    )


def test_shutdown_fails_closed_when_qa_route_does_not_return_404(
    monkeypatch, tmp_path
):
    configure_environment(monkeypatch, tmp_path)
    calls = install_successful_render_stub(monkeypatch, qa_status=401)

    with pytest.raises(RuntimeError, match="expected HTTP 404"):
        shutdown.run_shutdown()

    assert any(
        method == "PUT" and url.endswith("/env-vars/CAROAI_QA_ENABLED")
        for method, url, _data in calls
    )


def test_shutdown_rejects_live_deployment_with_an_unexpected_image(
    monkeypatch, tmp_path
):
    configure_environment(monkeypatch, tmp_path)
    install_successful_render_stub(
        monkeypatch,
        image_ref="docker.io/example/caroai:" + ("b" * 40),
    )

    with pytest.raises(RuntimeError, match="unexpected image"):
        shutdown.run_shutdown()


def test_shutdown_rejects_non_https_public_url(monkeypatch, tmp_path):
    configure_environment(monkeypatch, tmp_path)
    monkeypatch.setenv("PUBLIC_URL", "http://caroai.example")

    with pytest.raises(RuntimeError, match="clean HTTPS origin"):
        shutdown.run_shutdown()


def test_shutdown_rejects_partial_commit_sha(monkeypatch, tmp_path):
    configure_environment(monkeypatch, tmp_path)
    monkeypatch.setenv("GITHUB_SHA", "abc123")

    with pytest.raises(RuntimeError, match="full 40-character"):
        shutdown.run_shutdown()
