import os
import json
import yaml
import pandas as pd

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path

def read_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in ('.xlsx', '.xls'):
        return pd.read_excel(path)
    elif ext == '.csv':
        return pd.read_csv(path)
    elif ext == '.json':
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    elif ext in ('.yaml', '.yml'):
        with open(path, encoding='utf-8') as f:
            return yaml.safe_load(f)
    else:
        raise ValueError(f'unsupported format: {ext}')

def save_output(data, path):
    ensure_dir(os.path.dirname(path))
    ext = os.path.splitext(path)[1].lower()
    if ext == '.csv':
        pd.DataFrame(data).to_csv(path, index=False)
    elif ext == '.json':
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    elif ext == '.yaml':
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True)
