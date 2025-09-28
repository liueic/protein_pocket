from __future__ import annotations

import csv
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

from .fpocket import Pocket
from .installer import ensure_p2rank_installed


@dataclass
class ScoredPocket(Pocket):
    score: float


def export_pockets_to_prank_csv(pockets: Iterable[Pocket], out_csv: Path) -> None:
    with out_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["x", "y", "z"])  # centers only; P2Rank accepts centers
        for p in pockets:
            w.writerow([f"{p.center_x:.3f}", f"{p.center_y:.3f}", f"{p.center_z:.3f}"])


def rescore_with_p2rank(
    pockets: List[Pocket], pdb_path: Path, work_dir: Path, prank_home: Optional[str] = None
) -> List[ScoredPocket]:
    out_dir = work_dir / "p2rank_out"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 使用提供的P2Rank路径（如果已预先检查）或进行检查
    if prank_home and Path(prank_home).exists():
        # 如果提供了路径且存在，直接使用（避免重复检查）
        p2rank_path = Path(prank_home)
    else:
        # 否则进行完整的安装检查
        p2rank_path = ensure_p2rank_installed(prank_home)

    # Create a dataset file for P2Rank rescore
    dataset_file = out_dir / "fpocket_dataset.ds"
    
    # Find the actual fpocket output file (could be .pdb or .cif)
    fpocket_dir = work_dir / f"{pdb_path.stem}_fpocket"
    fpocket_out_pdb = fpocket_dir / f"{pdb_path.stem}_out.pdb"
    fpocket_out_cif = fpocket_dir / f"{pdb_path.stem}_out.cif"
    
    # Use the file that actually exists
    if fpocket_out_pdb.exists():
        fpocket_output_file = fpocket_out_pdb
    elif fpocket_out_cif.exists():
        fpocket_output_file = fpocket_out_cif
    else:
        raise FileNotFoundError(f"fpocket output file not found. Expected either {fpocket_out_pdb} or {fpocket_out_cif}")
    
    # Use absolute paths for P2Rank
    abs_fpocket_pdb = fpocket_output_file.resolve()
    abs_pdb_path = pdb_path.resolve()
    
    with open(dataset_file, 'w') as f:
        f.write("PARAM.PREDICTION_METHOD=fpocket\n")
        f.write("HEADER: prediction protein\n")
        f.write(f"{abs_fpocket_pdb}  {abs_pdb_path}\n")

    env = os.environ.copy()
    env["P2RANK_HOME"] = str(p2rank_path)

    # Use the prank script from P2RANK_HOME with rescore command
    prank_script = p2rank_path / "prank"
    cmd = [
        str(prank_script),
        "rescore",
        str(dataset_file),
        "-o",
        str(out_dir),
    ]
    subprocess.run(cmd, check=True, env=env)

    # Read P2Rank rescore results
    # The output files are directly in out_dir with full filename
    scores_csv = out_dir / f"{pdb_path.name}_predictions.csv"
    
    if not scores_csv.exists():
        # Try alternative naming
        scores_csv = out_dir / "predictions.csv"
        if not scores_csv.exists():
            raise FileNotFoundError(f"P2Rank rescore predictions CSV not found in {out_dir}")

    rescored: list[ScoredPocket] = []
    with scores_csv.open() as f:
        r = csv.DictReader(f)
        for row in r:
            # P2Rank rescore output has center_x, center_y, center_z columns with spaces
            # Clean up the keys and values to handle extra spaces
            clean_row = {k.strip(): v.strip() for k, v in row.items()}
            
            x = float(clean_row.get("center_x", "0.0"))
            y = float(clean_row.get("center_y", "0.0"))
            z = float(clean_row.get("center_z", "0.0"))
            score = float(clean_row.get("score", "0.0"))
            
            # Use the P2Rank coordinates directly instead of matching
            rescored.append(
                ScoredPocket(
                    center_x=x,
                    center_y=y,
                    center_z=z,
                    raw_score=0.0,  # We don't have the original fpocket score here
                    score=score,
                    residues=[],  # We don't have residue info in the CSV
                )
            )

    return rescored


