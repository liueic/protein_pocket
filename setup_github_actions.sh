#!/bin/bash

# GitHub Actions 设置脚本
# 使用方法: bash setup_github_actions.sh

set -e

echo "🚀 设置GitHub Actions容器构建"
echo "================================"

# 检查是否在Git仓库中
if [ ! -d ".git" ]; then
    echo "❌ 错误: 当前目录不是Git仓库"
    echo "请先初始化Git仓库:"
    echo "  git init"
    echo "  git remote add origin <your-repo-url>"
    exit 1
fi

echo "✅ 检测到Git仓库"

# 检查必要文件是否存在
REQUIRED_FILES=("Dockerfile" "Singularity.def" "protein_pocket" "environment.yml" "test_installation.py")
MISSING_FILES=()

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -e "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo "❌ 错误: 缺少必要文件:"
    for file in "${MISSING_FILES[@]}"; do
        echo "  - $file"
    done
    exit 1
fi

echo "✅ 所有必要文件都存在"

# 检查GitHub Actions工作流文件
if [ ! -d ".github/workflows" ]; then
    echo "📁 创建GitHub Actions目录..."
    mkdir -p .github/workflows
fi

# 检查工作流文件是否存在
if [ ! -f ".github/workflows/github-registry.yml" ]; then
    echo "❌ 错误: GitHub Actions工作流文件不存在"
    echo "请确保 .github/workflows/github-registry.yml 文件存在"
    exit 1
fi

echo "✅ GitHub Actions工作流文件存在"

# 检查远程仓库
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
if [ -z "$REMOTE_URL" ]; then
    echo "❌ 错误: 未设置远程仓库"
    echo "请设置远程仓库:"
    echo "  git remote add origin <your-github-repo-url>"
    exit 1
fi

echo "✅ 远程仓库: $REMOTE_URL"

# 检查是否是GitHub仓库
if [[ ! "$REMOTE_URL" =~ github\.com ]]; then
    echo "⚠️  警告: 远程仓库不是GitHub仓库"
    echo "GitHub Actions需要GitHub仓库才能工作"
fi

# 检查工作目录是否干净
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  警告: 工作目录有未提交的更改"
    echo "建议先提交更改:"
    echo "  git add ."
    echo "  git commit -m 'Add GitHub Actions workflow'"
    echo "  git push origin main"
fi

# 显示设置摘要
echo ""
echo "📋 设置摘要"
echo "============"
echo "✅ Git仓库: 已配置"
echo "✅ 必要文件: 已检查"
echo "✅ GitHub Actions: 已配置"
echo "✅ 远程仓库: $REMOTE_URL"
echo ""

# 显示下一步操作
echo "🎯 下一步操作"
echo "============="
echo "1. 提交并推送代码到GitHub:"
echo "   git add ."
echo "   git commit -m 'Add container build workflow'"
echo "   git push origin main"
echo ""
echo "2. 在GitHub上查看构建:"
echo "   - 进入仓库的 Actions 页面"
echo "   - 查看 'Build and Push to GitHub Container Registry' 工作流"
echo ""
echo "3. 查看构建的容器:"
echo "   - 在仓库页面查看 Packages 部分"
echo "   - 下载 Singularity 镜像从 Actions artifacts"
echo ""

# 询问是否立即提交
read -p "是否立即提交并推送代码? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 提交并推送代码..."
    
    # 添加所有文件
    git add .
    
    # 提交
    git commit -m "Add GitHub Actions container build workflow

- Add Docker and Singularity container definitions
- Add automated build and test workflow
- Push to GitHub Container Registry
- Include security scanning and comprehensive testing"
    
    # 推送到远程仓库
    git push origin main
    
    echo "✅ 代码已推送到GitHub"
    echo ""
    echo "🔗 查看构建状态:"
    echo "   https://github.com/$(git remote get-url origin | sed 's/.*github.com[:/]\([^/]*\/[^/]*\)\.git.*/\1/')/actions"
else
    echo "📝 请手动提交并推送代码"
fi

echo ""
echo "🎉 设置完成!"
echo "============="
echo "您的蛋白口袋检测Pipeline现在可以通过GitHub Actions自动构建容器了!"
echo ""
echo "📖 详细使用说明请查看: GITHUB_ACTIONS_GUIDE.md"
