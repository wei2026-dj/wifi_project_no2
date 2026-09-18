# main.py
import os
import time
import logging
import schedule
from datetime import datetime

from config import COLLECTION_INTERVAL_MINUTES, LOG_LEVEL, LOG_FILE
from collector import CsvReplayCollector
from processor import process_data
from reporter import generate_all_reports

# ---------- 1. 配置日志（同时输出到控制台和文件） ----------
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()  # 控制台也打印
    ]
)
logger = logging.getLogger(__name__)

# ---------- 2. 全局采集器（只需初始化一次） ----------
# 请确保 probe_5ap_800data.csv 和 main.py 在同一目录
try:
    collector = CsvReplayCollector('probe_5ap_800data.csv', chunk_size=200)
except Exception as e:
    logger.critical(f"初始化采集器失败，程序退出：{e}")
    exit(1)


# ---------- 3. 核心流水线函数（带重试） ----------
def run_pipeline():
    """执行一次完整的 采集 -> 处理 -> 报告 流程"""
    logger.info("=" * 50)
    logger.info("开始执行数据流水线...")

    try:
        # 步骤1：采集
        raw_data = collector.fetch()
        if raw_data.empty:
            logger.warning("本次采集无数据，跳过处理。")
            return

        # 步骤2：处理
        stats = process_data(raw_data)
        if stats.empty:
            logger.warning("处理后无有效区域数据，跳过报告生成。")
            return

        # 步骤3：报告
        generate_all_reports(stats)
        logger.info(f"流水线执行成功！统计时间：{stats['统计时间'].iloc[0]}")

    except Exception as e:
        # 捕获任何未被处理的异常，记录日志，但不让程序崩溃
        logger.error(f"流水线执行失败：{e}", exc_info=True)


# ---------- 4. 主程序入口 ----------
if __name__ == "__main__":
    logger.info(f"系统启动，采集间隔：{COLLECTION_INTERVAL_MINUTES} 分钟")

    # 启动时立即运行一次，避免等5分钟才出数据
    run_pipeline()

    # 定时调度
    schedule.every(COLLECTION_INTERVAL_MINUTES).minutes.do(run_pipeline)

    # 无限循环，执行调度任务
    while True:
        schedule.run_pending()
        time.sleep(1)  # 每秒检查一次，避免CPU空转