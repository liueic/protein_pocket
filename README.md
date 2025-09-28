# 蛋白口袋检测 Pipeline

一个完整的蛋白口袋检测和评估pipeline，集成了fpocket几何预测和P2Rank机器学习重打分，支持单文件和批量处理

引用项目：

- fpocket：https://github.com/Discngine/fpocket
- P2Rank：https://github.com/rdk/p2rank

## 系统要求

- Python 3.11+
- Conda环境管理器
- 网络连接（用于自动下载P2Rank）

## 安装

### 创建Conda环境
```bash
# 如果环境不存在，创建新环境
conda env create -f environment.yml

# 如果环境已存在，更新环境
conda env update -f environment.yml

# 激活环境
conda activate protein-pocket
```

**注意**：如果网络较慢，可以使用国内镜像源：
```bash
# 使用清华镜像源（可选）
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/bioconda
```

### 安装项目包
```bash
cd protein_pocket
pip install -e .
```

**说明**：这一步安装我们自己的`protein_pocket`包，使`protein-pocket`命令可用。虽然依赖包已在conda环境中安装，但项目本身需要以可编辑模式安装。

### 验证安装
```bash
# 运行安装测试脚本
python test_installation.py
```

## 快速开始

### 手动运行
```bash
# 1. 激活环境
conda activate protein-pocket

# 2. 处理单个文件
protein-pocket run protein/example.pdb

# 3. 批量处理
protein-pocket batch protein/
```

**注意**：首次运行时会自动下载P2Rank（约200MB），请确保网络连接稳定。

## 详细使用方法

### 单文件处理

处理单个蛋白质结构文件：

```bash
protein-pocket run <蛋白质文件路径> [选项]
```

**示例：**
```bash
# 基本用法
protein-pocket run protein/example.pdb

# 自定义选项
protein-pocket run protein/example.cif \
  --workdir my_runs \
  --topk 5 \
  --prank-home /path/to/p2rank
```

**参数说明：**
- `蛋白质文件路径`：输入的PDB或CIF文件路径
- `--workdir`：工作目录，默认为"runs"
- `--topk`：返回前N个最佳口袋，默认为5
- `--prank-home`：P2Rank安装路径（可选，会自动安装）

### 批量处理

处理整个文件夹的蛋白质文件，保持目录结构：

```bash
protein-pocket batch <输入目录> [选项]
```

**示例：**
```bash
# 基本批量处理：处理protein/目录，结果保存到results/目录
protein-pocket batch protein/

# 自定义批量处理
protein-pocket batch protein/ \
  --results-dir my_results \
  --topk 3 \
  --output-csv results.csv \
  --file-extensions "pdb,cif"

# 只处理.pdb文件
protein-pocket batch protein/ \
  --file-extensions "pdb"
```

**参数说明：**
- `输入目录`：包含蛋白质文件的目录
- `--results-dir`：结果输出目录，默认为"results"。每个蛋白质的结果会保存在对应的子目录中，保持与输入目录相同的结构
- `--topk`：每个蛋白质返回前N个最佳口袋，默认为5
- `--output-csv`：结果CSV文件名，默认为"batch_results.csv"
- `--file-extensions`：要处理的文件扩展名，默认为"pdb,cif"

**目录结构示例：**
```
protein/                    # 输入目录
├── protein1.pdb
├── subfolder/
│   └── protein2.cif
└── protein3.pdb

results/                    # 输出目录（保持相同结构）
├── protein1/              # protein1.pdb的结果
│   ├── protein1_fpocket/  # fpocket输出
│   ├── p2rank_out/        # P2Rank输出
│   └── protein1_pocket_results.csv  # 详细口袋结果CSV
├── subfolder/
│   └── protein2/          # protein2.cif的结果
│       ├── protein2_fpocket/
│       ├── p2rank_out/
│       └── protein2_pocket_results.csv
└── protein3/              # protein3.pdb的结果
    ├── protein3_fpocket/
    ├── p2rank_out/
    └── protein3_pocket_results.csv
```

**每个蛋白质的详细CSV文件包含以下信息：**
- `pocket_name`: 口袋名称（如pocket.1, pocket.2等）
- `rank`: 最终排名（按P2Rank分数排序）
- `score`: P2Rank重打分后的分数
- `center_x`, `center_y`, `center_z`: 口袋中心坐标
- `raw_score`: fpocket原始分数
- `fpocket_rank`: fpocket原始排名
- `rank_change`: 排名变化（正数表示排名上升，负数表示排名下降）

## 输出结果

### 单文件处理输出

