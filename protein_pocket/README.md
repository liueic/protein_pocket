Protein pocket detection pipeline

Usage

1) Activate env

    conda activate protein-pocket

2) Run pipeline

    protein-pocket run path/to/protein.pdb --workdir runs --topk 5 --prank-home /path/to/p2rank

Notes

- Requires fpocket on PATH (installed via conda env).
- P2Rank must be installed and its launcher `p2rank` available, or pass --prank-home.
