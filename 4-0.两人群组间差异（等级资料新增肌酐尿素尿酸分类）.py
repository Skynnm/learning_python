import pandas as pd
import scipy.stats as stats
import warnings
warnings.filterwarnings('ignore')  # 忽略无关警告

# ===================== 1. 配置项 =====================
# 文件路径
file_path = r"C:\Users\peng\Desktop\BC横断面肾功能\data原始数据文件\9.匹配后总表（新增肾脏彩超分类公式电解质肌酐尿酸）.xlsx"
output_path = r"C:\Users\peng\Desktop\BC横断面肾功能\组间差异分析结果.xlsx"

# 变量定义
# 等级变量（有序分类）- 1=正常, 2=低值, 3=高值
ordinal_vars = [
    '钙分类', '镁分类', '磷分类', '校正钙分类', '校正钙分类2', '白蛋白分类', '肌酐分类', '尿素分类', '尿酸分类'
]
# 肾功能分级变量（特殊等级变量）
renal_function_vars = ['Cockcroft_5分级', 'aMDRD_5分级']
# 连续变量
continuous_vars = ['Cockcroft', 'aMDRD']
# 分组变量
group_var = 'group'

# 等级含义说明
grade_explanation = """
等级变量说明：
1 = 正常值
2 = 低值
3 = 高值
"""

# ===================== 2. 数据读取与预处理 =====================
# 读取数据
df = pd.read_excel(file_path)

# 检查group变量取值
print("=== 分组变量(Group)取值检查 ===")
group_counts = df[group_var].value_counts(dropna=False)
print(group_counts)

# 筛选有效数据（仅保留group为0/1的行）
df_valid = df[df[group_var].isin([0, 1])].copy()
print(f"\n有效数据行数：{len(df_valid)}（原始数据：{len(df)}）")
print(f"Group 0 样本量：{len(df_valid[df_valid[group_var]==0])}")
print(f"Group 1 样本量：{len(df_valid[df_valid[group_var]==1])}")

# 按group分组
group_0 = df_valid[df_valid[group_var] == 0]
group_1 = df_valid[df_valid[group_var] == 1]

# ===================== 3. 统计检验函数 =====================
def analyze_ordinal_variable(var_name, data0, data1, var_type="电解质等级"):
    """分析等级变量（Kruskal-Wallis H检验）"""
    # 去除缺失值
    d0 = data0[var_name].dropna()
    d1 = data1[var_name].dropna()
    
    # 基础统计描述（中位数、四分位数、各等级分布）
    n0, n1 = len(d0), len(d1)
    median0, median1 = d0.median(), d1.median()
    q25_0, q75_0 = d0.quantile(0.25), d0.quantile(0.75)
    q25_1, q75_1 = d1.quantile(0.25), d1.quantile(0.75)
    
    # 各等级分布统计
    dist0 = d0.value_counts().sort_index()
    dist1 = d1.value_counts().sort_index()
    
    # Kruskal-Wallis H检验（两组时等价于Mann-Whitney U检验）
    # 这里直接使用Mann-Whitney U检验更适合两组比较
    u_stat, p_value = stats.mannwhitneyu(d0, d1, alternative='two-sided')
    # 计算H统计量（用于等级资料的报告）
    h_stat = (12 * u_stat) / (n0 * n1 * (n0 + n1 + 1)) * (n0 * n1) - 3 * (n0 + n1 + 1)
    
    # 结果整理
    result = {
        '变量类型': f'等级变量({var_type})',
        '变量名': var_name,
        'Group0样本量': n0,
        'Group1样本量': n1,
        'Group0中位数': round(median0, 3),
        'Group1中位数': round(median1, 3),
        'Group0四分位数': f"{q25_0:.3f}-{q75_0:.3f}",
        'Group1四分位数': f"{q25_1:.3f}-{q75_1:.3f}",
        'U统计量': round(u_stat, 4),
        'H统计量': round(h_stat, 4),
        'P值': round(p_value, 4),
        '显著性': '有' if p_value < 0.05 else '无',
        'Group0各等级分布': dict(dist0),
        'Group1各等级分布': dict(dist1)
    }
    
    # 打印详细结果
    print(f"\n【{var_name}】({var_type})")
    print(f"Group 0: 样本量={n0}, 中位数（Q25-Q75）={median0:.3f}（{q25_0:.3f}-{q75_0:.3f}）")
    print(f"        等级分布：{dict(dist0)}")
    print(f"Group 1: 样本量={n1}, 中位数（Q25-Q75）={median1:.3f}（{q25_1:.3f}-{q75_1:.3f}）")
    print(f"        等级分布：{dict(dist1)}")
    print(f"检验结果：U值={u_stat:.4f}, H值={h_stat:.4f}, P值={p_value:.4f}")
    print(f"        组间差异：{'有统计学意义' if p_value < 0.05 else '无统计学意义'} (α=0.05)")
    
    return result

