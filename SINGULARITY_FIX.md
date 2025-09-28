# Singularity构建问题修复

## 问题描述

Singularity构建失败，错误信息：
```
checking: conmon glib-2.0 headers... no
glib-2.0 headers are required to build conmon.
```

## 解决方案

### 1. 修复Singularity.def文件

添加了必要的glib-2.0开发头文件：
```dockerfile
apt-get update && apt-get install -y \
    wget \
    curl \
    tar \
    gzip \
    build-essential \
    libglib2.0-dev \    # 新增
    pkg-config \        # 新增
    && rm -rf /var/lib/apt/lists/*
```

### 2. 使用environment.yml

Singularity.def现在也使用environment.yml文件，与Dockerfile保持一致：
```dockerfile
# 创建conda环境（使用environment.yml）
conda env create -f /tmp/environment.yml
```

### 3. 更新GitHub Actions

在GitHub Actions的Singularity安装部分也添加了glib-2.0-dev：
```yaml
sudo apt-get install -y \
  build-essential \
  libssl-dev \
  uuid-dev \
  libgpgme11-dev \
  squashfs-tools \
  libseccomp-dev \
  wget \
  pkg-config \
  git \
  cryptsetup-bin \
  libglib2.0-dev    # 新增
```

## 修复内容

1. **Singularity.def** - 添加glib-2.0-dev和pkg-config依赖
2. **GitHub Actions** - 在Singularity安装时添加glib-2.0-dev
3. **统一环境配置** - 使用environment.yml确保一致性

## 验证修复

现在可以重新推送代码测试：

```bash
git add .
git commit -m "Fix Singularity build - add glib-2.0-dev dependency"
git push origin main
```

修复后，Singularity镜像应该能够成功构建！
