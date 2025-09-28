from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple


@dataclass
class Site:
    center_x: float
    center_y: float
    center_z: float


def distance(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> float:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    dz = a[2] - b[2]
    return (dx * dx + dy * dy + dz * dz) ** 0.5


def recall_top_n_plus_2(
    predicted_centers: Iterable[Tuple[float, float, float]],
    gt_sites: List[Site],
    hit_threshold: float = 4.0,
) -> float:
    n = len(gt_sites)
    k = n + 2
    preds = list(predicted_centers)[:k]
    hits = 0
    for site in gt_sites:
        site_center = (site.center_x, site.center_y, site.center_z)
        if any(distance(site_center, p) <= hit_threshold for p in preds):
            hits += 1
    return hits / max(1, n)


