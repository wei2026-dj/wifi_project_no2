# collector.py
import pandas as pd
import time
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)


class CsvReplayCollector:
    """
    从历史CSV文件中分批次读取数据，模拟实时采集。
    每次 fetch() 返回一批新的记录（DataFrame），并将时间戳映射到当前时间。
    """

    def __init__(self, csv_path, chunk_size=200):
        self.csv_path = csv_path
        self.chunk_size = chunk_size
        self.index = 0
        self.df = None
        self.base_time = None  # 用于时间映射的基准
        self._load_data()

    def _load_data(self):
        """加载CSV并预处理"""
        try:
            self.df = pd.read_csv(self.csv_path)
            # 确保有时间列，并转为datetime以便计算偏移
            self.df['_datetime'] = pd.to_datetime(self.df['timestamp'], unit='s')
            # 按时间排序，保证输出顺序
            self.df = self.df.sort_values('_datetime').reset_index(drop=True)

            # 计算基准：数据集的第一个时间点 映射到 “当前时间 - 5分钟”（留点处理余量）
            first_time = self.df['_datetime'].iloc[0]
            self.base_time = datetime.now() - first_time

            logger.info(f"模拟采集器加载完成，总记录数：{len(self.df)}")
        except FileNotFoundError:
            logger.error(f"CSV文件未找到：{self.csv_path}")
            raise
        except Exception as e:
            logger.error(f"加载CSV失败：{e}")
            raise

    def fetch(self):
        """
        模拟一次采集。
        返回: DataFrame (包含 rssi, timestamp, mac, ap_mac)
        如果数据已读完，则从头开始循环（模拟持续采集）。
        """
        if self.df is None or len(self.df) == 0:
            return pd.DataFrame()

        # 如果已经读完，重置索引（循环重放）
        if self.index >= len(self.df):
            logger.info("模拟数据已循环重放，重置到开头")
            self.index = 0
            # 重置基准时间，防止时间跳跃
            first_time = self.df['_datetime'].iloc[0]
            self.base_time = datetime.now() - first_time

        # 取一批数据
        end = min(self.index + self.chunk_size, len(self.df))
        chunk = self.df.iloc[self.index:end].copy()
        self.index = end

        # 🔑 关键步骤：将历史时间戳映射为当前时间
        # 即：新时间戳 = 历史时间 + 基准偏移
        chunk['timestamp'] = chunk['_datetime'].apply(
            lambda dt: (dt + self.base_time).timestamp()
        )

        # 只保留原CSV中必需的列（去掉辅助列）
        result = chunk[['rssi', 'timestamp', 'mac', 'ap_mac']].copy()

        logger.debug(f"采集到 {len(result)} 条记录")
        return result