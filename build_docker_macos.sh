#!/bin/bash

# 蛋白口袋检测Pipeline Docker容器构建脚本 (macOS版本)
# 使用方法: bash build_docker_macos.sh

set -e  # 遇到错误立即退出

echo "🐳 开始构建蛋白口袋检测Pipeline Docker容器 (macOS版本)"
echo "========================================================"

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: 未找到Docker，请先安装Docker Desktop"
    echo "安装方法:"
    echo "1. 使用Homebrew: brew install --cask docker"
    echo "2. 或从官网下载: https://www.docker.com/products/docker-desktop/"
    exit 1
fi

echo "✅ 找到Docker: $(docker --version)"

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ 错误: Docker未运行，请启动Docker Desktop"
    echo "启动方法: 打开Docker Desktop应用程序"
    exit 1
fi

echo "✅ Docker正在运行"

# 检查Dockerfile是否存在
if [ ! -f "Dockerfile" ]; then
    echo "❌ 错误: 未找到Dockerfile文件"
    exit 1
fi

# 设置镜像名称和标签
IMAGE_NAME="protein_pocket"
VERSION="1.0"
FULL_IMAGE_NAME="${IMAGE_NAME}:${VERSION}"

echo "📦 镜像名称: ${FULL_IMAGE_NAME}"

# 检查是否已存在同名镜像
if docker image inspect "${FULL_IMAGE_NAME}" > /dev/null 2>&1; then
    echo "⚠️  警告: 镜像 ${FULL_IMAGE_NAME} 已存在"
    read -p "是否重新构建? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 构建取消"
        exit 1
    fi
    echo "🗑️  删除旧镜像..."
    docker rmi "${FULL_IMAGE_NAME}" || true
fi

# 开始构建
echo "🚀 开始构建Docker镜像..."
echo "这可能需要几分钟时间，请耐心等待..."

# 构建镜像
docker build -t "${FULL_IMAGE_NAME}" .

# 检查构建是否成功
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Docker镜像构建成功!"
    echo "📁 镜像名称: ${FULL_IMAGE_NAME}"
    echo "📊 镜像大小: $(docker images --format "table {{.Size}}" ${FULL_IMAGE_NAME} | tail -1)"
    echo ""
    echo "🧪 测试镜像..."
    
    # 测试镜像
    echo "测试protein-pocket命令..."
    if docker run --rm "${FULL_IMAGE_NAME}" --help > /dev/null 2>&1; then
        echo "✅ 镜像测试通过!"
        echo ""
        echo "📖 使用方法:"
        echo "  # 单文件处理"
        echo "  docker run --rm -v \$(pwd)/data:/data -v \$(pwd)/output:/output \\"
        echo "    ${FULL_IMAGE_NAME} run /data/protein.pdb --workdir /output"
        echo ""
        echo "  # 批量处理"
        echo "  docker run --rm -v \$(pwd)/data:/data -v \$(pwd)/output:/output \\"
        echo "    ${FULL_IMAGE_NAME} batch /data --results-dir /output"
        echo ""
        echo "  # 使用便捷脚本"
        echo "  ./run_docker_macos.sh run /data/protein.pdb --workdir /output"
        echo "  ./run_docker_macos.sh batch /data --results-dir /output"
    else
        echo "❌ 镜像测试失败"
        exit 1
    fi
else
    echo "❌ Docker镜像构建失败"
    exit 1
fi
