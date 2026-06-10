"""
日志工具 — 两层设计：

Layer 1: write_log()
    写 markdown 格式日志到 logs/，给 CLAUDE.md 工作流使用。
    每一小步一个文件，结构固定（做了什么 / 为什么 / 结果 / 下一步 / 备注）。

Layer 2: setup_logger()
    基于 Python logging 模块的实时日志，同时输出到控制台和文件。
    用于跟踪代码执行过程，方便调试。
"""
import os
import logging
import sys
from datetime import datetime
from pathlib import Path


# ── Layer 1: Markdown 日志（给 CLAUDE.md 工作流） ──────────────────

def write_log(topic, content, log_dir='logs'):
    """写一份 markdown 日志到 logs/ 目录。

    Args:
        topic: 日志主题（会作为文件名的一部分）
        content: dict，支持键：做了什么、为什么、结果、下一步、备注
                 也可以传字符串，会全部填入"做了什么"字段
        log_dir: 日志目录，默认 logs/

    Returns:
        写入的文件路径
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    safe_topic = topic.replace('/', '_').replace('\\', '_')
    filename = f'{timestamp}_{safe_topic}.md'

    os.makedirs(log_dir, exist_ok=True)
    path = os.path.join(log_dir, filename)

    if isinstance(content, str):
        content = {'做了什么': content}

    lines = [
        f'# {topic}',
        '',
        '## 时间',
        datetime.now().strftime('%Y-%m-%d %H:%M'),
        '',
        '## 做了什么',
        content.get('做了什么', ''),
        '',
        '## 为什么这样做',
        content.get('为什么', ''),
        '',
        '## 结果',
        content.get('结果', ''),
        '',
        '## 下一步',
        content.get('下一步', ''),
        '',
        '## 备注',
        content.get('备注', ''),
        '',
    ]
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    return path


# ── Layer 2: Python logging 实时日志 ──────────────────

_LOG_FORMAT = '%(asctime)s | %(levelname)-5s | %(message)s'
_LOG_DATE_FORMAT = '%H:%M:%S'


def setup_logger(name='modeling', log_dir='logs', level=logging.INFO):
    """配置 logger，同时输出到控制台和文件。

    Args:
        name: logger 名称
        log_dir: 日志文件目录
        level: 日志级别，默认 INFO

    Returns:
        配置好的 logger 实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 控制台 handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_LOG_DATE_FORMAT))
    logger.addHandler(console)

    # 文件 handler（按天轮转，保留 7 天）
    os.makedirs(log_dir, exist_ok=True)
    log_file = Path(log_dir) / f'{name}.log'
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s | %(levelname)-5s | %(filename)s:%(lineno)d | %(message)s'
    ))
    logger.addHandler(file_handler)

    return logger