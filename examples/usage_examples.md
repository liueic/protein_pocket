# 使用示例

本文档提供了蛋白口袋检测Pipeline的各种使用场景和示例。

## 🚀 快速开始

### 1. 环境准备
```bash
# 创建并激活conda环境
conda env create -f environment.yml
conda activate protein-pocket

# 安装Python包
cd protein_pocket
pip install -e .
```

### 2. 运行快速开始脚本
```bash
# 将您的蛋白质文件放入protein/目录
# 然后运行快速开始脚本
bash examples/quick_start.sh
```

## 📋 详细使用示例

### 单文件处理示例

#### 基本用法
```bash
# 处理单个PDB文件
protein-pocket run protein/example.pdb

# 处理单个CIF文件
protein-pocket run protein/example.cif
```

#### 自定义参数
```bash
# 指定工作目录和返回前10个最佳口袋
protein-pocket run protein/example.pdb \
  --workdir my_analysis \
  --topk 10

# 使用自定义P2Rank路径
protein-pocket run protein/example.pdb \
  --prank-home /path/to/my/p2rank
```

#### 输出示例
```
──────────────────────────────── fpocket ─────────────────────────────────
***** POCKET HUNTING BEGINS ***** 
***** POCKET HUNTING ENDS ***** 

────────────────────────── filter & deduplicate ──────────────────────────
──────────────────────────── P2Rank rescoring ────────────────────────────
✓ 找到已安装的 P2Rank: /Users/.../p2rank_2.5.1
[P2Rank处理信息...]

───────────────────────────── final ranking ──────────────────────────────
Top 1: score=87.5800 center=(3.39,3.53,1.53)
Top 2: score=10.6700 center=(-13.17,12.19,-2.61)
Top 3: score=5.3300 center=(-2.74,20.54,-8.41)
```

### 批量处理示例

#### 基本批量处理
```bash
# 处理protein目录下的所有文件
protein-pocket batch protein/
```

#### 自定义批量处理
```bash
# 自定义输出目录和结果文件
protein-pocket batch protein/ \
  --workdir batch_analysis \
  --output-csv my_results.csv \
  --topk 5

# 只处理特定格式的文件
protein-pocket batch protein/ \
  --file-extensions "pdb" \
  --topk 3
```

#### 批量处理输出示例
```
开始批量处理蛋白质口袋检测
输入目录: protein/
工作目录: batch_runs
输出CSV: batch_results.csv
文件扩展名: pdb,cif
找到 5 个蛋白质文件

处理 fold_2025_09_23_15_12_model_0 ━━━━━━━━━━━━━━ 100% • 0:00:17 • 0:00:00
✓ 批量处理结果已保存到: batch_results.csv

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

批量处理完成!
详细结果请查看: batch_results.csv
```

## 📊 结果分析示例

### CSV结果文件格式
```csv
protein_name,protein_path,status,error_message,num_pockets_detected,num_pockets_filtered,processing_time,top_pocket_1_score,top_pocket_1_center_x,top_pocket_1_center_y,top_pocket_1_center_z,top_pocket_2_score,top_pocket_2_center_x,top_pocket_2_center_y,top_pocket_2_center_z,top_pocket_3_score,top_pocket_3_center_x,top_pocket_3_center_y,top_pocket_3_center_z
fold_2025_09_23_15_12_model_0,protein/fold_2025_09_23_15_12_model_0.cif,success,,36,1,4.01,87.5800,3.388,3.533,1.525,10.6700,-13.169,12.192,-2.606,5.3300,-2.737,20.536,-8.405
fold_2025_09_23_15_12_model_1,protein/fold_2025_09_23_15_12_model_1.cif,success,,40,1,3.25,59.3900,3.137,-3.617,-2.188,38.7300,2.553,-2.330,7.091,12.7700,-2.850,4.754,17.231
```

### 结果解读
- **score**: P2Rank重打分后的口袋质量分数（越高越好）
- **center_x/y/z**: 口袋中心的三维坐标
- **num_pockets_detected**: fpocket检测到的原始口袋数量
- **num_pockets_filtered**: 过滤去重后的口袋数量
- **processing_time**: 单个文件的处理时间

## 🔧 高级用法

### 处理大型数据集
```bash
# 对于大量文件，建议分批处理
protein-pocket batch dataset_part1/ --workdir batch1 --output-csv results1.csv
protein-pocket batch dataset_part2/ --workdir batch2 --output-csv results2.csv
```

### 自定义文件扩展名
```bash
# 只处理PDB文件
protein-pocket batch protein/ --file-extensions "pdb"

# 处理多种格式
protein-pocket batch protein/ --file-extensions "pdb,cif,ent"
```

### 调试模式
```bash
# 查看详细的处理信息
protein-pocket run protein/example.pdb --workdir debug_runs

# 检查中间结果
ls debug_runs/
# 查看fpocket输出
ls debug_runs/example_fpocket/
# 查看P2Rank输出
ls debug_runs/p2rank_out/
```

## 🐛 常见问题解决

### 1. P2Rank自动安装失败
```bash
# 手动下载并指定路径
wget https://github.com/rdk/p2rank/releases/download/2.5.1/p2rank_2.5.1.tar.gz
tar -xzf p2rank_2.5.1.tar.gz
protein-pocket run protein/example.pdb --prank-home ./p2rank_2.5.1
```

### 2. 内存不足
```bash
# 对于大型蛋白质，减少topk数量
protein-pocket run protein/large_protein.pdb --topk 3
```

### 3. 文件格式问题
```bash
# 检查文件格式
file protein/example.pdb
# 确保文件是有效的PDB或CIF格式
```

## 📈 性能优化建议

1. **批量处理**: 对于多个文件，使用batch命令比单独处理更高效
2. **合理设置topk**: 根据需求设置合适的topk值，避免不必要的计算
3. **磁盘空间**: 确保有足够的磁盘空间存储中间结果
4. **网络连接**: 首次运行需要下载P2Rank，确保网络稳定

## 🔍 结果验证

### 检查处理结果
```bash
# 查看CSV结果
head -5 batch_results.csv

# 统计成功率
grep -c "success" batch_results.csv

# 查看失败的文件
grep "failed" batch_results.csv
```

### 可视化结果
P2Rank会在工作目录中生成可视化文件：
```bash
# 查看可视化结果
ls batch_runs/*/p2rank_out/visualizations/
```

这些文件可以用PyMOL或其他分子可视化软件打开。
