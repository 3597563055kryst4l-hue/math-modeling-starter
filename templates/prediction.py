"""
预测参考 — 按场景组织的"怎么调"参考
不是封装好的黑箱，是可复用的调用片段

使用方式：复制代码段到自己的脚本中修改参数
"""
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge


# ============================================================
# 场景A：传统机器学习预测
# 可选: RF, XGBoost, LightGBM, Ridge, SVR
# 小样本(<1000)建议RF或Ridge，大样本用XGB/LGB
# ============================================================

def train_sklearn(X_train, y_train, X_test, model_type='rf'):
    if model_type == 'rf':
        model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
    elif model_type == 'ridge':
        model = Ridge(alpha=1.0)
    elif model_type == 'xgb':
        from xgboost import XGBRegressor
        model = XGBRegressor(n_estimators=200, random_state=42, n_jobs=-1)
    elif model_type == 'lgb':
        from lightgbm import LGBMRegressor
        model = LGBMRegressor(n_estimators=200, random_state=42, n_jobs=-1, verbose=-1)
    else:
        raise ValueError(f'unknown model: {model_type}')

    model.fit(X_train, y_train)
    return model.predict(X_test), model


# ============================================================
# 场景B：时间序列预测（无外部特征）
# 可选: ARIMA/SARIMA, LSTM, Prophet
# 短序列(<100点)用ARIMA，长序列考虑LSTM
# ============================================================

def train_arima(train_data, test_len, order=(1, 1, 1)):
    from statsmodels.tsa.arima.model import ARIMA
    model = ARIMA(train_data, order=order)
    fitted = model.fit(disp=False)
    return fitted.forecast(steps=test_len), fitted


def train_lstm(data, seq_len=24, epochs=50):
    """LSTM 时间序列预测参考实现。

    返回 (y_pred, y_true, model, scaler)，其中 y_pred/y_true 是逆变换后的原始尺度值。
    使用方式：
        pred, actual, model, scaler = train_lstm(data)
        # 预测未来 n 步：
        last_seq = data[-seq_len:]
        last_scaled = scaler.transform(np.array(last_seq).reshape(-1, 1)).flatten()
        future = []
        for _ in range(n):
            x = torch.FloatTensor(last_scaled[-seq_len:]).unsqueeze(0).unsqueeze(-1)
            p = model(x).item()
            future.append(p)
            last_scaled = np.append(last_scaled, p)
        future = scaler.inverse_transform(np.array(future).reshape(-1, 1))
    """
    import torch
    import torch.nn as nn
    from sklearn.preprocessing import MinMaxScaler

    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(np.array(data).reshape(-1, 1)).flatten()

    X, y = [], []
    for i in range(len(data_scaled) - seq_len):
        X.append(data_scaled[i:i+seq_len])
        y.append(data_scaled[i+seq_len])
    X = torch.FloatTensor(np.array(X)).unsqueeze(-1)
    y_true = torch.FloatTensor(np.array(y)).unsqueeze(-1)

    class LSTMModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.lstm = nn.LSTM(1, 64, 2, batch_first=True, dropout=0.2)
            self.fc = nn.Linear(64, 1)
        def forward(self, x):
            out, _ = self.lstm(x)
            return self.fc(out[:, -1, :])

    model = LSTMModel()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss()

    for epoch in range(epochs):
        optimizer.zero_grad()
        loss = criterion(model(X), y_true)
        loss.backward()
        optimizer.step()

    # 训练完成后在训练集上预测，逆变换回原始尺度
    with torch.no_grad():
        y_pred_scaled = model(X).numpy().flatten()
    y_pred = scaler.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
    y_true_orig = scaler.inverse_transform(y_true.numpy().reshape(-1, 1)).flatten()
    return y_pred, y_true_orig, model, scaler


# ============================================================
# 场景C：多模型对比（自动选出当前最优）
# ============================================================

def compare_models(X_train, y_train, X_test, y_test):
    from sklearn.metrics import mean_squared_error, r2_score
    models = {
        'RF': RandomForestRegressor(n_estimators=100, random_state=42),
        'Ridge': Ridge(alpha=1.0),
    }
    try:
        from xgboost import XGBRegressor
        models['XGB'] = XGBRegressor(n_estimators=100, random_state=42)
    except ImportError:
        pass

    results = []
    for name, model in models.items():
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        results.append({'model': name, 'RMSE': np.sqrt(mean_squared_error(y_test, pred)),
                        'R2': r2_score(y_test, pred)})

    import pandas as pd
    df = pd.DataFrame(results).sort_values('RMSE')
    print(df.to_string(index=False))
    return df
