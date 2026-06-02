import matplotlib.pyplot as plt
import matplotlib
import numpy as np


def set_paper_style():
    matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
    matplotlib.rcParams['axes.unicode_minus'] = False
    matplotlib.rcParams['figure.dpi'] = 300
    matplotlib.rcParams['savefig.dpi'] = 300
    matplotlib.rcParams['savefig.bbox'] = 'tight'
    matplotlib.rcParams['axes.spines.top'] = False
    matplotlib.rcParams['axes.spines.right'] = False


COLORS = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#44BBA4']


def plot_lines(x, y_dict, title='', xlabel='', ylabel='', figsize=(10, 5), save_path=None):
    fig, ax = plt.subplots(figsize=figsize)
    for i, (label, y) in enumerate(y_dict.items()):
        ax.plot(x, y, label=label, color=COLORS[i % len(COLORS)], linewidth=1.5)
    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path)
    plt.show()


def plot_bar(categories, values_dict, title='', xlabel='', ylabel='', figsize=(10, 6), save_path=None):
    x = np.arange(len(categories))
    n = len(values_dict)
    width = 0.8 / n
    fig, ax = plt.subplots(figsize=figsize)
    for i, (label, values) in enumerate(values_dict.items()):
        offset = (i - n / 2 + 0.5) * width
        ax.bar(x + offset, values, width, label=label, color=COLORS[i % len(COLORS)])
    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path)
    plt.show()


def plot_heatmap(data, row_labels, col_labels, title='', cmap='YlOrRd', figsize=(10, 8), save_path=None):
    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(data, cmap=cmap, aspect='auto')
    ax.set_xticks(np.arange(len(col_labels)))
    ax.set_yticks(np.arange(len(row_labels)))
    ax.set_xticklabels(col_labels, rotation=45, ha='right')
    ax.set_yticklabels(row_labels)
    for i in range(len(row_labels)):
        for j in range(len(col_labels)):
            ax.text(j, i, f'{data[i][j]:.2f}', ha='center', va='center',
                    fontsize=8, color='white' if data[i][j] > data.mean() else 'black')
    plt.colorbar(im)
    ax.set_title(title)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path)
    plt.show()


def subplots_grid(nrows, ncols, figsize=None):
    if figsize is None:
        figsize = (5 * ncols, 4 * nrows)
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    return fig, axes.flatten()
