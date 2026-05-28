import pandas as pd
import numpy as np
import warnings
import time
warnings.filterwarnings('ignore')

# ===================== 核心配置 =====================
FILE_PATH = r"C:\Users\peng\Desktop\BC横断面肾功能\data原始数据文件\无缺失总体检人群（分析用）.xlsx"
OUTPUT_PATH = r"C:\Users\peng\Desktop\肾功能数据描述统计结果_最终版.xlsx"

# 定义变量列表（清理潜在的制表符/空格）
CONTINUOUS_VARS = [
    "年龄", "身高", "体重", "体重指数", "eGFR_2009", "白蛋白", "总胆红素", "直接胆红素",
    "谷酰转移酶", "谷丙转氨酶", "谷草转氨酶", "碱性磷酸酶", "总胆汁酸",
    "乳酸脱氢酶", "白细胞总数", "红细胞", "血红蛋白", "血小板", "红细胞比容",
    "总胆固醇", "甘油三脂", "高密度脂蛋白", "低密度脂蛋白", "载脂蛋白A",
    "载脂蛋白B", "脂蛋白α", "超敏C反应蛋白", "血糖", "尿素", "肌酐1",
    "尿酸", "钙", "白蛋白校正钙", "镁", "磷", "钙磷乘积"
]

CATEGORICAL_VARS = [
    "性别", "RI2009_5分级", "RI2009_3分级", "RI2009_2分级1", 
    "RI2009_2分级2", "尿白细胞", "尿蛋白定性", "尿葡萄糖"
]

# 定义需要识别为缺失值的特殊字符（覆盖体检数据常见异常值）
NA_VALUES = ['', ' ', 'NA', 'N/A', '无', '-', '#', '※', '—', 'NaN', 'nan', '不详', '未知']

# ===================== 工具函数 =====================
def print_progress(msg):
    """带时间戳的进度提示"""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def clean_column_names(df):
    """清理列名：去除空格、制表符、换行符、全角空格"""
    df.columns = (df.columns.str.strip()
                  .str.replace('\t', '')
                  .str.replace('\n', '')
                  .str.replace(' ', '')
                  .str.replace('　', ''))  # 全角空格
    return df

def safe_convert_numeric(series):
    """安全转换为数值型：仅将当前列的特殊字符设为NaN（不影响其他列）"""
    # 先替换特殊字符为NaN
    series = series.replace(NA_VALUES, np.nan)
    # 强制转换为数值型，无法转换的设为NaN
    return pd.to_numeric(series, errors='coerce')

def get_effective_vars(df, var_list):
    """获取数据中实际存在的变量（匹配清理后的列名）"""
    clean_var_list = [var.strip().replace(' ', '').replace('\t', '') for var in var_list]
    effective_vars = [var for var in clean_var_list if var in df.columns]
    return effective_vars

# ===================== 数据读取与预处理 =====================
print_progress("开始读取原始数据（保留所有行，仅标记缺失值）...")
# 第一步：读取原始数据（全部按object读取，避免类型冲突）
df = pd.read_excel(
    FILE_PATH,
    engine='openpyxl',
    sheet_name=0,
    na_values=NA_VALUES,
    dtype=object  # 先按字符串读取，后续逐列转换
)

# 清理列名（关键：统一列名格式，解决eGFR_2009后制表符问题）
df = clean_column_names(df)
total_raw_samples = len(df)
print_progress(f"原始数据读取完成，总样本量：{total_raw_samples}")

# 获取有效变量列表（仅保留数据中存在的列）
CONTINUOUS_VARS_EFFECTIVE = get_effective_vars(df, CONTINUOUS_VARS)
CATEGORICAL_VARS_EFFECTIVE = get_effective_vars(df, CATEGORICAL_VARS)

print_progress(f"有效连续变量（{len(CONTINUOUS_VARS_EFFECTIVE)}个）：{CONTINUOUS_VARS_EFFECTIVE}")
print_progress(f"有效分类变量（{len(CATEGORICAL_VARS_EFFECTIVE)}个）：{CATEGORICAL_VARS_EFFECTIVE}")

# ===================== 逐列清洗数据（核心：仅处理当前列缺失值，不删行） =====================
print_progress("开始逐列清洗数据（仅标记当前列缺失值，保留其他列数据）...")

# 1. 清洗连续变量：逐列转换为数值型，仅标记当前列缺失值
for var in CONTINUOUS_VARS_EFFECTIVE:
    df[var] = safe_convert_numeric(df[var])
    # 统计当前列缺失值
    col_missing = df[var].isnull().sum()
    col_valid = total_raw_samples - col_missing
    print_progress(f"  连续变量【{var}】：有效数据{col_valid}个（缺失{col_missing}个，{col_missing/total_raw_samples*100:.2f}%）")

