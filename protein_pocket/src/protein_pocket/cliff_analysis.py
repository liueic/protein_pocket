"""
断崖算法分析模块

该模块实现了基于P2Rank分数的"断崖算法"，用于识别高置信度的口袋候选集。
算法通过分析相邻分数之间的差值来找到显著的"断崖"，从而确定高置信度口袋集合。
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
from .p2rank import ScoredPocket


@dataclass
class CliffAnalysisResult:
    """断崖分析结果"""
    protein_id: str
    top1_pocket_id: str
    top1_score: float
    high_confidence_count: int
    high_confidence_set: List[str]
    is_top1_dominant: bool
    max_delta: float
    cliff_index: int
    all_scores: List[float]
    deltas: List[float]


def analyze_cliff_pattern(scored_pockets: List[ScoredPocket], protein_id: str) -> CliffAnalysisResult:
    """
    对P2Rank重打分后的口袋进行断崖分析
    
    Args:
        scored_pockets: 按分数降序排列的ScoredPocket列表
        protein_id: 蛋白质ID
        
    Returns:
        CliffAnalysisResult: 断崖分析结果
    """
    if not scored_pockets:
        raise ValueError("口袋列表不能为空")
    
    # 确保口袋按分数降序排列
    sorted_pockets = sorted(scored_pockets, key=lambda x: x.score, reverse=True)
    
    # 获取分数列表
    scores = [pocket.score for pocket in sorted_pockets]
    
    # 计算分数差（Deltas）
    deltas = []
    for i in range(len(scores) - 1):
        delta = scores[i] - scores[i + 1]
        deltas.append(delta)
    
    # 寻找最大差值（Find the Cliff）
    if not deltas:
        # 只有一个口袋的情况
        max_delta = 0.0
        cliff_index = 0
    else:
        max_delta = max(deltas)
        cliff_index = deltas.index(max_delta)
    
    # 定义"断崖之上"的口袋集
    high_confidence_count = cliff_index + 1
    high_confidence_set = []
    
    # 为口袋生成ID（基于坐标）
    for i in range(high_confidence_count):
        pocket = sorted_pockets[i]
        pocket_id = f"Pocket_{i+1}_{pocket.center_x:.1f}_{pocket.center_y:.1f}_{pocket.center_z:.1f}"
        high_confidence_set.append(pocket_id)
    
    # 获取Top1口袋信息
    top1_pocket = sorted_pockets[0]
    top1_pocket_id = high_confidence_set[0]
    top1_score = top1_pocket.score
    
    # 判断是否为Top1主导（只有一个高置信度口袋）
    is_top1_dominant = (high_confidence_count == 1)
    
    return CliffAnalysisResult(
        protein_id=protein_id,
        top1_pocket_id=top1_pocket_id,
        top1_score=top1_score,
        high_confidence_count=high_confidence_count,
        high_confidence_set=high_confidence_set,
        is_top1_dominant=is_top1_dominant,
        max_delta=max_delta,
        cliff_index=cliff_index,
        all_scores=scores,
        deltas=deltas
    )


def format_cliff_analysis_result(result: CliffAnalysisResult) -> str:
    """
    格式化断崖分析结果为可读字符串
    
    Args:
        result: 断崖分析结果
        
    Returns:
        str: 格式化的结果字符串
    """
    output = []
    output.append(f"=== 断崖分析结果: {result.protein_id} ===")
    output.append(f"Top1口袋ID: {result.top1_pocket_id}")
    output.append(f"Top1分数: {result.top1_score:.4f}")
    output.append(f"高置信度口袋数量: {result.high_confidence_count}")
    output.append(f"高置信度口袋集合: {result.high_confidence_set}")
    output.append(f"是否为Top1主导: {result.is_top1_dominant}")
    output.append(f"最大分数差: {result.max_delta:.4f}")
    output.append(f"断崖位置索引: {result.cliff_index}")
    
    if len(result.all_scores) > 1:
        output.append(f"分数序列: {[f'{s:.4f}' for s in result.all_scores[:5]]}{'...' if len(result.all_scores) > 5 else ''}")
        output.append(f"分数差值: {[f'{d:.4f}' for d in result.deltas[:4]]}{'...' if len(result.deltas) > 4 else ''}")
    
    return "\n".join(output)


def get_cliff_summary_stats(results: List[CliffAnalysisResult]) -> dict:
    """
    获取多个断崖分析结果的统计摘要
    
    Args:
        results: 断崖分析结果列表
        
    Returns:
        dict: 统计摘要
    """
    if not results:
        return {}
    
    total_proteins = len(results)
    top1_dominant_count = sum(1 for r in results if r.is_top1_dominant)
    avg_high_confidence_count = sum(r.high_confidence_count for r in results) / total_proteins
    avg_max_delta = sum(r.max_delta for r in results) / total_proteins
    
    high_confidence_distribution = {}
    for result in results:
        count = result.high_confidence_count
        high_confidence_distribution[count] = high_confidence_distribution.get(count, 0) + 1
    
    return {
        "total_proteins": total_proteins,
        "top1_dominant_count": top1_dominant_count,
        "top1_dominant_percentage": (top1_dominant_count / total_proteins) * 100,
        "avg_high_confidence_count": avg_high_confidence_count,
        "avg_max_delta": avg_max_delta,
        "high_confidence_distribution": high_confidence_distribution
    }
