import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# -------------------------- 1. 配置绘图环境 --------------------------
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['figure.dpi'] = 120
plt.rcParams['savefig.dpi'] = 300

# -------------------------- 2. 读取数据 --------------------------
file_path = r"C:\Users\peng\Desktop\BC横断面肾功能\匹配后年龄数据.xlsx"
df = pd.read_excel(file_path, engine='openpyxl')
df = df.dropna(subset=['年龄'])

group1 = df[df['group'] == 1]['年龄']  # 乳腺癌人群
group0 = df[df['group'] == 0]['年龄']  # 体检人群

# -------------------------- 3. 强化对比的颜色定义 --------------------------
variables = [
    {
        'data': group0,
        'display_name': '70520名年龄匹配女性体检人群',
        'hist_color': "#C6E2FF",  # 更浅的蓝色（底层）
        'kde_color': "#0059BE",   # 深蓝色线条
        'linestyle': '-',
        'hist_alpha': 0.6,
        'kde_alpha': 1.0,
        'zorder': 1  # 先画，在底层
    },
    {
        'data': group1,
        'display_name': '7052名女性乳腺癌人群',
        'hist_color': "#FF9999",  # 更亮的浅红（上层）
        'kde_color': "#C00000",   # 更深的红色线条
        'linestyle': '-',
        'hist_alpha': 0.8,
        'kde_alpha': 1.0,
        'zorder': 2  # 后画，在上层
    }
]

# -------------------------- 4. 绘制分层核密度图 --------------------------
fig, ax = plt.subplots()

# 先画底层（体检人群），再画上层（乳腺癌人群）
for var in sorted(variables, key=lambda x: x['zorder']):
    data = var['data']
    kde = stats.gaussian_kde(data)
    x_range = np.linspace(df['年龄'].min(), df['年龄'].max(), 300)
    y_kde = kde(x_range)
    
    # 填充面积
    ax.fill_between(
        x_range, y_kde,
        color=var['hist_color'],
        alpha=var['hist_alpha'],
        zorder=var['zorder']
    )
    # 绘制线条
    ax.plot(
        x_range, y_kde,
        color=var['kde_color'],
        linestyle=var['linestyle'],
        linewidth=2.0,  # 加粗线条
        alpha=var['kde_alpha'],
        label=var['display_name'],
        zorder=var['zorder'] + 1
    )

# -------------------------- 5. 图表美化 --------------------------
# 【已调整】标题紧贴图片下方，居中
fig.suptitle(
    '图3.女性乳腺癌人群和按年龄1:10匹配女性体检人群年龄分布核密度图',
    fontsize=15,
    fontweight='bold',
    y=0.09,         # 提高位置，紧贴图片
    x=0.5,
    ha='center'
)

ax.set_xlabel('年龄', fontsize=11, labelpad=10)
ax.set_ylabel('核密度值', fontsize=11, labelpad=10)

# 图例位置调整到右上角，避免遮挡曲线
ax.legend(
    loc='upper right',
    frameon=True,
    fancybox=True,
    shadow=True,
    fontsize=10,
    borderpad=1
)

# 网格与边框
ax.grid(True, linestyle='--', alpha=0.4, color='#DDDDDD')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#333333')
ax.spines['bottom'].set_color('#333333')
ax.tick_params(axis='both', labelsize=10)

# 调整x轴范围，让曲线更舒展
ax.set_xlim(18, 102)

# 【已调整】紧凑布局，不留空白
plt.tight_layout(rect=[0, 0.08, 1, 0.98])

# 保存图片
save_path = r'C:\Users\peng\Desktop\化疗前后肾功能\年龄分布核密度图_高对比版.png'
plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
plt.show()