# 2. 清洗分类变量：逐列处理，仅标记当前列缺失值
for var in CATEGORICAL_VARS_EFFECTIVE:
    # 转换为字符串并清理空格
    df[var] = df[var].astype(str).str.strip()
    # 标记特殊字符为缺失值（仅当前列）
    df[var] = df[var].replace(NA_VALUES, np.nan)
    # 统计当前列缺失值
    col_missing = df[var].isnull().sum()
    col_valid = total_raw_samples - col_missing
    print_progress(f"  分类变量【{var}】：有效数据{col_valid}个（缺失{col_missing}个，{col_missing/total_raw_samples*100:.2f}%）")

# 3. 清洗性别列（单独处理，确保分组准确）
df['性别'] = df['性别'].replace(['男', '男性'], '男')
df['性别'] = df['性别'].replace(['女', '女性'], '女')
df['性别'] = df['性别'].replace(NA_VALUES, np.nan)

# 按性别分组（仅过滤性别列缺失值，保留其他列所有数据）
df_male = df[df['性别'] == '男'].copy().reset_index(drop=True)
df_female = df[df['性别'] == '女'].copy().reset_index(drop=True)
df_total = df[df['性别'].isin(['男', '女'])].copy().reset_index(drop=True)

print_progress(f"\n性别分组完成（仅过滤性别列缺失值）：")
print_progress(f"  总人群有效样本（性别非缺失）：{len(df_total)}")
print_progress(f"  男性人群：{len(df_male)}（{len(df_male)/len(df_total)*100:.2f}%）")
print_progress(f"  女性人群：{len(df_female)}（{len(df_female)/len(df_total)*100:.2f}%）")
print_progress(f"  性别列缺失：{total_raw_samples - len(df_total)}")

# ===================== 连续变量描述统计（核心：仅忽略本项目缺失值） =====================
def describe_continuous_by_col(data, var_list, group_name):
    """
    连续变量描述统计（仅忽略当前变量的缺失值，不影响其他变量）
    输出格式：中位数（下四分位数，上四分位数）
    """
    print_progress(f"\n生成{group_name}连续变量统计（仅忽略本项目缺失值）...")
    # 初始化结果字典
    result_dict = {
        '变量': [],
        '本项目有效样本量': [],
        '中位数': [],
        '下四分位数(Q1)': [],
        '上四分位数(Q3)': [],
        '中位数（Q1, Q3）': [],
        '最小值': [],
        '最大值': []
    }
    
    for var in var_list:
        # 仅提取当前变量的非缺失值（核心：只忽略本项目缺失，不删行）
        var_valid_data = data[var].dropna()
        var_valid_count = len(var_valid_data)
        
        if var_valid_count == 0:
            print_progress(f"  【{var}】：无有效数据")
            # 填充空值
            result_dict['变量'].append(var)
            result_dict['本项目有效样本量'].append(0)
            result_dict['中位数'].append(np.nan)
            result_dict['下四分位数(Q1)'].append(np.nan)
            result_dict['上四分位数(Q3)'].append(np.nan)
            result_dict['中位数（Q1, Q3）'].append('无有效数据')
            result_dict['最小值'].append(np.nan)
            result_dict['最大值'].append(np.nan)
            continue
        
        # 计算当前变量的分位数（仅基于本变量有效数据）
        q0 = var_valid_data.min()
        q25 = var_valid_data.quantile(0.25)
        q50 = var_valid_data.median()
        q75 = var_valid_data.quantile(0.75)
        q100 = var_valid_data.max()
        
        # 保留2位小数
        q0, q25, q50, q75, q100 = [round(x, 2) for x in [q0, q25, q50, q75, q100]]
        
        # 填充结果
        result_dict['变量'].append(var)
        result_dict['本项目有效样本量'].append(var_valid_count)
        result_dict['中位数'].append(q50)
        result_dict['下四分位数(Q1)'].append(q25)
        result_dict['上四分位数(Q3)'].append(q75)
        result_dict['中位数（Q1, Q3）'].append(f"{q50}（{q25}, {q75}）")
        result_dict['最小值'].append(q0)
        result_dict['最大值'].append(q100)
        
        print_progress(f"  【{var}】：有效样本{var_valid_count}个 | 中位数（Q1, Q3）：{q50}（{q25}, {q75}）")
    
    # 转换为DataFrame
    result_df = pd.DataFrame(result_dict)
    # 控制台输出核心结果
    print(f"\n=== {group_name} 连续变量核心统计（仅忽略本项目缺失值）===")
    print(result_df[['变量', '本项目有效样本量', '中位数（Q1, Q3）']].to_string(index=False))
    return result_df

