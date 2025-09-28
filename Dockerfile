# 蛋白口袋检测Pipeline Docker容器
FROM continuumio/miniconda3:latest

LABEL maintainer="Aicnal Liueic <liusomes@gmail.com>"
LABEL version="1.0"
LABEL description="Protein pocket detection pipeline with fpocket and P2Rank"

# 设置环境变量
ENV PATH="/opt/conda/bin:$PATH"
ENV P2RANK_HOME="/opt/p2rank_2.5.1"
ENV PATH="$P2RANK_HOME:$PATH"
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    tar \
    gzip \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制环境配置文件
COPY environment.yml /tmp/

# 创建conda环境（使用environment.yml）
RUN conda env create -f /tmp/environment.yml

# 下载并安装P2Rank
RUN cd /opt && \
    wget https://github.com/rdk/p2rank/releases/download/2.5.1/p2rank_2.5.1.tar.gz && \
    tar -xzf p2rank_2.5.1.tar.gz && \
    rm p2rank_2.5.1.tar.gz && \
    chmod +x /opt/p2rank_2.5.1/prank

# 测试P2Rank安装
RUN conda run -n protein-pocket /opt/p2rank_2.5.1/prank --version

# 创建应用目录
RUN mkdir -p /app /data /output

# 复制项目文件
COPY protein_pocket/ /app/protein_pocket/
COPY test_installation.py /app/

# 安装项目包
WORKDIR /app
RUN conda run -n protein-pocket pip install -e protein_pocket/

# 测试安装
RUN conda run -n protein-pocket python test_installation.py

# 设置默认命令
ENTRYPOINT ["conda", "run", "-n", "protein-pocket", "protein-pocket"]
CMD ["--help"]