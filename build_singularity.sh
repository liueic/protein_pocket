#!/bin/bash

# 蛋白口袋检测Pipeline Singularity容器构建脚本
# 使用方法: bash build_singularity.sh

set -e  # 遇到错误立即退出

echo "🔧 开始构建蛋白口袋检测Pipeline Singularity容器"
echo "=================================================="

# 检查Singularity是否安装
if ! command -v singularity &> /dev/null; then
    echo "❌ 错误: 未找到Singularity，请先安装Singularity"
    echo "安装指南: https://sylabs.io/guides/3.0/user-guide/installation.html"
    exit 1
fi

echo "✅ 找到Singularity: $(singularity --version)"

# 检查定义文件是否存在
if [ ! -f "Singularity.def" ]; then
    echo "❌ 错误: 未找到Singularity.def文件"
    exit 1
fi

# 设置容器名称和标签
CONTAINER_NAME="protein_pocket"
VERSION="1.0"
IMAGE_NAME="${CONTAINER_NAME}_${VERSION}.sif"

echo "📦 容器名称: ${IMAGE_NAME}"

# 检查是否已存在同名容器
if [ -f "${IMAGE_NAME}" ]; then
    echo "⚠️  警告: 容器文件 ${IMAGE_NAME} 已存在"
    read -p "是否覆盖? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 构建取消"
        exit 1
    fi
    rm -f "${IMAGE_NAME}"
fi

# 开始构建
echo "🚀 开始构建容器..."
echo "这可能需要几分钟时间，请耐心等待..."

# 构建容器
singularity build --fakeroot "${IMAGE_NAME}" Singularity.def

# 检查构建是否成功
if [ $? -eq 0 ] && [ -f "${IMAGE_NAME}" ]; then
    echo ""
    echo "🎉 容器构建成功!"
    echo "📁 容器文件: ${IMAGE_NAME}"
    echo "📊 文件大小: $(du -h ${IMAGE_NAME} | cut -f1)"
    echo ""
    echo "🧪 测试容器..."
    
    # 测试容器
    echo "测试protein-pocket命令..."
    singularity run "${IMAGE_NAME}" --help
    
    if [ $? -eq 0 ]; then
        echo "✅ 容器测试通过!"
        echo ""
        echo "📖 使用方法:"
        echo "  # 单文件处理"
        echo "  singularity run ${IMAGE_NAME} run /path/to/protein.pdb --workdir /output"
        echo ""
        echo "  # 批量处理"
        echo "  singularity run ${IMAGE_NAME} batch /path/to/proteins/ --results-dir /output"
        echo ""
        echo "  # 挂载数据目录"
        echo "  singularity run -B /your/data:/data -B /your/output:/output ${IMAGE_NAME} batch /data --results-dir /output"
    else
        echo "❌ 容器测试失败"
        exit 1
    fi
else
    echo "❌ 容器构建失败"
    exit 1
fi
