"""Post-hoc uncertainty sensitivity: cluster board-equivalent D4 openings.

Changes no engine, tournament result or prespecified exact-opening summary.
Run with the downloaded id-named ZIPs used by both artifact manifests.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import zipfile

from benchmarks.competitive.corpus import transform_cell
from benchmarks.competitive.metrics import paired_interval


def canonical_opening(opening):
    variants = []
    for rotation in range(4):
        for reflect in range(2):
            variants.append(tuple(sorted(
                (index % 2 + 1, *transform_cell(move, rotation, reflect))
                for index, move in enumerate(opening))))
    return min(variants)


def analyze(archives, root):
    records = []
    manifests = ('artifact-manifest.json', 'replica-artifact-manifest.json')
    for manifest_name in manifests:
        manifest = json.loads((root / manifest_name).read_text())
        for artifact in manifest['artifacts']:
            path = archives / (str(artifact['id']) + '.zip')
            raw = path.read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            assert digest == artifact['archive_sha256']
            with zipfile.ZipFile(path) as archive:
                for name in archive.namelist():
                    if (not name.endswith('.jsonl')
                            or name.startswith(('engine', 'server'))):
                        continue
                    summary = json.loads(archive.read(name[:-1]))
                    clusters = defaultdict(list)
                    games = [json.loads(line) for line in
                             archive.read(name).splitlines()]
                    assert len(games) == summary['games']
                    for game in games:
                        key = canonical_opening(game['opening'])
                        clusters[key].append(game['candidate_score'])
                    scores = [sum(v) / len(v) for v in clusters.values()]
                    records.append({
                        'comparison': name.removesuffix('.jsonl'),
                        'source_sha': summary['environment']['source_sha'],
                        'workflow_run_id': manifest['workflow_run_id'],
                        'artifact_id': artifact['id'], 'games': len(games),
                        'exact_opening_clusters':
                            summary['unique_opening_clusters'],
                        'canonical_d4_board_clusters': len(clusters),
                        'equal_canonical_cluster_score':
                            sum(scores) / len(scores),
                        'canonical_cluster_bootstrap95':
                            paired_interval(scores),
                        'prespecified_exact_cluster_bootstrap95':
                            summary['score_rate_paired_bootstrap95'],
                    })
    return {
        'scope': ('Post-hoc sensitivity analysis; not new games or a new '
                  'independent replication.'),
        'estimand': ('Equal-weight canonical D4 board clusters, preserving '
                     'stone colors and side to move; this differs from '
                     'game-weighted score and exact-opening-weighted score.'),
        'limitations': ('Does not make these seeded openings representative '
                        'of human games or remove all strategic dependence '
                        'between related opening families.'),
        'records': records,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archives', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.archives, Path(__file__).parent)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
