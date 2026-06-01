import pandas as pd
import warnings
warnings.filterwarnings('ignore')  # 忽略无关警告

# ---------------------- 核心配置（仅需修改此处路径） ----------------------
# 输入文件路径
INPUT_FILE = r"C:\Users\peng\Desktop\BC横断面肾功能\data原始数据文件\无缺失总体检人群（分析用7）.xlsx"
# 输出结果保存路径
OUTPUT_FILE = r"C:\Users\peng\Desktop\BC横断面肾功能\Cockcroft_aMDRD_四分位数统计_体检人群.xlsx"

# ---------------------- 1. 读取并校验数据 ----------------------
def load_and_validate_data(file_path):
    """读取数据并进行基础校验"""
    try:
        # 读取Excel文件（自动识别第一个sheet，如需指定可加sheet_name参数）
        df = pd.read_excel(file_path)
        print(f"✅ 成功读取数据，共 {len(df)} 行，{len(df.columns)} 列")
        
        # 检查必要列是否存在
        required_cols = ['Cockcroft', 'aMDRD', '性别']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"❌ 数据缺失必要列：{missing_cols}")
        
        # 检查性别取值
        gender_unique = df['性别'].dropna().unique()
        invalid_gender = [g for g in gender_unique if g not in ['男', '女']]
        if invalid_gender:
            raise ValueError(f"❌ 性别列包含非预期值：{invalid_gender}，仅支持'男/女'")
        
        # 去除关键列缺失值（保证统计有效性）
        df_clean = df.dropna(subset=required_cols).copy()
        print(f"✅ 数据清洗完成，有效样本数：{len(df_clean)}（剔除缺失值 {len(df)-len(df_clean)} 行）")
        
        # 输出性别分布
        gender_count = df_clean['性别'].value_counts()
        print(f"📊 性别分布：\n{gender_count}")
        
        return df_clean
    
    except Exception as e:
        print(f"❌ 数据读取/校验失败：{str(e)}")
        raise

# ---------------------- 2. 定义统计计算函数 ----------------------
def get_quantile_stats(data, col_name):
    """
    计算指定列的中位数、下四分位数(Q1)、上四分位数(Q3)
    返回格式：[中位数, Q1, Q3]
    """
    stats = {
        '中位数': data[col_name].median(),
        '下四分位数(Q1)': data[col_name].quantile(0.25),
        '上四分位数(Q3)': data[col_name].quantile(0.75)
    }
    # 保留3位小数，提升精度
    return {k: round(v, 3) for k, v in stats.items()}

# ---------------------- 3. 分组统计主逻辑 ----------------------
def main():
    # 读取并校验数据
    df_clean = load_and_validate_data(INPUT_FILE)
    
    # 定义需要分析的连续变量
    continuous_vars = ['Cockcroft', 'aMDRD']
    
    # 初始化统计结果字典
    all_stats = {}
    
    # 1. 总人群统计
    print("\n" + "="*70)
    print("📈 总人群统计结果")
    print("="*70)
    total_stats = {}
    for var in continuous_vars:
        total_stats[var] = get_quantile_stats(df_clean, var)
        print(f"\n{var}：")
        for stat_name, value in total_stats[var].items():
            print(f"  {stat_name}：{value}")
    all_stats['总人群'] = total_stats
    
    # 2. 男性人群统计
    male_df = df_clean[df_clean['性别'] == '男']
    print("\n" + "="*70)
    print(f"📈 男性人群统计结果（样本数：{len(male_df)}）")
    print("="*70)
    male_stats = {}
    for var in continuous_vars:
        male_stats[var] = get_quantile_stats(male_df, var)
        print(f"\n{var}：")
        for stat_name, value in male_stats[var].items():
            print(f"  {stat_name}：{value}")
    all_stats['男性'] = male_stats
    
    # 3. 女性人群统计
    female_df = df_clean[df_clean['性别'] == '女']
    print("\n" + "="*70)
    print(f"📈 女性人群统计结果（样本数：{len(female_df)}）")
    print("="*70)
    female_stats = {}
    for var in continuous_vars:
        female_stats[var] = get_quantile_stats(female_df, var)
        print(f"\n{var}：")
        for stat_name, value in female_stats[var].items():
            print(f"  {stat_name}：{value}")
    all_stats['女性'] = female_stats
    
    # ---------------------- 4. 结果整理与保存 ----------------------
    # 构建汇总DataFrame
    summary_data = []
    index_names = ['中位数', '下四分位数(Q1)', '上四分位数(Q3)']
    for idx in index_names:
        row = {
            '统计指标': idx,
            '总人群-Cockcroft': all_stats['总人群']['Cockcroft'][idx],
            '总人群-aMDRD': all_stats['总人群']['aMDRD'][idx],
            '男性-Cockcroft': all_stats['男性']['Cockcroft'][idx],
            '男性-aMDRD': all_stats['男性']['aMDRD'][idx],
            '女性-Cockcroft': all_stats['女性']['Cockcroft'][idx],
            '女性-aMDRD': all_stats['女性']['aMDRD'][idx]
        }
        summary_data.append(row)
    
    summary_df = pd.DataFrame(summary_data).set_index('统计指标')
    
    # 保存到Excel
    try:
        summary_df.to_excel(OUTPUT_FILE, sheet_name='四分位数统计')
        print(f"\n✅ 统计结果已保存至：{OUTPUT_FILE}")
    except Exception as e:
        print(f"❌ 结果保存失败：{str(e)}")
    
    # ---------------------- 5. 补充输出 ----------------------
    print("\n" + "="*70)
    print("📋 补充统计信息")
    print("="*70)
    print(f"总人群样本数：{len(df_clean)}")
    print(f"男性样本数：{len(male_df)}（占比：{len(male_df)/len(df_clean)*100:.1f}%）")
    print(f"女性样本数：{len(female_df)}（占比：{len(female_df)/len(df_clean)*100:.1f}%）")
    
    # 输出完整描述性统计
    print("\n📊 Cockcroft 完整描述性统计：")
    print(df_clean['Cockcroft'].describe().round(3))
    print("\n📊 aMDRD 完整描述性统计：")
    print(df_clean['aMDRD'].describe().round(3))

if __name__ == "__main__":
    main()