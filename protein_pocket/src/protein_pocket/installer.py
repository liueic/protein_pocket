"""
自动安装和配置 P2Rank 的工具模块
"""
import os
import subprocess
import shutil
import tarfile
import urllib.request
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

console = Console()

P2RANK_VERSION = "2.5.1"
P2RANK_URL = f"https://github.com/rdk/p2rank/releases/download/{P2RANK_VERSION}/p2rank_{P2RANK_VERSION}.tar.gz"
P2RANK_DIR_NAME = f"p2rank_{P2RANK_VERSION}"


def check_p2rank_installed(prank_home: Optional[str] = None) -> bool:
    """检查 P2Rank 是否已安装"""
    if prank_home:
        prank_path = Path(prank_home) / "prank"
        return prank_path.exists() and prank_path.is_file()
    
    # 检查环境变量
    if "P2RANK_HOME" in os.environ:
        prank_path = Path(os.environ["P2RANK_HOME"]) / "prank"
        return prank_path.exists() and prank_path.is_file()
    
    # 检查当前目录
    current_dir = Path.cwd()
    prank_path = current_dir / P2RANK_DIR_NAME / "prank"
    if prank_path.exists():
        return True
    
    # 检查 PATH 中是否有 prank 命令
    try:
        subprocess.run(["prank", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def download_p2rank(download_dir: Path) -> Path:
    """下载 P2Rank"""
    console.print(f"[blue]正在下载 P2Rank {P2RANK_VERSION}...[/blue]")
    
    tar_file = download_dir / f"p2rank_{P2RANK_VERSION}.tar.gz"
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("下载中...", total=None)
        
        def show_progress(block_num, block_size, total_size):
            if total_size > 0:
                downloaded = block_num * block_size
                progress.update(task, completed=downloaded, total=total_size)
        
        urllib.request.urlretrieve(P2RANK_URL, tar_file, reporthook=show_progress)
    
    console.print(f"[green]✓ 下载完成: {tar_file}[/green]")
    return tar_file


def extract_p2rank(tar_file: Path, extract_dir: Path) -> Path:
    """解压 P2Rank"""
    console.print(f"[blue]正在解压 P2Rank...[/blue]")
    
    with tarfile.open(tar_file, "r:gz") as tar:
        tar.extractall(extract_dir)
    
    p2rank_dir = extract_dir / P2RANK_DIR_NAME
    if not p2rank_dir.exists():
        raise FileNotFoundError(f"解压后未找到 P2Rank 目录: {p2rank_dir}")
    
    console.print(f"[green]✓ 解压完成: {p2rank_dir}[/green]")
    return p2rank_dir


def make_prank_executable(p2rank_dir: Path) -> None:
    """使 prank 脚本可执行"""
    prank_script = p2rank_dir / "prank"
    if prank_script.exists():
        os.chmod(prank_script, 0o755)
        console.print(f"[green]✓ 设置 prank 脚本可执行权限[/green]")


def test_p2rank_installation(p2rank_dir: Path) -> bool:
    """测试 P2Rank 安装是否成功"""
    console.print("[blue]正在测试 P2Rank 安装...[/blue]")
    
    prank_script = p2rank_dir / "prank"
    if not prank_script.exists():
        console.print("[red]✗ prank 脚本不存在[/red]")
        return False
    
    try:
        # 设置环境变量并测试
        env = os.environ.copy()
        env["P2RANK_HOME"] = str(p2rank_dir)
        
        result = subprocess.run(
            [str(prank_script), "--version"],
            capture_output=True,
            text=True,
            env=env,
            timeout=30
        )
        
        if result.returncode == 0:
            console.print(f"[green]✓ P2Rank 安装成功! 版本信息:[/green]")
            console.print(f"[dim]{result.stdout.strip()}[/dim]")
            return True
        else:
            console.print(f"[red]✗ P2Rank 测试失败: {result.stderr}[/red]")
            return False
            
    except subprocess.TimeoutExpired:
        console.print("[red]✗ P2Rank 测试超时[/red]")
        return False
    except Exception as e:
        console.print(f"[red]✗ P2Rank 测试出错: {e}[/red]")
        return False


def install_p2rank(install_dir: Optional[Path] = None) -> Path:
    """自动安装 P2Rank"""
    if install_dir is None:
        install_dir = Path.cwd()
    
    console.print(f"[yellow]开始自动安装 P2Rank {P2RANK_VERSION}...[/yellow]")
    
    # 检查是否已安装
    if check_p2rank_installed():
        console.print("[green]✓ P2Rank 已安装，跳过下载[/green]")
        # 返回已安装的路径
        if "P2RANK_HOME" in os.environ:
            return Path(os.environ["P2RANK_HOME"])
        else:
            return Path.cwd() / P2RANK_DIR_NAME
    
    # 创建安装目录
    install_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 下载
        tar_file = download_p2rank(install_dir)
        
        # 解压
        p2rank_dir = extract_p2rank(tar_file, install_dir)
        
        # 设置权限
        make_prank_executable(p2rank_dir)
        
        # 测试安装
        if test_p2rank_installation(p2rank_dir):
            console.print(f"[green]🎉 P2Rank {P2RANK_VERSION} 安装成功![/green]")
            console.print(f"[dim]安装路径: {p2rank_dir}[/dim]")
            
            # 清理下载的压缩包
            tar_file.unlink()
            console.print("[dim]已清理下载文件[/dim]")
            
            return p2rank_dir
        else:
            raise RuntimeError("P2Rank 安装测试失败")
            
    except Exception as e:
        console.print(f"[red]✗ P2Rank 安装失败: {e}[/red]")
        raise


def get_p2rank_home() -> Optional[Path]:
    """获取 P2Rank 安装路径"""
    # 检查环境变量
    if "P2RANK_HOME" in os.environ:
        p2rank_home = Path(os.environ["P2RANK_HOME"])
        if p2rank_home.exists():
            return p2rank_home
    
    # 检查当前目录
    current_dir = Path.cwd()
    p2rank_dir = current_dir / P2RANK_DIR_NAME
    if p2rank_dir.exists():
        return p2rank_dir
    
    # 检查父目录
    parent_dir = current_dir.parent
    p2rank_dir = parent_dir / P2RANK_DIR_NAME
    if p2rank_dir.exists():
        return p2rank_dir
    
    return None


def ensure_p2rank_installed(prank_home: Optional[str] = None) -> Path:
    """确保 P2Rank 已安装，如果没有则自动安装"""
    if prank_home:
        prank_path = Path(prank_home)
        if prank_path.exists() and (prank_path / "prank").exists():
            return prank_path
    
    # 检查是否已安装
    existing_p2rank = get_p2rank_home()
    if existing_p2rank and check_p2rank_installed(str(existing_p2rank)):
        console.print(f"[green]✓ 找到已安装的 P2Rank: {existing_p2rank}[/green]")
        return existing_p2rank
    
    # 自动安装
    console.print("[yellow]未找到 P2Rank，开始自动安装...[/yellow]")
    return install_p2rank()
