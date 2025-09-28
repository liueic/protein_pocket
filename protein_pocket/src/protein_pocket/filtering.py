from __future__ import annotations

from typing import List, Set

from .fpocket import Pocket


def jaccard_residue_overlap(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union > 0 else 0.0


def group_overlapping_pockets(
    pockets: List[Pocket],
    center_distance_threshold: float = 5.0,
    residue_jaccard_threshold: float = 0.75,
) -> list[list[int]]:
    groups: list[list[int]] = []
    visited = [False] * len(pockets)

    def is_overlapped(i: int, j: int) -> bool:
        pi, pj = pockets[i], pockets[j]
        dx = pi.center_x - pj.center_x
        dy = pi.center_y - pj.center_y
        dz = pi.center_z - pj.center_z
        dist = (dx * dx + dy * dy + dz * dz) ** 0.5
        if dist <= center_distance_threshold:
            return True
        ja = jaccard_residue_overlap(set(pi.residues), set(pj.residues))
        return ja >= residue_jaccard_threshold

    for i in range(len(pockets)):
        if visited[i]:
            continue
        stack = [i]
        group: list[int] = []
        visited[i] = True
        while stack:
            u = stack.pop()
            group.append(u)
            for v in range(len(pockets)):
                if visited[v] or v == u:
                    continue
                if is_overlapped(u, v):
                    visited[v] = True
                    stack.append(v)
        groups.append(group)
    return groups


def deduplicate_pockets(pockets: List[Pocket]) -> List[Pocket]:
    groups = group_overlapping_pockets(pockets)
    kept: list[Pocket] = []
    for g in groups:
        best_idx = max(g, key=lambda idx: pockets[idx].raw_score)
        kept.append(pockets[best_idx])
    return kept


