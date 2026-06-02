import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PATHS = {
    'data_raw': os.path.join(BASE, 'data', 'raw'),
    'data_processed': os.path.join(BASE, 'data', 'processed'),
    'data_external': os.path.join(BASE, 'data', 'external'),
    'problems': os.path.join(BASE, 'problems'),
    'logs': os.path.join(BASE, 'logs'),
    'figures': os.path.join(BASE, 'paper', 'figures'),
}

RANDOM_SEED = 42

def set_plot_style():
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
    matplotlib.rcParams['axes.unicode_minus'] = False
    matplotlib.rcParams['figure.dpi'] = 300
    matplotlib.rcParams['savefig.dpi'] = 300
    matplotlib.rcParams['savefig.bbox'] = 'tight'
    matplotlib.rcParams['axes.spines.top'] = False
    matplotlib.rcParams['axes.spines.right'] = False
