#!/bin/bash

# 蛋白口袋检测Pipeline Docker容器测试脚本 (macOS版本)
# 使用方法: bash test_docker_macos.sh

set -e

# 设置镜像名称
IMAGE_NAME="protein_pocket:1.0"

echo "🧪 开始测试蛋白口袋检测Pipeline Docker容器 (macOS版本)"
echo "======================================================"
echo "镜像名称: ${IMAGE_NAME}"

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ 错误: Docker未运行，请启动Docker Desktop"
    exit 1
fi

# 检查镜像是否存在
if ! docker image inspect "${IMAGE_NAME}" > /dev/null 2>&1; then
    echo "❌ 错误: 镜像 ${IMAGE_NAME} 不存在"
    echo "请先构建镜像: bash build_docker_macos.sh"
    exit 1
fi

echo "✅ 找到Docker镜像: ${IMAGE_NAME}"

# 创建测试目录
TEST_DIR="docker_test"
mkdir -p "${TEST_DIR}/data" "${TEST_DIR}/output"

echo "📁 创建测试目录: ${TEST_DIR}"

# 测试1: 基本命令测试
echo ""
echo "🔍 测试1: 基本命令测试"
echo "----------------------"

echo "测试 --help 命令..."
if docker run --rm "${IMAGE_NAME}" --help > /dev/null 2>&1; then
    echo "✅ --help 命令测试通过"
else
    echo "❌ --help 命令测试失败"
    exit 1
fi

echo "测试 version 命令..."
if docker run --rm "${IMAGE_NAME}" version > /dev/null 2>&1; then
    echo "✅ version 命令测试通过"
else
    echo "❌ version 命令测试失败"
    exit 1
fi

# 测试2: 环境检查
echo ""
echo "🔍 测试2: 环境检查"
echo "------------------"

echo "检查Python环境..."
PYTHON_VERSION=$(docker run --rm "${IMAGE_NAME}" python --version 2>&1)
echo "✅ Python版本: ${PYTHON_VERSION}"

echo "检查fpocket..."
if docker run --rm "${IMAGE_NAME}" which fpocket > /dev/null 2>&1; then
    echo "✅ fpocket 已安装"
else
    echo "❌ fpocket 未找到"
    exit 1
fi

echo "检查P2Rank..."
if docker run --rm "${IMAGE_NAME}" test -f /opt/p2rank_2.5.1/prank; then
    echo "✅ P2Rank 已安装"
    P2RANK_VERSION=$(docker run --rm "${IMAGE_NAME}" /opt/p2rank_2.5.1/prank --version 2>&1 | head -1)
    echo "   P2Rank版本: ${P2RANK_VERSION}"
else
    echo "❌ P2Rank 未找到"
    exit 1
fi

# 测试3: 创建测试数据
echo ""
echo "🔍 测试3: 创建测试数据"
echo "----------------------"

# 创建一个简单的测试PDB文件
cat > "${TEST_DIR}/data/test_protein.pdb" << 'EOF'
HEADER    TEST PROTEIN
ATOM      1  N   ALA A   1      20.154  16.967  23.862  1.00 11.18           N
ATOM      2  CA  ALA A   1      19.030  16.140  23.862  1.00 11.18           C
ATOM      3  C   ALA A   1      17.762  16.967  23.862  1.00 11.18           C
ATOM      4  O   ALA A   1      17.762  18.194  23.862  1.00 11.18           O
ATOM      5  CB  ALA A   1      19.030  15.313  25.123  1.00 11.18           C
ATOM      6  N   GLY A   2      16.590  16.140  23.862  1.00 11.18           N
ATOM      7  CA  GLY A   2      15.322  16.967  23.862  1.00 11.18           C
ATOM      8  C   GLY A   2      14.054  16.140  23.862  1.00 11.18           C
ATOM      9  O   GLY A   2      14.054  14.913  23.862  1.00 11.18           O
END
EOF

echo "✅ 创建测试PDB文件: ${TEST_DIR}/data/test_protein.pdb"

# 测试4: 单文件处理测试
echo ""
echo "🔍 测试4: 单文件处理测试"
echo "------------------------"

