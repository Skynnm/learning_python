import pandas as pd
import numpy as np
import scipy.stats as stats
from scipy.stats import mannwhitneyu
import os

# 设置中文显示
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
import seaborn as sns
sns.set(font_scale=1.0)
sns.set_style("whitegrid")

# 读取数据
file_path = r"C:\Users\peng\Desktop\BC横断面肾功能\data原始数据文件\3.匹配后总表.xlsx"
try:
    df = pd.read_excel(file_path)
    print(f"数据读取成功，共{df.shape[0]}行，{df.shape[1]}列")
except Exception as e:
    print(f"数据读取失败：{e}")
    exit()

# 定义变量列表
quantitative_vars = [
    '肌酐1', 'BMI', 'eGFR_2009', '尿素', '尿酸', '钙', '镁', '磷', '白蛋白', 
    '白蛋白校正钙', '钙磷乘积', '总胆红素', '直接胆红素', '谷酰转移酶', 
    '谷丙转氨酶', '谷草转氨酶', '碱性磷酸酶', '总胆汁酸', '乳酸脱氢酶', 
    '白细胞总数', '红细胞', '血红蛋白', '血小板', '红细胞比容', '总胆固醇', 
    '甘油三脂', '高密度脂蛋白', '低密度脂蛋白', '载脂蛋白A', '载脂蛋白B', 
    '脂蛋白α', '超敏C反应蛋白', '血糖'
]

categorical_vars = [
    'RI2009_5分级', 'RI2009_4分级','RI2009_3分级', 'RI2009_2分级1', 'RI2009_2分级2'
]

# 检查数据中是否存在这些变量
missing_vars = [var for var in quantitative_vars + categorical_vars if var not in df.columns]
if missing_vars:
    print(f"警告：数据中缺少以下变量：{missing_vars}")
    exit()

# 检查group变量
if 'group' not in df.columns:
    print("数据中缺少'group'变量")
    exit()

# 分组
group1 = df[df['group'] == 1]  # 乳腺癌患者
group0 = df[df['group'] == 0]  # 体检人群（假设group=0为体检人群，根据描述可能需要调整）

print(f"乳腺癌患者数量：{len(group1)}")
print(f"体检人群数量：{len(group0)}")

# ----------------------定量变量分析----------------------
def analyze_quantitative(var):
    # 描述性统计
    desc1 = group1[var].describe(percentiles=[0.25, 0.75])
    desc0 = group0[var].describe(percentiles=[0.25, 0.75])
    
    # 提取需要的统计量
    stats1 = {
        '中位数': desc1['50%'],
        '下四分位数': desc1['25%'],
        '上四分位数': desc1['75%'],
        '样本量': desc1['count']
    }
    
    stats0 = {
        '中位数': desc0['50%'],
        '下四分位数': desc0['25%'],
        '上四分位数': desc0['75%'],
        '样本量': desc0['count']
    }
    
    # 秩和检验 (Mann-Whitney U检验)
    try:
        # 去除缺失值
        data1 = group1[var].dropna()
        data0 = group0[var].dropna()
        stat, p_value = mannwhitneyu(data1, data0, alternative='two-sided')
        significant = '是' if p_value < 0.05 else '否'
    except Exception as e:
        p_value = np.nan
        significant = '无法计算'
        print(f"变量{var}的秩和检验出错：{e}")
    
    return {
        '乳腺癌患者': stats1,
        '体检人群': stats0,
        'p值': p_value,
        '差异显著': significant
    }

# 处理所有定量变量
quant_results = {}
for var in quantitative_vars:
    quant_results[var] = analyze_quantitative(var)

