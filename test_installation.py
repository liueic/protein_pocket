#!/usr/bin/env python3
"""
蛋白口袋检测Pipeline安装测试脚本
用于验证所有依赖是否正确安装
"""

import sys
import subprocess
from pathlib import Path

def test_conda_environment():
    """测试conda环境"""
    print("🔍 测试conda环境...")
    try:
        result = subprocess.run(['conda', 'info', '--envs'], 
                              capture_output=True, text=True, check=True)
        if 'protein-pocket' in result.stdout:
            print("✅ protein-pocket环境存在")
            return True
        else:
            print("❌ protein-pocket环境不存在")
            return False
    except subprocess.CalledProcessError:
        print("❌ conda命令执行失败")
        return False

def test_python_package():
    """测试Python包安装"""
    print("🔍 测试Python包安装...")
    try:
        import protein_pocket
        print("✅ protein_pocket包导入成功")
        return True
    except ImportError as e:
        print(f"❌ protein_pocket包导入失败: {e}")
        return False

def test_cli_command():
    """测试CLI命令"""
    print("🔍 测试CLI命令...")
    try:
        result = subprocess.run(['protein-pocket', '--help'], 
                              capture_output=True, text=True, check=True)
        if 'protein-pocket' in result.stdout:
            print("✅ CLI命令可用")
            return True
        else:
            print("❌ CLI命令不可用")
            return False
    except subprocess.CalledProcessError:
        print("❌ CLI命令执行失败")
        return False

def test_fpocket():
    """测试fpocket"""
    print("🔍 测试fpocket...")
    try:
        result = subprocess.run(['fpocket', '--help'], 
                              capture_output=True, text=True, check=True)
        if 'fpocket' in result.stdout:
            print("✅ fpocket可用")
            return True
        else:
            print("❌ fpocket不可用")
            return False
    except subprocess.CalledProcessError:
        print("❌ fpocket执行失败")
        return False

def test_java():
    """测试Java"""
    print("🔍 测试Java...")
    try:
        result = subprocess.run(['java', '-version'], 
                              capture_output=True, text=True, check=True)
        if 'version' in result.stderr.lower():
            print("✅ Java可用")
            return True
        else:
            print("❌ Java不可用")
            return False
    except subprocess.CalledProcessError:
        print("❌ Java执行失败")
        return False

def main():
    """主测试函数"""
    print("🚀 蛋白口袋检测Pipeline安装测试")
    print("=" * 50)
    
    tests = [
        test_conda_environment,
        test_python_package,
        test_cli_command,
        test_fpocket,
        test_java,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！Pipeline已正确安装。")
        print("\n📖 下一步:")
        print("1. 将蛋白质文件放入protein/目录")
        print("2. 运行: bash examples/quick_start.sh")
        print("3. 或手动运行: protein-pocket batch protein/")
        return 0
    else:
        print("❌ 部分测试失败，请检查安装。")
        print("\n🔧 故障排除:")
        print("1. 确保已激活conda环境: conda activate protein-pocket")
        print("2. 重新安装Python包: pip install -e .")
        print("3. 检查environment.yml中的依赖")
        return 1

if __name__ == "__main__":
    sys.exit(main())
