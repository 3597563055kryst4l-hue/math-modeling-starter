"""Quick start demo — 验证环境是否就绪。"""

# 先尝试正常导入（pip install -e . 后生效），失败则用 sys.path 回退
import sys
import os

try:
    import numpy as np
    import pandas as pd
    from config.settings import set_plot_style, RANDOM_SEED
    from templates.data_preprocessing import data_summary
    from templates.metrics import regression_report
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import numpy as np
    import pandas as pd
    from config.settings import set_plot_style, RANDOM_SEED
    from templates.data_preprocessing import data_summary
    from templates.metrics import regression_report

np.random.seed(RANDOM_SEED)
set_plot_style()


def demo():
    df = pd.DataFrame({
        'x': np.linspace(0, 10, 100),
        'y': 2 * np.linspace(0, 10, 100) + np.random.randn(100),
    })
    data_summary(df)

    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    model.fit(df[['x']], df['y'])
    pred = model.predict(df[['x']])

    regression_report(df['y'], pred, 'LinearRegression')
    print('Quick start demo completed.')


if __name__ == '__main__':
    demo()
