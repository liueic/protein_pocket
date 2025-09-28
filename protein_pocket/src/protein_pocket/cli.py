from typing import Optional

import typer
from rich.console import Console

app = typer.Typer(add_completion=False, help="Protein pocket detection pipeline CLI")
console = Console()


@app.callback()
def main_callback() -> None:
    """Protein pocket detection pipeline."""
    return None


@app.command()
def version() -> None:
    """Show version info."""
    from importlib.metadata import version, PackageNotFoundError

    try:
        v = version("protein-pocket")
    except PackageNotFoundError:
        v = "0.1.0"
    console.print(f"protein-pocket {v}")


@app.command()
def run(
    pdb_path: str = typer.Argument(..., help="Path to input PDB file"),
    workdir: str = typer.Option("runs", help="Working directory for intermediate outputs"),
    topk: int = typer.Option(5, help="Number of top pockets to keep after rescoring"),
    prank_home: Optional[str] = typer.Option(None, help="P2Rank home directory (optional, will auto-install if not found)"),
    enable_cliff_analysis: bool = typer.Option(True, help="Enable cliff analysis for high-confidence pocket identification"),
) -> None:
    """Run the full pipeline: fpocket -> refine/filter -> P2Rank rescoring -> cliff analysis -> rank.
    
    The pipeline will automatically download and install P2Rank if not found.
    Cliff analysis identifies high-confidence pockets using the 'cliff' algorithm.
    """
    from .pipeline import run_pipeline

    run_pipeline(
        pdb_path=pdb_path,
        workdir=workdir,
        topk=topk,
        prank_home=prank_home,
        enable_cliff_analysis=enable_cliff_analysis,
    )


@app.command()
def batch(
    input_dir: str = typer.Argument(..., help="Directory containing protein structure files"),
    results_dir: str = typer.Option("results", help="Output directory for results (maintains input directory structure)"),
    topk: int = typer.Option(5, help="Number of top pockets to keep after rescoring"),
    prank_home: Optional[str] = typer.Option(None, help="P2Rank home directory (optional, will auto-install if not found)"),
    output_csv: str = typer.Option("batch_results.csv", help="Output CSV file for batch results"),
    file_extensions: str = typer.Option("pdb,cif", help="Comma-separated file extensions to process"),
    max_workers: Optional[int] = typer.Option(None, help="Maximum number of parallel workers (default: min(CPU cores, 8))"),
    enable_cliff_analysis: bool = typer.Option(True, help="Enable cliff analysis for high-confidence pocket identification"),
) -> None:
    """Batch process multiple protein structure files in a directory.
    
    Processes all protein files in the specified directory and generates a summary CSV.
    Results are saved to the results directory, maintaining the same folder structure as input.
    Includes cliff analysis results in the output CSV for high-confidence pocket identification.
    """
    from .batch import run_batch_pipeline

    run_batch_pipeline(
        input_dir=input_dir,
        results_dir=results_dir,
        topk=topk,
        prank_home=prank_home,
        output_csv=output_csv,
        file_extensions=file_extensions,
        max_workers=max_workers,
    )