# ----------------------分类变量分析----------------------
def analyze_categorical(var):
    # 交叉表
    contingency = pd.crosstab(df[var], df['group'], margins=True)
    contingency.columns = ['体检人群', '乳腺癌患者', '合计']
    
    # 计算比例
    prop_table = pd.DataFrame()
    for col in ['体检人群', '乳腺癌患者']:
        prop_table[f'{col}_数量'] = contingency[col]
        prop_table[f'{col}_比例(%)'] = (contingency[col] / contingency.loc['All', col] * 100).round(2)
    
    # 卡方检验
    try:
        # 去除合计行
        observed = contingency.iloc[:-1, :-1]
        chi2, p_value, dof, expected = stats.chi2_contingency(observed)
        significant = '是' if p_value < 0.05 else '否'
    except Exception as e:
        p_value = np.nan
        significant = '无法计算'
        chi2 = np.nan
        dof = np.nan
        print(f"变量{var}的卡方检验出错：{e}")
    
    return {
        '频数与比例': prop_table,
        '卡方值': chi2,
        '自由度': dof,
        'p值': p_value,
        '差异显著': significant
    }

# 处理所有分类变量
cat_results = {}
for var in categorical_vars:
    cat_results[var] = analyze_categorical(var)

# ----------------------输出结果----------------------
print("\n" + "="*50)
print("定量变量描述性统计及组间差异检验结果")
print("="*50)

# 创建定量变量结果表格
quant_table = pd.DataFrame(columns=[
    '变量', '乳腺癌患者_样本量', '乳腺癌患者_中位数', '乳腺癌患者_四分位数范围',
    '体检人群_样本量', '体检人群_中位数', '体检人群_四分位数范围',
    'p值', '差异显著'
])

for i, var in enumerate(quantitative_vars):
    res = quant_results[var]
    quant_table.loc[i] = [
        var,
        res['乳腺癌患者']['样本量'],
        round(res['乳腺癌患者']['中位数'], 2),
        f"{round(res['乳腺癌患者']['下四分位数'], 2)}-{round(res['乳腺癌患者']['上四分位数'], 2)}",
        res['体检人群']['样本量'],
        round(res['体检人群']['中位数'], 2),
        f"{round(res['体检人群']['下四分位数'], 2)}-{round(res['体检人群']['上四分位数'], 2)}",
        round(res['p值'], 4) if not np.isnan(res['p值']) else 'NaN',
        res['差异显著']
    ]

print(quant_table.to_string(index=False))

print("\n" + "="*50)
print("分类变量频数、比例及组间差异检验结果")
print("="*50)

for var in categorical_vars:
    print(f"\n变量：{var}")
    print("-"*40)
    print(cat_results[var]['频数与比例'].to_string())
    print("\n统计检验结果：")
    print(f"卡方值：{round(cat_results[var]['卡方值'], 4) if not np.isnan(cat_results[var]['卡方值']) else 'NaN'}")
    print(f"自由度：{cat_results[var]['自由度'] if not np.isnan(cat_results[var]['自由度']) else 'NaN'}")
    print(f"p值：{round(cat_results[var]['p值'], 4) if not np.isnan(cat_results[var]['p值']) else 'NaN'}")
    print(f"差异显著：{cat_results[var]['差异显著']}")
    print("-"*40)

# 保存结果到Excel
output_dir = os.path.dirname(file_path)
output_file = os.path.join(output_dir, "乳腺癌与体检人群变量统计分析结果.xlsx")

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    quant_table.to_excel(writer, sheet_name='定量变量分析', index=False)
    
    # 为每个分类变量创建单独的工作表
    for var in categorical_vars:
        cat_results[var]['频数与比例'].to_excel(writer, sheet_name=f'{var}_频数比例')
        # 保存检验结果
        test_res = pd.DataFrame({
            '统计量': ['卡方值', '自由度', 'p值', '差异显著'],
            '值': [
                round(cat_results[var]['卡方值'], 4) if not np.isnan(cat_results[var]['卡方值']) else 'NaN',
                cat_results[var]['自由度'] if not np.isnan(cat_results[var]['自由度']) else 'NaN',
                round(cat_results[var]['p值'], 4) if not np.isnan(cat_results[var]['p值']) else 'NaN',
                cat_results[var]['差异显著']
            ]
        })
        test_res.to_excel(writer, sheet_name=f'{var}_检验结果', index=False)

print(f"\n分析结果已保存至：{output_file}")