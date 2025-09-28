"""
批量处理模块 - 处理多个蛋白质结构文件
"""

import csv
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.table import Table

from .pipeline import run_pipeline
from .fpocket import Pocket

console = Console()


@dataclass
class BatchResult:
    """批量处理结果"""
    protein_name: str
    protein_path: str
    status: str  # "success", "failed", "skipped"
    error_message: Optional[str] = None
    num_pockets_detected: int = 0
    num_pockets_filtered: int = 0
    top_pockets: List[Dict[str, Any]] = None
    processing_time: float = 0.0
    # 断崖分析结果
    high_confidence_count: int = 0
    is_top1_dominant: bool = False
    max_delta: float = 0.0
    cliff_index: int = 0
    
    def __post_init__(self):
        if self.top_pockets is None:
            self.top_pockets = []


def find_protein_files(input_dir: str, extensions: List[str]) -> List[Path]:
    """在指定目录中查找蛋白质结构文件（递归查找，保持目录结构）"""
    input_path = Path(input_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"输入目录不存在: {input_dir}")
    
    if not input_path.is_dir():
        raise ValueError(f"输入路径不是目录: {input_dir}")
    
    protein_files = []
    for ext in extensions:
        ext = ext.strip().lower()
        if not ext.startswith('.'):
            ext = f'.{ext}'
        
        # 递归查找所有匹配的文件，保持目录结构
        files = list(input_path.rglob(f"*{ext}"))
        protein_files.extend(files)
    
    # 去重并排序
    protein_files = sorted(list(set(protein_files)))
    
    console.print(f"找到 {len(protein_files)} 个蛋白质文件")
    return protein_files


def process_single_protein_worker(args) -> BatchResult:
    """并行处理单个蛋白质文件的工作函数"""
    protein_path, input_dir, results_dir, topk, prank_home = args
    return process_single_protein(protein_path, input_dir, results_dir, topk, prank_home, None, None)


