# config.py
from datetime import datetime

# ---------- 处理参数 ----------
RSSI_THRESHOLD = -80
DEDUP_WINDOW_MINUTES = 5

# ---------- 固定盐值 ----------
SALT = datetime.now().strftime('%Y-%m-%d')

# ---------- AP 与区域映射 ----------
AP_TO_REGION = {
    'AC-40RT:AP1': '食堂一楼',
    'AC-40RT:AP2': '食堂二楼',
    'AC-40RT:AP3': '图书馆二楼',
    'AC-40RT:AP4': '教学楼大厅',
    'AC-40RT:AP5': '自习室',
}

# ---------- 各区域基准容量 ----------
CAPACITY = {
    '食堂一楼': 300,
    '食堂二楼': 250,
    '图书馆二楼': 200,
    '教学楼大厅': 150,
    '自习室': 100,
    '其他区域': 50,
}

# ---------- 输出路径 ----------
OUTPUT_DIR = '.'

# ========== 🆕 新增：调度与模拟配置 ==========
COLLECTION_INTERVAL_MINUTES = 5   # 每隔几分钟采集一次
CHUNK_SIZE = 200                  # 模拟采集时，每次从CSV读取多少行

# ---------- 日志配置 ----------
LOG_LEVEL = 'INFO'                # DEBUG, INFO, WARNING, ERROR
LOG_FILE = 'system.log'           # 日志文件名