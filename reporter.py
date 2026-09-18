# reporter.py
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import os
import logging
from config import OUTPUT_DIR

logger = logging.getLogger(__name__)

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei', 'Arial Unicode MS']
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
    plt.title(f'各区域当前人数统计 (更新于 {latest_time})')
    plt.ylabel('人数')

    max_cap = region_stats['基准容量'].max()
    if max_cap == 0:
        max_cap = region_stats['当前人数'].max() + 10
    plt.ylim(0, max_cap * 1.1)

    for bar, num in zip(bars, region_stats['当前人数']):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                 str(num), ha='center', va='bottom')

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