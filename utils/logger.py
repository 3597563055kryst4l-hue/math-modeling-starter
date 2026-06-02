import os
from datetime import datetime

def write_log(topic, content, log_dir='logs'):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    filename = f'{timestamp}_{topic}.md'
    os.makedirs(log_dir, exist_ok=True)
    path = os.path.join(log_dir, filename)

    lines = [
        f'# {topic}',
        '',
        f'## 时间',
        f'{datetime.now().strftime("%Y-%m-%d %H:%M")}',
        '',
        '## 做了什么',
        f'{content.get("做了什么", "")}',
        '',
        '## 为什么这样做',
        f'{content.get("为什么", "")}',
        '',
        '## 结果',
        f'{content.get("结果", "")}',
        '',
        '## 下一步',
        f'{content.get("下一步", "")}',
        '',
        '## 备注',
        f'{content.get("备注", "")}',
        '',
    ]
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    return path