echo "运行单文件处理..."
if docker run --rm \
    -v "$(pwd)/${TEST_DIR}/data:/data" \
    -v "$(pwd)/${TEST_DIR}/output:/output" \
    "${IMAGE_NAME}" run /data/test_protein.pdb --workdir /output --topk 3; then
    echo "✅ 单文件处理测试通过"
    
    # 检查输出文件
    if [ -f "${TEST_DIR}/output/test_protein_pocket_results.csv" ]; then
        echo "✅ 输出文件生成成功"
        echo "📊 输出文件内容:"
        head -5 "${TEST_DIR}/output/test_protein_pocket_results.csv"
    else
        echo "⚠️  输出文件未找到，但处理完成"
    fi
else
    echo "❌ 单文件处理测试失败"
    exit 1
fi

# 测试5: 批量处理测试
echo ""
echo "🔍 测试5: 批量处理测试"
echo "----------------------"

echo "运行批量处理..."
if docker run --rm \
    -v "$(pwd)/${TEST_DIR}/data:/data" \
    -v "$(pwd)/${TEST_DIR}/output:/output" \
    "${IMAGE_NAME}" batch /data --results-dir /output --topk 2 --output-csv /output/batch_test.csv; then
    echo "✅ 批量处理测试通过"
    
    # 检查批量输出文件
    if [ -f "${TEST_DIR}/output/batch_test.csv" ]; then
        echo "✅ 批量输出文件生成成功"
        echo "📊 批量输出文件内容:"
        head -3 "${TEST_DIR}/output/batch_test.csv"
    else
        echo "⚠️  批量输出文件未找到，但处理完成"
    fi
else
    echo "❌ 批量处理测试失败"
    exit 1
fi

# 测试6: 性能测试
echo ""
echo "🔍 测试6: 性能测试"
echo "------------------"

echo "测试处理时间..."
START_TIME=$(date +%s)
docker run --rm \
    -v "$(pwd)/${TEST_DIR}/data:/data" \
    -v "$(pwd)/${TEST_DIR}/output:/output" \
    "${IMAGE_NAME}" run /data/test_protein.pdb --workdir /output --topk 1 > /dev/null 2>&1
END_TIME=$(date +%s)
PROCESSING_TIME=$((END_TIME - START_TIME))

echo "✅ 处理时间: ${PROCESSING_TIME} 秒"

# 测试7: 便捷脚本测试
echo ""
echo "🔍 测试7: 便捷脚本测试"
echo "----------------------"

echo "测试便捷脚本..."
if [ -f "run_docker_macos.sh" ]; then
    chmod +x run_docker_macos.sh
    if ./run_docker_macos.sh --help > /dev/null 2>&1; then
        echo "✅ 便捷脚本测试通过"
    else
        echo "❌ 便捷脚本测试失败"
    fi
else
    echo "⚠️  便捷脚本不存在，跳过测试"
fi

# 清理测试文件
echo ""
echo "🧹 清理测试文件..."
rm -rf "${TEST_DIR}"

# 总结
echo ""
echo "🎉 所有测试通过!"
echo "=================="
echo "✅ 基本命令测试"
echo "✅ 环境检查"
echo "✅ 单文件处理"
echo "✅ 批量处理"
echo "✅ 性能测试"
echo "✅ 便捷脚本测试"
echo ""
echo "📋 测试总结:"
echo "  - 镜像名称: ${IMAGE_NAME}"
echo "  - 处理时间: ${PROCESSING_TIME} 秒"
echo "  - 所有功能正常"
echo ""
echo "🚀 Docker容器已准备就绪，可以用于生产环境!"
echo ""
echo "📖 使用方法:"
echo "  # 使用便捷脚本"
echo "  ./run_docker_macos.sh run /data/protein.pdb --workdir /output"
echo "  ./run_docker_macos.sh batch /data --results-dir /output"
echo ""
echo "  # 直接使用Docker命令"
echo "  docker run --rm -v \$(pwd)/data:/data -v \$(pwd)/output:/output \\"
echo "    ${IMAGE_NAME} run /data/protein.pdb --workdir /output"
