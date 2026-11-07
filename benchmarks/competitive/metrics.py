"""Recorded experiment provenance and uncertainty (no production credentials)."""
import hashlib
import math
import platform
import random
import subprocess
from pathlib import Path


def wilson(successes, total, z=1.959963984540054):
    if not total:
        return None
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    radius = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return [max(0.0, center - radius), min(1.0, center + radius)]


def paired_interval(pair_scores, seed=0, samples=5000):
    """Bootstrap opening-pair clusters, not correlated color-swapped games."""
    if len(pair_scores) < 2:
        return None
    rng = random.Random(seed)
    estimates = sorted(sum(rng.choices(pair_scores, k=len(pair_scores))) / len(pair_scores) for _ in range(samples))
    return [estimates[int(.025 * samples)], estimates[min(samples - 1, int(.975 * samples))]]


def percentile(values, q):
    return sorted(values)[max(0, math.ceil(len(values) * q) - 1)] if values else None


def provenance(root):
    root = Path(root).resolve()
    tracked = sorted((root / 'app/ai').glob('*.py'))
    tracked += sorted((root / 'benchmarks/competitive').glob('*.py'))
    h = hashlib.sha256()
    for path in tracked:
        h.update(str(path.relative_to(root)).encode())
        h.update(path.read_bytes())
    cpu = 'unknown'
    if Path('/proc/cpuinfo').exists():
        cpu = next((line.split(':', 1)[1].strip() for line in Path('/proc/cpuinfo').read_text().splitlines()
                    if line.startswith('model name')), 'unknown')
    return {
        'source_sha': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
        'working_tree_dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=root, text=True).strip()),
        'source_content_sha256': h.hexdigest(), 'python': platform.python_version(),
        'platform': platform.platform(), 'cpu': cpu,
        'packages': subprocess.check_output([__import__('sys').executable, '-m', 'pip', 'freeze'], text=True).splitlines(),
        'percentiles': 'nearest_rank', 'clock': 'perf_counter_ns',
    }