def process_single_protein(
    protein_path: Path, 
    input_dir: Path,
    results_dir: Path,
    topk: int, 
    prank_home: Optional[str],
    progress: Optional[Progress] = None,
    task_id: Optional[int] = None
) -> BatchResult:
    """处理单个蛋白质文件"""
    start_time = time.time()
    protein_name = protein_path.stem
    
    try:
        # 更新进度条（如果提供）
        if progress and task_id is not None:
            progress.update(task_id, description=f"处理 {protein_name}")
        
        # 计算相对于输入目录的路径，保持目录结构
        relative_path = protein_path.relative_to(input_dir)
        # 移除文件扩展名，作为结果目录名
        result_subdir = results_dir / relative_path.parent / protein_name
        
        # 创建结果目录
        result_subdir.mkdir(parents=True, exist_ok=True)
        
        # 运行 pipeline，使用结果目录作为工作目录
        from .pipeline import run_pipeline
        result = run_pipeline(
            pdb_path=str(protein_path),
            workdir=str(result_subdir),
            topk=topk,
            prank_home=prank_home,
            return_results=True,  # 我们需要返回结果而不是直接打印
            enable_cliff_analysis=True  # 启用断崖分析
        )
        
        processing_time = time.time() - start_time
        
        # 提取结果信息
        top_pockets = []
        cliff_analysis = None
        if result and hasattr(result, 'top_pockets'):
            for i, pocket in enumerate(result.top_pockets):
                top_pockets.append({
                    'rank': i + 1,
                    'score': pocket.score,
                    'center_x': pocket.center_x,
                    'center_y': pocket.center_y,
                    'center_z': pocket.center_z,
                    'raw_score': pocket.raw_score
                })
            
            # 提取断崖分析结果
            if hasattr(result, 'cliff_analysis') and result.cliff_analysis:
                cliff_analysis = result.cliff_analysis
            
            # 为每个蛋白质生成详细的CSV文件
            save_protein_detailed_results(protein_name, result, result_subdir)
        
        return BatchResult(
            protein_name=protein_name,
            protein_path=str(protein_path),
            status="success",
            num_pockets_detected=getattr(result, 'num_pockets_detected', 0),
            num_pockets_filtered=getattr(result, 'num_pockets_filtered', 0),
            top_pockets=top_pockets,
            processing_time=processing_time,
            # 断崖分析结果
            high_confidence_count=getattr(cliff_analysis, 'high_confidence_count', 0) if cliff_analysis else 0,
            is_top1_dominant=getattr(cliff_analysis, 'is_top1_dominant', False) if cliff_analysis else False,
            max_delta=getattr(cliff_analysis, 'max_delta', 0.0) if cliff_analysis else 0.0,
            cliff_index=getattr(cliff_analysis, 'cliff_index', 0) if cliff_analysis else 0
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = str(e)
        console.print(f"[red]处理 {protein_name} 时出错: {error_msg}[/red]")
        
        return BatchResult(
            protein_name=protein_name,
            protein_path=str(protein_path),
            status="failed",
            error_message=error_msg,
            processing_time=processing_time
        )


def save_protein_detailed_results(protein_name: str, result, result_dir: Path) -> None:
    """为单个蛋白质保存详细的CSV结果文件"""
    if not result or not hasattr(result, 'top_pockets'):
        return
    
    # 创建详细的CSV文件
    detailed_csv = result_dir / f"{protein_name}_pocket_results.csv"
    
    with open(detailed_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # 写入表头
        writer.writerow([
            'pocket_name', 'rank', 'score', 'center_x', 'center_y', 'center_z', 
            'raw_score', 'fpocket_rank', 'rank_change', 'is_high_confidence'
        ])
        
        # 获取断崖分析结果
        cliff_analysis = getattr(result, 'cliff_analysis', None)
        high_confidence_indices = set()
        if cliff_analysis:
            high_confidence_indices = set(range(cliff_analysis.high_confidence_count))
        
        # 获取过滤后的口袋，按原始分数排序（用于计算fpocket排名）
        filtered_pockets = getattr(result, 'filtered_pockets', [])
        if filtered_pockets:
            # 按原始分数排序，获取fpocket排名
            fpocket_sorted = sorted(filtered_pockets, key=lambda x: x.raw_score, reverse=True)
            fpocket_rank_map = {id(pocket): i + 1 for i, pocket in enumerate(fpocket_sorted)}
        else:
            fpocket_rank_map = {}
        
        # 写入每个口袋的详细信息
        for i, pocket in enumerate(result.top_pockets):
            # 获取fpocket原始排名
            pocket_id = id(pocket)
            fpocket_rank = fpocket_rank_map.get(pocket_id, i + 1)
            rank_change = fpocket_rank - (i + 1)  # 正数表示排名上升，负数表示排名下降
            
            # 生成口袋名称
            pocket_name = f"pocket.{i + 1}"
            
            # 判断是否为高置信度口袋
            is_high_confidence = i in high_confidence_indices
            
            writer.writerow([
                pocket_name,
                i + 1,  # 最终排名
                f"{pocket.score:.4f}",
                f"{pocket.center_x:.3f}",
                f"{pocket.center_y:.3f}",
                f"{pocket.center_z:.3f}",
                f"{pocket.raw_score:.4f}",
                fpocket_rank,
                f"{rank_change:+d}" if rank_change != 0 else "0",
                is_high_confidence
            ])
    
    # 如果存在断崖分析结果，在文件末尾添加分析摘要
    if cliff_analysis:
        with open(detailed_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # 添加空行分隔
            writer.writerow([])
            writer.writerow([])
            # 添加断崖分析摘要
            writer.writerow(['=== 断崖分析摘要 ==='])
            writer.writerow(['项目', '值'])
            writer.writerow(['高置信度口袋数量', cliff_analysis.high_confidence_count])
            writer.writerow(['是否为Top1主导', cliff_analysis.is_top1_dominant])
            writer.writerow(['最大分数差', f"{cliff_analysis.max_delta:.4f}"])
            writer.writerow(['断崖位置索引', cliff_analysis.cliff_index])
            writer.writerow(['Top1口袋分数', f"{cliff_analysis.top1_score:.4f}"])
            writer.writerow(['高置信度口袋集合', ', '.join(cliff_analysis.high_confidence_set)])
    
    console.print(f"✓ {protein_name} 详细结果已保存到: {detailed_csv}")


def save_batch_results(results: List[BatchResult], output_csv: str) -> None:
    """保存批量处理结果到CSV文件"""
    output_path = Path(output_csv)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # 写入表头
        writer.writerow([
            'protein_name', 'protein_path', 'status', 'error_message',
            'num_pockets_detected', 'num_pockets_filtered', 'processing_time',
            'top_pocket_1_score', 'top_pocket_1_center_x', 'top_pocket_1_center_y', 'top_pocket_1_center_z',
            'top_pocket_2_score', 'top_pocket_2_center_x', 'top_pocket_2_center_y', 'top_pocket_2_center_z',
            'top_pocket_3_score', 'top_pocket_3_center_x', 'top_pocket_3_center_y', 'top_pocket_3_center_z',
            # 断崖分析结果
            'high_confidence_count', 'is_top1_dominant', 'max_delta', 'cliff_index'
        ])
        
        # 写入数据
        for result in results:
            row = [
                result.protein_name,
                result.protein_path,
                result.status,
                result.error_message or '',
                result.num_pockets_detected,
                result.num_pockets_filtered,
                f"{result.processing_time:.2f}",
            ]
            
            # 添加前3个口袋的信息
            for i in range(3):
                if i < len(result.top_pockets):
                    pocket = result.top_pockets[i]
                    row.extend([
                        f"{pocket['score']:.4f}",
                        f"{pocket['center_x']:.3f}",
                        f"{pocket['center_y']:.3f}",
                        f"{pocket['center_z']:.3f}",
                    ])
                else:
                    row.extend(['', '', '', ''])
            
            # 添加断崖分析结果
            row.extend([
                result.high_confidence_count,
                result.is_top1_dominant,
                f"{result.max_delta:.4f}",
                result.cliff_index
            ])
            
            writer.writerow(row)
    
    console.print(f"✓ 批量处理结果已保存到: {output_path}")


def print_batch_summary(results: List[BatchResult]) -> None:
    """打印批量处理摘要"""
    total_files = len(results)
    successful = sum(1 for r in results if r.status == "success")
    failed = sum(1 for r in results if r.status == "failed")
    total_time = sum(r.processing_time for r in results)
    
    # 创建摘要表格
    table = Table(title="批量处理摘要")
    table.add_column("统计项", style="cyan")
    table.add_column("数值", style="magenta")
    
    table.add_row("总文件数", str(total_files))
    table.add_row("成功处理", str(successful))
    table.add_row("处理失败", str(failed))
    table.add_row("成功率", f"{(successful/total_files*100):.1f}%" if total_files > 0 else "0%")
    table.add_row("总处理时间", f"{total_time:.1f} 秒")
    table.add_row("平均处理时间", f"{total_time/total_files:.1f} 秒" if total_files > 0 else "0 秒")
    
    console.print(table)
    
    # 断崖分析统计
    if successful > 0:
        successful_results = [r for r in results if r.status == "success"]
        top1_dominant_count = sum(1 for r in successful_results if r.is_top1_dominant)
        avg_high_confidence = sum(r.high_confidence_count for r in successful_results) / len(successful_results)
        avg_max_delta = sum(r.max_delta for r in successful_results) / len(successful_results)
        
        cliff_table = Table(title="断崖分析统计")
        cliff_table.add_column("统计项", style="cyan")
        cliff_table.add_column("数值", style="magenta")
        
        cliff_table.add_row("Top1主导蛋白数", str(top1_dominant_count))
        cliff_table.add_row("Top1主导比例", f"{(top1_dominant_count/len(successful_results)*100):.1f}%")
        cliff_table.add_row("平均高置信度口袋数", f"{avg_high_confidence:.1f}")
        cliff_table.add_row("平均最大分数差", f"{avg_max_delta:.4f}")
        
        console.print(cliff_table)
    
    # 显示失败的文件
    if failed > 0:
        console.print("\n[red]处理失败的文件:[/red]")
        for result in results:
            if result.status == "failed":
                console.print(f"  - {result.protein_name}: {result.error_message}")


def run_batch_pipeline(
    input_dir: str,
    results_dir: str = "results",
    topk: int = 5,
    prank_home: Optional[str] = None,
    output_csv: str = "batch_results.csv",
    file_extensions: str = "pdb,cif",
    max_workers: Optional[int] = None,
) -> None:
    """运行批量处理 pipeline"""
    
    console.print(f"[bold blue]开始批量处理蛋白质口袋检测[/bold blue]")
    console.print(f"输入目录: {input_dir}")
    console.print(f"结果目录: {results_dir}")
    console.print(f"输出CSV: {output_csv}")
    console.print(f"文件扩展名: {file_extensions}")
    
    # 解析文件扩展名
    extensions = [ext.strip() for ext in file_extensions.split(',')]
    
    # 查找蛋白质文件
    try:
        protein_files = find_protein_files(input_dir, extensions)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]错误: {e}[/red]")
        return
    
    if not protein_files:
        console.print("[yellow]未找到任何蛋白质文件[/yellow]")
        return
    
    # 创建结果目录
    input_path = Path(input_dir)
    results_path = Path(results_dir)
    results_path.mkdir(parents=True, exist_ok=True)
    
    # 预先检查P2Rank安装（只检查一次）
    console.print("🔍 检查P2Rank安装...")
    from .installer import ensure_p2rank_installed
    try:
        p2rank_path = ensure_p2rank_installed(prank_home)
        console.print(f"✅ P2Rank已就绪: {p2rank_path}")
    except Exception as e:
        console.print(f"[red]❌ P2Rank检查失败: {e}[/red]")
        return
    
    # 确定并行工作进程数
    if max_workers is None:
        max_workers = min(mp.cpu_count(), 8)  # 最多使用8个进程，避免过度并行
    
    console.print(f"使用 {max_workers} 个并行进程处理")
    
    # 准备并行处理参数（使用预先检查的P2Rank路径）
    process_args = [
        (protein_path, input_path, results_path, topk, str(p2rank_path))
        for protein_path in protein_files
    ]
    
    # 批量处理
    results = []
    
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        "•",
        TimeElapsedColumn(),
        "•",
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        
        task_id = progress.add_task("批量处理中...", total=len(protein_files))
        
        # 使用进程池并行处理
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_protein = {
                executor.submit(process_single_protein_worker, args): args[0]
                for args in process_args
            }
            
            # 收集结果
            for future in as_completed(future_to_protein):
                protein_path = future_to_protein[future]
                try:
                    result = future.result()
                    results.append(result)
                    progress.advance(task_id)
                    
                    # 更新进度条描述
                    if result.status == "success":
                        progress.update(task_id, description=f"完成 {result.protein_name}")
                    else:
                        progress.update(task_id, description=f"失败 {result.protein_name}")
                        
                except Exception as e:
                    # 处理异常情况
                    protein_name = protein_path.stem
                    error_result = BatchResult(
                        protein_name=protein_name,
                        protein_path=str(protein_path),
                        status="failed",
                        error_message=str(e),
                        processing_time=0.0
                    )
                    results.append(error_result)
                    progress.advance(task_id)
                    progress.update(task_id, description=f"异常 {protein_name}")
    
    # 保存结果
    save_batch_results(results, output_csv)
    
    # 打印摘要
    print_batch_summary(results)
    
    console.print(f"\n[bold green]批量处理完成![/bold green]")
    console.print(f"详细结果请查看: {output_csv}")
    console.print(f"每个蛋白质的详细结果保存在: {results_dir}/")
