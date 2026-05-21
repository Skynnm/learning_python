import pandas as pd

# 读取原始Excel文件
input_path = r"C:\Users\peng\Desktop\BC横断面肾功能\data原始数据文件\无缺失总体检人群.xlsx"
df = pd.read_excel(input_path)

# 筛选出性别为女性的行
female_df = df[df["性别"] == "女"]

# 保存为新的Excel文件
output_path = r"C:\Users\peng\Desktop\BC横断面肾功能\data原始数据文件\2.女性体检研究人群.xlsx"
female_df.to_excel(output_path, index=False)

print(f"已成功生成女性体检研究人群文件，保存路径：{output_path}")