Pipeline会显示以下信息：
```
──────────────────────────────── fpocket ─────────────────────────────────
***** POCKET HUNTING BEGINS ***** 
***** POCKET HUNTING ENDS ***** 

────────────────────────── filter & deduplicate ──────────────────────────
──────────────────────────── P2Rank rescoring ────────────────────────────
✓ 找到已安装的 P2Rank: /path/to/p2rank_2.5.1
[P2Rank处理信息...]

───────────────────────────── final ranking ──────────────────────────────
Top 1: score=87.5800 center=(3.39,3.53,1.53)
Top 2: score=10.6700 center=(-13.17,12.19,-2.61)
Top 3: score=5.3300 center=(-2.74,20.54,-8.41)
```

### 批量处理输出

生成CSV文件，包含以下列：
- `protein_name`：蛋白质名称
- `protein_path`：蛋白质文件路径
- `status`：处理状态（success/failed）
- `error_message`：错误信息（如果有）
- `num_pockets_detected`：检测到的口袋数量
- `num_pockets_filtered`：过滤后的口袋数量
- `processing_time`：处理时间（秒）
- `top_pocket_1_score`：最佳口袋分数
- `top_pocket_1_center_x/y/z`：最佳口袋中心坐标
- `top_pocket_2_score`：第二佳口袋分数和坐标
- `top_pocket_3_score`：第三佳口袋分数和坐标

**批量处理摘要示例：**
```
       批量处理摘要       
┏━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ 统计项       ┃ 数值    ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ 总文件数     │ 5       │
│ 成功处理     │ 5       │
│ 处理失败     │ 0       │
│ 成功率       │ 100.0%  │
│ 总处理时间   │ 17.7 秒 │
│ 平均处理时间 │ 3.5 秒  │
└──────────────┴─────────┘
```

## Pipeline工作流程

1. **fpocket几何预测**
   - 使用fpocket检测蛋白质表面的几何口袋
   - 生成初始口袋候选和评分

2. **过滤和去重**
   - 根据口袋中心距离和残基重叠进行去重
   - 保留每个重叠组中评分最高的口袋

3. **P2Rank重打分**
   - 使用机器学习模型重新评估口袋质量
   - 提供更准确的活性位点预测

4. **最终排序**
   - 按P2Rank分数排序
   - 返回前N个最佳口袋

## 参考论文

考虑了这篇论文对于蛋白质口袋预测的打分方法：https://jcheminf.biomedcentral.com/articles/10.1186/s13321-024-00923-z

### **选择基础几何预测器 (Base Geometric Prediction)**

论文中显示，高性能的组合方法（如 DeepPocketRESC 和 fpocketPRANK）都选择 **fpocket** 的输出作为**起点**。几何方法在识别空腔方面快速且可靠，运行基础工具，生成一组**未经过滤和重新排名**的原始候选口袋，每个口袋都会有一个原始分数

### 处理冗余与筛选（Refining & Filtering）

需要按照以下步骤：

1. **定义重叠：**设定一个阈值（例如：口袋中心点距离 ≤5A˚，或**残基重叠 Jaccard 指数 ≥0.75**，这是论文中使用的标准）
2. **去冗余：** 遍历所有预测口袋，识别出所有重叠的口袋群组
3. **保留最优：** 在每个重叠的群组中，**只保留**原始分数**最高**的那一个口袋，**丢弃**其余冗余的口袋
4. **操作目标：** 得到一组**精简、不重叠**的候选口袋集合

### 重打分 (Re-scoring with P2Rank/PRANK)

使用P2Rank导出前面自定义的外部口袋，然后再对其进行重新打分，

### 最终排名与选择（Final Ranking）

根据 P2Rank 输出的新分数对口袋进行排序，分数最高的即为最佳预测结果

需要考虑到召回率

论文中使用的 **“Top-N”** 评估，其具体含义是：**“我们只考虑每个蛋白质的前 N 个预测结果”**

- **N：** 代表一个蛋白质**实际拥有的**、**经过 LIGYSIS 数据库验证的结合位点数量**
- **+2：** 是一个**额外的缓冲**。研究人员在评估时，将预测数量的上限设为 **N (实际结合位点数) 加上 2 个额外的预测**
    - **例子：** 如果一个蛋白质有 N=1 个已知的结合位点，评估时会检查该方法的 **Top 3 预测**（1+2）是否命中了这个位点
    - 如果一个蛋白质有 N=3 个已知的结合位点，评估时会检查该方法的 **Top 5 预测**（3+2）是否命中了这 3 个位点

在实际处理蛋白中

- **Top 1：** 永远是最应该关注的口袋（最具信心的预测）
- **Top 3（或 Top 5）：** 检查得分排在前 3 个（或 5 个）的口袋，以确保没有遗漏任何潜在的结合位点