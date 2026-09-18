# processor.py
import pandas as pd
import hashlib
import logging
from config import RSSI_THRESHOLD, DEDUP_WINDOW_MINUTES, SALT, AP_TO_REGION, CAPACITY

logger = logging.getLogger(__name__)


def anonymize_mac(mac):
    if pd.isna(mac):
        return None
    combined = str(mac) + SALT
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()[:16]


def process_data(df_raw):
    logger.info("开始处理数据...")

    if df_raw.empty:
        logger.warning("输入数据为空，跳过处理")
        return pd.DataFrame()

    # 1. 过滤
    original_len = len(df_raw)
    df = df_raw[df_raw['rssi'] > RSSI_THRESHOLD].copy()
    logger.info(f"RSSI过滤：{original_len} -> {len(df)} 条")

    if df.empty:
        return pd.DataFrame()

    # 2. 时间处理与去重
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
    df = df.sort_values(['mac', 'ap_mac', 'datetime'])
    df['time_diff'] = df.groupby(['mac', 'ap_mac'])['datetime'].diff()
    df['time_diff_min'] = df['time_diff'].dt.total_seconds() / 60

    dedup_before = len(df)
    df_dedup = df[
        (df['time_diff'].isna()) | (df['time_diff_min'] > DEDUP_WINDOW_MINUTES)
        ].copy()
    logger.info(f"5分钟去重：{dedup_before} -> {len(df_dedup)} 条")

    if df_dedup.empty:
        return pd.DataFrame()

    # 3. 脱敏
    df_dedup['匿名ID'] = df_dedup['mac'].apply(anonymize_mac)
    df_dedup.drop(columns=['mac'], inplace=True)

    # 4. 区域统计
    df_dedup['区域'] = df_dedup['ap_mac'].map(AP_TO_REGION).fillna('其他区域')
    region_stats = df_dedup.groupby('区域')['匿名ID'].nunique().reset_index()
    region_stats.columns = ['区域名称', '当前人数']

    # 5. 容量与饱和度
    region_stats['基准容量'] = region_stats['区域名称'].map(CAPACITY).fillna(50)
    region_stats['饱和度(%)'] = (region_stats['当前人数'] / region_stats['基准容量'] * 100).round(1)

    latest_time = df_dedup['datetime'].max()
    region_stats['统计时间'] = latest_time.strftime('%Y-%m-%d %H:%M:%S')

    logger.info(f"处理完成，统计到 {len(region_stats)} 个区域数据")
    return region_stats