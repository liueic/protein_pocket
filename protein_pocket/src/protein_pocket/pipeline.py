from pathlib import Path
from typing import Optional, NamedTuple
from dataclasses import dataclass

from rich.console import Console

from .fpocket import run_fpocket, read_fpocket_pockets
from .filtering import deduplicate_pockets
from .p2rank import rescore_with_p2rank
from .cliff_analysis import analyze_cliff_pattern, CliffAnalysisResult


console = Console()


@dataclass
class PipelineResult:
    """Pipeline 处理结果"""
    top_pockets: list
    num_pockets_detected: int
    num_pockets_filtered: int
    all_pockets: list  # 所有检测到的口袋（用于排名变化计算）
    filtered_pockets: list  # 过滤后的口袋（用于排名变化计算）
    cliff_analysis: Optional[CliffAnalysisResult] = None  # 断崖分析结果


def run_pipeline(
    pdb_path: str,
    workdir: str,
    topk: int,
    prank_home: Optional[str] = None,
    return_results: bool = False,
    enable_cliff_analysis: bool = True,
) -> Optional[PipelineResult]:
    work_dir = Path(workdir)
    work_dir.mkdir(parents=True, exist_ok=True)

    if not return_results:
        console.rule("fpocket")
    fp_out = run_fpocket(pdb_path, work_dir)
    pockets = read_fpocket_pockets(fp_out)

    if not return_results:
        console.rule("filter & deduplicate")
    pockets_filtered = deduplicate_pockets(pockets)

    if not return_results:
        console.rule("P2Rank rescoring")
    rescored = rescore_with_p2rank(pockets_filtered, Path(pdb_path), work_dir, prank_home)

    if not return_results:
        console.rule("final ranking")
    rescored_sorted = sorted(rescored, key=lambda x: x.score, reverse=True)[:topk]
    
    # 执行断崖分析
    cliff_analysis_result = None
    if enable_cliff_analysis and rescored:
        if not return_results:
            console.rule("断崖分析")
        
        protein_id = Path(pdb_path).stem
        cliff_analysis_result = analyze_cliff_pattern(rescored, protein_id)
        
        if not return_results:
            console.print(f"高置信度口袋数量: {cliff_analysis_result.high_confidence_count}")
            console.print(f"最大分数差: {cliff_analysis_result.max_delta:.4f}")
            console.print(f"是否为Top1主导: {cliff_analysis_result.is_top1_dominant}")
    
    if not return_results:
        for i, p in enumerate(rescored_sorted, start=1):
            console.print(f"Top {i}: score={p.score:.4f} center=({p.center_x:.2f},{p.center_y:.2f},{p.center_z:.2f})")
    
    if return_results:
        return PipelineResult(
            top_pockets=rescored_sorted,
            num_pockets_detected=len(pockets),
            num_pockets_filtered=len(pockets_filtered),
            all_pockets=pockets,
            filtered_pockets=pockets_filtered,
            cliff_analysis=cliff_analysis_result
        )


