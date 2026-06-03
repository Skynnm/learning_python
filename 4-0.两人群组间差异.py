import pandas as pd
import scipy.stats as stats
import warnings
warnings.filterwarnings('ignore')  # 忽略无关警告

# ===================== 1. 数据读取 =====================
file_path = r"C:\Users\peng\Desktop\BC横断面肾功能\data原始数据文件\8.匹配后总表（新增肾脏彩超分类公式电解质体重均值填充）.xlsx"
df = pd.read_excel(file_path)

# 定义变量列表
categorical_vars = [
    'Cockcroft_5分级', 'aMDRD_5分级', '钙分类', '镁分类', '磷分类', '校正钙分类', '校正钙分类2', '白蛋白分类'
]
continuous_vars = ['Cockcroft', 'aMDRD']
group_var = 'group'

# ===================== 2. 数据预处理 =====================
# 检查group变量取值是否为0/1
print("=== Group变量取值检查 ===")
print(df[group_var].value_counts(dropna=False))

# 筛选有效数据（仅保留group为0/1的行，缺失值自动忽略）
df_valid = df[df[group_var].isin([0, 1])].copy()
print(f"\n有效数据行数：{len(df_valid)}（原始数据：{len(df)}）")

# 按group分组
group_0 = df_valid[df_valid[group_var] == 0]
group_1 = df_valid[df_valid[group_var] == 1]

# ===================== 3. 统计检验 =====================
# 存储结果
results = []

# -------- 3.1 分类变量：方差分析（ANOVA） --------
print("\n" + "="*50)
print("分类变量 - 方差分析（ANOVA）结果")
print("="*50)
for var in categorical_vars:
    # 提取各组数据（自动忽略缺失值）
    data_0 = group_0[var].dropna()
    data_1 = group_1[var].dropna()
    
    # 基础统计信息
    n_0, n_1 = len(data_0), len(data_1)
    mean_0, mean_1 = data_0.mean(), data_1.mean()
    std_0, std_1 = data_0.std(), data_1.std()
    
    # 方差分析
    f_stat, p_value = stats.f_oneway(data_0, data_1)
    
    # 结果存储
    results.append({
        '变量类型': '分类变量',
        '变量名': var,
        'Group0样本量': n_0,
        'Group1样本量': n_1,
        'Group0均值': round(mean_0, 3),
        'Group1均值': round(mean_1, 3),
        'Group0标准差': round(std_0, 3),
        'Group1标准差': round(std_1, 3),
        '统计量': round(f_stat, 4),
        'P值': round(p_value, 4),
        '显著性': '有' if p_value < 0.05 else '无'
    })
    
    # 打印结果
    print(f"\n【{var}】")
    print(f"Group 0: 样本量={n_0}, 均值±标准差={mean_0:.3f}±{std_0:.3f}")
    print(f"Group 1: 样本量={n_1}, 均值±标准差={mean_1:.3f}±{std_1:.3f}")
    print(f"F值={f_stat:.4f}, P值={p_value:.4f} → 组间差异：{results[-1]['显著性']}")

# -------- 3.2 连续变量：秩和检验（Mann-Whitney U检验） --------
print("\n" + "="*50)
print("连续变量 - 秩和检验（Mann-Whitney U）结果")
print("="*50)
for var in continuous_vars:
    # 提取各组数据（自动忽略缺失值）
    data_0 = group_0[var].dropna()
    data_1 = group_1[var].dropna()
    
    # 基础统计信息（中位数和四分位数）
    median_0 = data_0.median()
    q25_0, q75_0 = data_0.quantile(0.25), data_0.quantile(0.75)
    median_1 = data_1.median()
    q25_1, q75_1 = data_1.quantile(0.25), data_1.quantile(0.75)
    
    # 秩和检验
    u_stat, p_value = stats.mannwhitneyu(data_0, data_1, alternative='two-sided')
    
    # 结果存储
    results.append({
        '变量类型': '连续变量',
        '变量名': var,
        'Group0样本量': len(data_0),
        'Group1样本量': len(data_1),
        'Group0中位数': round(median_0, 3),
        'Group1中位数': round(median_1, 3),
        'Group0四分位数': f"{q25_0:.3f}-{q75_0:.3f}",
        'Group1四分位数': f"{q25_1:.3f}-{q75_1:.3f}",
        '统计量': round(u_stat, 4),
        'P值': round(p_value, 4),
        '显著性': '有' if p_value < 0.05 else '无'
    })
    
    # 打印结果
    print(f"\n【{var}】")
    print(f"Group 0: 样本量={len(data_0)}, 中位数（Q25-Q75）={median_0:.3f}（{q25_0:.3f}-{q75_0:.3f}）")
    print(f"Group 1: 样本量={len(data_1)}, 中位数（Q25-Q75）={median_1:.3f}（{q25_1:.3f}-{q75_1:.3f}）")
    print(f"U值={u_stat:.4f}, P值={p_value:.4f} → 组间差异：{results[-1]['显著性']}")

# ===================== 4. 结果导出 =====================
# 转换为DataFrame并保存
results_df = pd.DataFrame(results)
output_path = r"C:\Users\peng\Desktop\BC横断面肾功能\组间差异分析结果.xlsx"
results_df.to_excel(output_path, index=False)
print(f"\n✅ 结果已保存至：{output_path}")

# 打印汇总表
print("\n" + "="*80)
print("分析结果汇总")
print("="*80)
print(results_df[['变量类型', '变量名', 'P值', '显著性']].to_string(index=False))