# 生成各人群连续变量统计（仅忽略本项目缺失值）
desc_total_cont = describe_continuous_by_col(df_total, CONTINUOUS_VARS_EFFECTIVE, "总人群")
desc_male_cont = describe_continuous_by_col(df_male, CONTINUOUS_VARS_EFFECTIVE, "男性人群")
desc_female_cont = describe_continuous_by_col(df_female, CONTINUOUS_VARS_EFFECTIVE, "女性人群")

# ===================== 分类变量描述统计（核心：仅忽略本项目缺失值） =====================
def describe_categorical_by_col(data, var_list, group_name):
    """
    分类变量构成比统计（仅忽略当前变量的缺失值，不影响其他变量）
    """
    print_progress(f"\n生成{group_name}分类变量统计（仅忽略本项目缺失值）...")
    result_list = []
    print(f"\n=== {group_name} 分类变量构成比（仅忽略本项目缺失值）===")
    
    for var in var_list:
        # 仅提取当前分类变量的非缺失值（核心：只忽略本项目缺失）
        var_valid_data = data[var].dropna()
        var_valid_count = len(var_valid_data)
        
        if var_valid_count == 0:
            print(f"  【{var}】：无有效数据")
            continue
        
        # 计算当前分类变量的频数和构成比（仅基于本变量有效数据）
        freq = var_valid_data.value_counts().sort_index()
        freq_pct = (freq / var_valid_count * 100).round(2)
        
        # 控制台输出
        print(f"\n  【{var}】（本项目有效样本：{var_valid_count}）：")
        for cat, count in freq.items():
            print(f"    {cat}：{count} 例（{freq_pct[cat]}%）")
        
        # 存储结果
        temp_df = pd.DataFrame({
            '变量': [var]*len(freq),
            '类别': freq.index,
            '本项目有效频数': freq.values,
            '构成比(%)': freq_pct.values,
            '本项目总有效样本量': [var_valid_count]*len(freq)
        })
        result_list.append(temp_df)
    
    # 合并结果
    if result_list:
        result_df = pd.concat(result_list, ignore_index=True)
    else:
        result_df = pd.DataFrame()
    
    return result_df

# 生成各人群分类变量统计（仅忽略本项目缺失值）
desc_total_cat = describe_categorical_by_col(df_total, CATEGORICAL_VARS_EFFECTIVE, "总人群")
desc_male_cat = describe_categorical_by_col(df_male, CATEGORICAL_VARS_EFFECTIVE, "男性人群")
desc_female_cat = describe_categorical_by_col(df_female, CATEGORICAL_VARS_EFFECTIVE, "女性人群")

# ===================== 结果导出（结构化Excel） =====================
print_progress("\n开始导出结果到Excel文件...")
try:
    with pd.ExcelWriter(OUTPUT_PATH, engine='openpyxl') as writer:
        # 连续变量结果（核心：本项目有效样本量）
        desc_total_cont.to_excel(writer, sheet_name='总人群_连续变量', index=False)
        desc_male_cont.to_excel(writer, sheet_name='男性_连续变量', index=False)
        desc_female_cont.to_excel(writer, sheet_name='女性_连续变量', index=False)
        
        # 分类变量结果
        if not desc_total_cat.empty:
            desc_total_cat.to_excel(writer, sheet_name='总人群_分类变量', index=False)
        if not desc_male_cat.empty:
            desc_male_cat.to_excel(writer, sheet_name='男性_分类变量', index=False)
        if not desc_female_cat.empty:
            desc_female_cat.to_excel(writer, sheet_name='女性_分类变量', index=False)
    
    print_progress(f"✅ 结果导出成功！文件路径：{OUTPUT_PATH}")
except Exception as e:
    print_progress(f"❌ 结果导出失败：{str(e)}")

# ===================== 最终汇总报告 =====================
print("\n" + "="*80)
print("🔍 最终统计汇总报告（仅忽略本项目缺失值）")
print("="*80)
print(f"原始数据总样本量：{total_raw_samples}")
print(f"总人群有效样本（性别非缺失）：{len(df_total)}")
print(f"  - 男性：{len(df_male)} 例（{len(df_male)/len(df_total)*100:.2f}%）")
print(f"  - 女性：{len(df_female)} 例（{len(df_female)/len(df_total)*100:.2f}%）")
print(f"\n连续变量统计：")
for group, data in [("总人群", desc_total_cont), ("男性", desc_male_cont), ("女性", desc_female_cont)]:
    if not data.empty:
        avg_valid = data['本项目有效样本量'].mean()
        print(f"  {group}：平均每个变量有效样本 {avg_valid:.0f} 个")
print(f"\n分类变量统计：")
for group, data in [("总人群", desc_total_cat), ("男性", desc_male_cat), ("女性", desc_female_cat)]:
    if not data.empty:
        vars_count = data['变量'].nunique()
        print(f"  {group}：统计 {vars_count} 个分类变量")
print("="*80)
print_progress("🎉 所有分析完成！")