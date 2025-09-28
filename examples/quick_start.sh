#!/bin/bash

# 蛋白口袋检测Pipeline快速开始脚本
# 使用方法: bash quick_start.sh

echo "🚀 蛋白口袋检测Pipeline快速开始"
echo "=================================="

# 检查conda环境
if ! command -v conda &> /dev/null; then
    echo "❌ 错误: 未找到conda，请先安装Anaconda或Miniconda"
    exit 1
fi

# 激活环境
echo "📦 激活conda环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate protein-pocket

if [ $? -ne 0 ]; then
    echo "❌ 错误: 无法激活protein-pocket环境，请先创建环境"
    echo "运行: conda env create -f environment.yml"
    exit 1
fi

echo "✅ 环境激活成功"

# 检查是否有示例文件
if [ ! -d "protein" ] || [ -z "$(ls -A protein/ 2>/dev/null)" ]; then
    echo "⚠️  警告: protein目录为空或不存在"
    echo "请将您的蛋白质文件（.pdb或.cif格式）放入protein/目录"
    echo "或者使用以下命令处理其他目录："
    echo "protein-pocket batch <您的目录路径>"
    exit 1
fi

echo "📁 找到蛋白质文件，开始处理..."

# 运行批量处理
echo "🔬 开始批量处理..."
protein-pocket batch protein/ --results-dir results --topk 3 --output-csv batch_results.csv

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 处理完成！"
    echo "📊 结果文件: batch_results.csv"
    echo "📁 详细输出: results/"
    echo ""
    echo "查看结果:"
    echo "cat batch_results.csv"
    echo ""
    echo "查看每个蛋白质的详细结果:"
    echo "ls -la results/"
else
    echo "❌ 处理失败，请检查错误信息"
    exit 1
fi
