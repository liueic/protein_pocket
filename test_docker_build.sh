#!/bin/bash

# Docker构建测试脚本
# 使用方法: bash test_docker_build.sh

set -e

echo "🐳 测试Docker构建"
echo "=================="

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ 错误: Docker未运行，请启动Docker Desktop"
    exit 1
fi

echo "✅ Docker正在运行"

# 检查Dockerfile是否存在
if [ ! -f "Dockerfile" ]; then
    echo "❌ 错误: 未找到Dockerfile"
    exit 1
fi

echo "📁 使用Dockerfile"

# 设置镜像名称
IMAGE_NAME="protein_pocket_test"
echo "🏷️  镜像名称: $IMAGE_NAME"

# 检查是否已存在同名镜像
if docker image inspect "$IMAGE_NAME" > /dev/null 2>&1; then
    echo "🗑️  删除旧镜像..."
    docker rmi "$IMAGE_NAME" || true
fi

# 开始构建
echo "🚀 开始构建Docker镜像..."
echo "这可能需要几分钟时间，请耐心等待..."

# 构建镜像
if docker build -t "$IMAGE_NAME" .; then
    echo ""
    echo "🎉 Docker镜像构建成功!"
    echo "📁 镜像名称: $IMAGE_NAME"
    echo "📊 镜像大小: $(docker images --format "table {{.Size}}" $IMAGE_NAME | tail -1)"
    echo ""
    echo "🧪 测试镜像..."
    
    # 测试镜像
    echo "测试protein-pocket命令..."
    if docker run --rm "$IMAGE_NAME" --help > /dev/null 2>&1; then
        echo "✅ 镜像测试通过!"
        echo ""
        echo "📖 使用方法:"
        echo "  # 单文件处理"
        echo "  docker run --rm -v \$(pwd)/data:/data -v \$(pwd)/output:/output \\"
        echo "    $IMAGE_NAME run /data/protein.pdb --workdir /output"
        echo ""
        echo "  # 批量处理"
        echo "  docker run --rm -v \$(pwd)/data:/data -v \$(pwd)/output:/output \\"
        echo "    $IMAGE_NAME batch /data --results-dir /output"
        echo ""
        echo "  # 进入容器调试"
        echo "  docker run --rm -it $IMAGE_NAME /bin/bash"
    else
        echo "❌ 镜像测试失败"
        exit 1
    fi
else
    echo "❌ Docker镜像构建失败"
    echo ""
    echo "🔍 故障排除建议:"
    echo "1. 检查网络连接"
    echo "2. 尝试使用Dockerfile.simple"
    echo "3. 检查conda包版本兼容性"
    echo "4. 查看详细构建日志"
    exit 1
fi
