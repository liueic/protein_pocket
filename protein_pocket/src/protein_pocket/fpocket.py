from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class Pocket:
    center_x: float
    center_y: float
    center_z: float
    raw_score: float
    score: float
    residues: List[str]


def run_fpocket(pdb_path: str | Path, work_dir: Path) -> Path:
    pdb_path = Path(pdb_path)
    
    # Check if input file exists
    if not pdb_path.exists():
        raise FileNotFoundError(f"Input file not found: {pdb_path}")
    
    # fpocket creates output in the same directory as the input PDB
    # with suffix "_out", so we need to look for that
    expected_out_dir = pdb_path.parent / (pdb_path.stem + "_out")
    
    # Run fpocket
    cmd = ["fpocket", "-f", str(pdb_path)]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"fpocket stdout: {result.stdout}")
        if result.stderr:
            print(f"fpocket stderr: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"fpocket failed with return code {e.returncode}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        raise
    
    # Move the output to our work directory
    work_out_dir = work_dir / (pdb_path.stem + "_fpocket")
    if expected_out_dir.exists():
        import shutil
        if work_out_dir.exists():
            shutil.rmtree(work_out_dir)
        shutil.move(str(expected_out_dir), str(work_out_dir))
    else:
        raise FileNotFoundError(f"fpocket output directory not found: {expected_out_dir}")
    
    return work_out_dir


def read_fpocket_pockets(fp_out_dir: Path) -> List[Pocket]:
    # Find the info.txt file
    info_files = list(fp_out_dir.glob("*_info.txt"))
    if not info_files:
        raise FileNotFoundError(f"No fpocket info.txt found in {fp_out_dir}")
    
    info_file = info_files[0]
    pockets: List[Pocket] = []
    
    # Parse the info.txt file
    with open(info_file, 'r') as f:
        content = f.read()
    
    # Split by pocket sections
    pocket_sections = content.split("Pocket ")[1:]  # Skip empty first element
    
    for i, section in enumerate(pocket_sections, 1):
        lines = section.strip().split('\n')
        score = 0.0
        center_x = center_y = center_z = 0.0
        residues = []
        
        for line in lines:
            if "Score :" in line:
                score = float(line.split(":")[1].strip())
        
        # Try to get center coordinates from the corresponding pocket PDB file
        pocket_pdb = fp_out_dir / "pockets" / f"pocket{i}_atm.pdb"
        if pocket_pdb.exists():
            # Parse PDB to get center coordinates
            coords = []
            with open(pocket_pdb, 'r') as f:
                for line in f:
                    if line.startswith("ATOM"):
                        x = float(line[30:38].strip())
                        y = float(line[38:46].strip())
                        z = float(line[46:54].strip())
                        coords.append((x, y, z))
            
            if coords:
                center_x = sum(c[0] for c in coords) / len(coords)
                center_y = sum(c[1] for c in coords) / len(coords)
                center_z = sum(c[2] for c in coords) / len(coords)
        
        pockets.append(
            Pocket(
                center_x=center_x,
                center_y=center_y,
                center_z=center_z,
                raw_score=score,
                score=score,
                residues=residues,
            )
        )
    
    return pockets


