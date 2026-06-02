"""
敏感性分析 — 参数扫描骨架
系统化地扰动参数，观察输出变化
"""
import numpy as np
import matplotlib.pyplot as plt


def scan_param(func, param_name, values, fixed_params=None):
    """
    单参数扫描
    func(param_dict) → float
    param_name: 要扫描的参数名
    values: 参数取值列表
    fixed_params: 固定参数字典

    返回 {param_name: [value, ...], 'output': [result, ...]}
    """
    results = []
    for v in values:
        params = dict(fixed_params or {})
        params[param_name] = v
        results.append(func(params))
    return {param_name: list(values), 'output': results}


def plot_sensitivity(scan_result, xlabel='', ylabel='output', title='', save_path=None):
    keys = [k for k in scan_result if k != 'output']
    fig, axes = plt.subplots(1, len(keys), figsize=(6*len(keys), 4))
    if len(keys) == 1:
        axes = [axes]

    for ax, key in zip(axes, keys):
        ax.plot(scan_result[key], scan_result['output'], 'o-', linewidth=1.5)
        ax.set(xlabel=xlabel or key, ylabel=ylabel, title=title or f'sensitivity: {key}')
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path)
    plt.show()


def perturbation_analysis(func, base_params, perturb_pct=10):
    """
    扰动分析：对每个参数扰动 ±pct%，观察输出变化百分比
    func(param_dict) → float
    base_params: 基准参数
    perturb_pct: 扰动百分比
    """
    base = func(base_params)
    results = {}
    for k, v in base_params.items():
        if v == 0:
            continue
        p = base_params.copy()
        p[k] = v * (1 + perturb_pct / 100)
        high = func(p)
        p[k] = v * (1 - perturb_pct / 100)
        low = func(p)
        results[k] = {
            'base': base,
            'low': low,
            'high': high,
            'delta_pct': max(abs(high-base), abs(low-base)) / abs(base) * 100 if base != 0 else 0,
        }
    return results