def analyze_continuous_variable(var_name, data0, data1):
    """分析连续变量（Mann-Whitney U检验）"""
    # 去除缺失值
    d0 = data0[var_name].dropna()
    d1 = data1[var_name].dropna()
    
    # 基础统计描述
    n0, n1 = len(d0), len(d1)
    median0, median1 = d0.median(), d1.median()
    q25_0, q75_0 = d0.quantile(0.25), d0.quantile(0.75)
    q25_1, q75_1 = d1.quantile(0.25), d1.quantile(0.75)
    mean0, mean1 = d0.mean(), d1.mean()
    std0, std1 = d0.std(), d1.std()
    
    # Mann-Whitney U检验
    u_stat, p_value = stats.mannwhitneyu(d0, d1, alternative='two-sided')
    
    # 结果整理
    result = {
        '变量类型': '连续变量',
        '变量名': var_name,
        'Group0样本量': n0,
        'Group1样本量': n1,
        'Group0中位数': round(median0, 3),
        'Group1中位数': round(median1, 3),
        'Group0四分位数': f"{q25_0:.3f}-{q75_0:.3f}",
        'Group1四分位数': f"{q25_1:.3f}-{q75_1:.3f}",
        'Group0均值±标准差': f"{mean0:.3f}±{std0:.3f}",
        'Group1均值±标准差': f"{mean1:.3f}±{std1:.3f}",
        'U统计量': round(u_stat, 4),
        'P值': round(p_value, 4),
        '显著性': '有' if p_value < 0.05 else '无'
    }
    
    # 打印详细结果
    print(f"\n【{var_name}】")
    print(f"Group 0: 样本量={n0}, 中位数（Q25-Q75）={median0:.3f}（{q25_0:.3f}-{q75_0:.3f}）")
    print(f"        均值±标准差：{mean0:.3f}±{std0:.3f}")
    print(f"Group 1: 样本量={n1}, 中位数（Q25-Q75）={median1:.3f}（{q25_1:.3f}-{q75_1:.3f}）")
    print(f"        均值±标准差：{mean1:.3f}±{std1:.3f}")
    print(f"检验结果：U值={u_stat:.4f}, P值={p_value:.4f}")
    print(f"        组间差异：{'有统计学意义' if p_value < 0.05 else '无统计学意义'} (α=0.05)")
    
    return result

# ===================== 4. 执行统计分析 =====================
# 存储所有结果
all_results = []

print("\n" + "="*60)
print("1. 电解质等级变量分析（Kruskal-Wallis H检验）")
print("="*60)
print(grade_explanation)

# 分析电解质等级变量
for var in ordinal_vars:
    result = analyze_ordinal_variable(var, group_0, group_1, "电解质等级")
    all_results.append(result)

print("\n" + "="*60)
print("2. 肾功能分级变量分析（Kruskal-Wallis H检验）")
print("="*60)

# 分析肾功能分级变量
for var in renal_function_vars:
    result = analyze_ordinal_variable(var, group_0, group_1, "肾功能分级")
    all_results.append(result)

print("\n" + "="*60)
print("3. 连续变量分析（Mann-Whitney U检验）")
print("="*60)

# 分析连续变量
for var in continuous_vars:
    result = analyze_continuous_variable(var, group_0, group_1)
    all_results.append(result)

# ===================== 5. 结果整理与导出 =====================
# 整理结果表格（简化展示）
results_df = pd.DataFrame(all_results)

# 选择要导出的列
export_columns = [
    '变量类型', '变量名', 'Group0样本量', 'Group1样本量',
    'Group0中位数', 'Group1中位数', 'P值', '显著性'
]

# 补充连续变量的均值标准差列（如果存在）
if 'Group0均值±标准差' in results_df.columns:
    export_columns.insert(7, 'Group0均值±标准差')
    export_columns.insert(8, 'Group1均值±标准差')

# 创建导出用的DataFrame
export_df = results_df[export_columns].copy()

# 保存结果到Excel
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    # 主要结果
    export_df.to_excel(writer, sheet_name='统计检验结果', index=False)
    
    # 详细分布结果
    detailed_results = []
    for _, row in results_df.iterrows():
        detail = {
            '变量类型': row['变量类型'],
            '变量名': row['变量名'],
            'Group0样本量': row['Group0样本量'],
            'Group1样本量': row['Group1样本量'],
            'Group0中位数': row['Group0中位数'],
            'Group1中位数': row['Group1中位数'],
            'Group0四分位数': row.get('Group0四分位数', ''),
            'Group1四分位数': row.get('Group1四分位数', ''),
            'U统计量': row.get('U统计量', ''),
            'H统计量': row.get('H统计量', ''),
            'P值': row['P值'],
            '显著性': row['显著性'],
            'Group0各等级分布': str(row.get('Group0各等级分布', '')),
            'Group1各等级分布': str(row.get('Group1各等级分布', ''))
        }
        detailed_results.append(detail)
    
    pd.DataFrame(detailed_results).to_excel(writer, sheet_name='详细结果', index=False)
    
    # 等级说明
    explanation_df = pd.DataFrame({
        '说明': [
            '等级变量含义：',
            '1 = 正常值',
            '2 = 低值', 
            '3 = 高值',
            '',
            '显著性判断标准：',
            'P < 0.05 为有统计学意义',
            '',
            '检验方法说明：',
            '等级变量：Kruskal-Wallis H检验（Mann-Whitney U检验）',
            '连续变量：Mann-Whitney U检验'
        ]
    })
    explanation_df.to_excel(writer, sheet_name='说明', index=False)

# ===================== 6. 输出汇总信息 =====================
print(f"\n" + "="*80)
print("分析结果汇总")
print("="*80)
print(export_df.to_string(index=False))

print(f"\n✅ 结果已保存至：{output_path}")
print(f"\n📋 输出文件包含3个工作表：")
print("   1. 统计检验结果 - 主要统计结果")
print("   2. 详细结果 - 包含四分位数、统计量、等级分布等")
print("   3. 说明 - 变量含义和检验方法说明")

# 打印有统计学意义的变量
significant_vars = export_df[export_df['显著性'] == '有']['变量名'].tolist()
if significant_vars:
    print(f"\n🔍 有统计学意义的变量（P<0.05）：")
    for var in significant_vars:
        print(f"   - {var}")
else:
    print(f"\n🔍 无统计学意义的变量（所有P≥0.05）")

# 打印等级说明
print(f"\n📖 {grade_explanation}")