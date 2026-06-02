import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler


def read_data(path, sheet=0):
    ext = str(path).lower()
    if ext.endswith('.xlsx') or ext.endswith('.xls'):
        return pd.read_excel(path, sheet_name=sheet)
    elif ext.endswith('.csv'):
        return pd.read_csv(path)
    else:
        raise ValueError(f'unsupported: {path}')


def read_multi_sheet(path):
    return pd.read_excel(path, sheet_name=None)


def data_summary(df):
    print(f'shape: {df.shape}')
    print(f'columns: {list(df.columns)}')
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    print(pd.DataFrame({'missing': missing, 'pct': missing_pct}))
    print(df.describe().round(3))


def normalize(df, columns=None, method='minmax'):
    df = df.copy()
    cols = columns or df.select_dtypes(include=[np.number]).columns.tolist()
    scaler = MinMaxScaler() if method == 'minmax' else StandardScaler()
    df[cols] = scaler.fit_transform(df[cols])
    return df, scaler
