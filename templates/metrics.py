import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


def rmse(y_true, y_pred):
    return np.sqrt(mean_squared_error(y_true, y_pred))


def mae(y_true, y_pred):
    return mean_absolute_error(y_true, y_pred)


def mape(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100


def r2(y_true, y_pred):
    return r2_score(y_true, y_pred)


def regression_report(y_true, y_pred, name='model'):
    results = {
        'RMSE': rmse(y_true, y_pred),
        'MAE': mae(y_true, y_pred),
        'MAPE(%)': mape(y_true, y_pred),
        'R²': r2(y_true, y_pred)
    }
    print(f'{name}:')
    for k, v in results.items():
        print(f'  {k}: {v:.4f}')
    return results


def compare_models(y_true, pred_dict):
    import pandas as pd
    records = []
    for name, y_pred in pred_dict.items():
        records.append({
            'model': name,
            'RMSE': rmse(y_true, y_pred),
            'MAE': mae(y_true, y_pred),
            'R²': r2(y_true, y_pred)
        })
    df = pd.DataFrame(records)
    print(df.to_string(index=False))
    return df
