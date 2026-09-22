# reporter.py
import matplotlib
import matplotlib.font_manager as font_manager   # 后加入
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import os
import logging
from config import OUTPUT_DIR

logger = logging.getLogger(__name__)
# —— 用项目内的字体文件，跨平台稳定 ——
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, 'fonts', 'simhei.ttf')

if os.path.exists(FONT_PATH):
    ZH_FONT = font_manager.FontProperties(fname=FONT_PATH)
    plt.rcParams['font.sans-serif'] = [ZH_FONT.get_name()]
    logger.info(f"使用项目字体: {FONT_PATH}")
else:
    # 兜底：按系统字体名
    ZH_FONT = font_manager.FontProperties(
        family=['SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei']
    )
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei']
    logger.warning("未找到项目字体文件，回退到系统字体")

plt.rcParams['axes.unicode_minus'] = False


def generate_all_reports(region_stats):
    if region_stats.empty:
        logger.warning("统计数据为空，无法生成报告。")
        return

    # 1. CSV
    csv_path = os.path.join(OUTPUT_DIR, '人流统计结果.csv')
    region_stats.to_csv(csv_path, index=False, encoding='utf-8-sig')
    logger.info(f"统计CSV已保存：{csv_path}")

    # 2. 柱状图
    plt.figure(figsize=(10, 6))
    bars = plt.bar(
        region_stats['区域名称'],
        region_stats['当前人数'],
        color=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffb6c1']
    )
    latest_time = region_stats['统计时间'].iloc[0]

    # 关键：所有中文元素都加 fontproperties=ZH_FONT
    plt.title(f'各区域当前人数统计 (更新于 {latest_time})', fontproperties=ZH_FONT)
    plt.ylabel('人数', fontproperties=ZH_FONT)
    plt.xticks(fontproperties=ZH_FONT)   # 区域名称是中文，必须指定

    # 修复 y 轴范围，避免柱子看不见
    ymax = max(
        region_stats['当前人数'].max(),
        region_stats['基准容量'].max(),
        10
    ) * 1.15
    plt.ylim(0, ymax)

    for bar, num in zip(bars, region_stats['当前人数']):
        plt.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + ymax * 0.01,
                 str(num), ha='center', va='bottom',
                 fontproperties=ZH_FONT)

    plt.tight_layout()
    chart_path = os.path.join(OUTPUT_DIR, 'crowd_chart.png')
    plt.savefig(chart_path)
    plt.close()
    logger.info(f"柱状图已保存：{chart_path}")

    # 3. HTML
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="300"> <!-- 浏览器每5分钟自动刷新 -->
    <title>校园人流密度引导屏</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', sans-serif; margin: 40px; }}
        table {{ border-collapse: collapse; width: 60%; }}
        td, th {{ border: 1px solid #ddd; padding: 12px; text-align: center; }}
        th {{ background: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>📊 校园公共区域人流密度实时看板</h1>
    <p><b>统计时间：</b>{latest_time}</p>
    <img src="crowd_chart.png" alt="人流柱状图" style="width:70%;">
    <h2>📋 详细区域数据</h2>
    <table>
        <tr><th>区域名称</th><th>当前人数</th><th>基准容量</th><th>饱和度</th><th>引导建议</th></tr>
    """
    for _, row in region_stats.iterrows():
        sat = row['饱和度(%)']
        if sat < 60:
            advice = "✅ 空闲"
        elif sat < 80:
            advice = "⚠️ 较忙"
        else:
            advice = "🚫 拥挤"
        html_content += f"""
        <tr><td>{row['区域名称']}</td><td>{row['当前人数']}</td><td>{row['基准容量']}</td><td>{sat}%</td><td>{advice}</td></tr>
        """
    html_content += "</table></body></html>"

    html_path = os.path.join(OUTPUT_DIR, '人流引导报告.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    logger.info(f"引导报告已生成：{html_path}")