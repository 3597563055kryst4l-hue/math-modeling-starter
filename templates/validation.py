"""
校验工具 — 结果合理性检查 + 交叉验证辅助

使用方式：在 verify.py 中调用，确保输出在合理范围内
"""
import numpy as np


def sanity_check(val, name='value', expected_range=None, non_negative=True):
    """
    数值合理性检查
    expected_range: (min, max) 或 None
    non_negative: 是否应非负
    """
    issues = []
    if np.isnan(val) or np.isinf(val):
        issues.append(f'{name} is NaN or Inf')
    if non_negative and val < 0:
        issues.append(f'{name} < 0 ({val})')
    if expected_range and (val < expected_range[0] or val > expected_range[1]):
        issues.append(f'{name}={val} out of range {expected_range}')

    if issues:
        print(f'[WARN] {"; ".join(issues)}')
    else:
        print(f'[OK] {name} = {val}')
    return len(issues) == 0


def power_balance(supply, demand, tolerance=1e-6):
    """
    功率平衡检查：supply 应 ≈ demand（逐时刻）
    """
    diff = np.array(supply) - np.array(demand)
    max_diff = np.max(np.abs(diff))
    if max_diff > tolerance:
        print(f'[WARN] power imbalance: max |diff| = {max_diff:.4f}')
    else:
        print(f'[OK] power balanced, max |diff| = {max_diff:.2e}')
    return max_diff


def cross_validate(results_dict, metric='value'):
    """
    简单交叉验证：多个求解器/方法对同一问题的结果对比
    results_dict: {'method_A': val_A, 'method_B': val_B, ...}
    返回均值、标准差、最大偏差百分比
    """
    vals = np.array(list(results_dict.values()))
    mean_val = np.mean(vals)
    std_val = np.std(vals)
    max_dev = np.max(np.abs(vals - mean_val)) / abs(mean_val) * 100 if mean_val != 0 else 0

    print(f'Cross-validation ({len(vals)} methods):')
    for name, val in results_dict.items():
        dev = abs(val - mean_val) / abs(mean_val) * 100 if mean_val != 0 else 0
        print(f'  {name}: {val:.4f} (dev: {dev:.2f}%)')
    print(f'  mean={mean_val:.4f}, std={std_val:.4f}, max_dev={max_dev:.2f}%')

    if max_dev > 10:
        print(f'  [WARN] max deviation > 10%, methods inconsistent!')
    else:
        print(f'  [OK] results agree within {max_dev:.2f}%')

    return {'mean': mean_val, 'std': std_val, 'max_dev_pct': max_dev}
