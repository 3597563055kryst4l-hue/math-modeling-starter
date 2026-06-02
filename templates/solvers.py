"""
求解器参考 — 按问题类型组织
不是算法名录，是"你的问题属于哪一类 → 可以考虑这些方法"

使用方式：复制代码段到自己脚本中修改，或作为方法选择的参考清单
"""
import numpy as np

# ============================================================
# 场景A：连续决策 + 线性约束
# 可以考虑: LP, MILP, 二次规划
# 涉及整数变量时用 MILP（pulp 或 ortools）
# ============================================================

def solve_lp(c, A_ub, b_ub, A_eq=None, b_eq=None, bounds=None):
    from scipy.optimize import linprog
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                  bounds=bounds, method='highs')
    if not res.success:
        print(f'LP failed: {res.message}')
    return res


# ============================================================
# 场景B：离散决策 + 组合优化（路径、排班、调度）
# 可选: DP, 整数规划(MIP), 遗传算法, 模拟退火
# 提示：DP适合"多阶段决策，每步状态有限"的问题
#       规模大时遗传/退火可以接受近似解
# ============================================================

def solve_dp_example(stages, states_per_stage, transition_cost):
    n_states = states_per_stage
    dp = np.full((stages, n_states), np.inf)
    dp[0] = 0
    prev = np.zeros((stages, n_states), dtype=int)

    for stage in range(1, stages):
        for s in range(n_states):
            for t in range(n_states):
                val = dp[stage-1, t] + transition_cost[t, s]
                if val < dp[stage, s]:
                    dp[stage, s] = val
                    prev[stage, s] = t

    best_end = np.argmin(dp[-1])
    return dp[-1, best_end], best_end


# ============================================================
# 场景C：指派/分配问题
# 可选: 匈牙利算法, 整数规划
# ============================================================

def solve_assignment(cost_matrix):
    from scipy.optimize import linear_sum_assignment
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    total = cost_matrix[row_ind, col_ind].sum()
    return total, list(zip(row_ind, col_ind))


# ============================================================
# 场景D：非线性/非凸优化
# 可选: 遗传算法, 模拟退火, scipy.optimize.minimize
# 多目标时考虑 Pareto 前沿
# ============================================================

def solve_ga(fitness_func, init_pop, generations=200, mutate_rate=0.1):
    pop = init_pop[:]
    best_fit = -np.inf
    best_sol = None

    for gen in range(generations):
        fits = [fitness_func(ind) for ind in pop]
        best_idx = np.argmax(fits)
        if fits[best_idx] > best_fit:
            best_fit = fits[best_idx]
            best_sol = pop[best_idx].copy()

        parents = [pop[i] for i in np.argsort(fits)[-len(pop)//2:]]
        children = []
        for i in range(0, len(parents), 2):
            if i+1 < len(parents):
                cut = np.random.randint(1, len(parents[i]))
                c1 = np.concatenate([parents[i][:cut], parents[i+1][cut:]])
                c2 = np.concatenate([parents[i+1][:cut], parents[i][cut:]])
                children.extend([c1, c2])

        for c in children:
            if np.random.random() < mutate_rate:
                idx = np.random.randint(len(c))
                c[idx] = np.random.rand() if isinstance(c[0], float) else np.random.randint(len(c))

        pop = parents + children[:len(pop)-len(parents)]

    return best_sol, best_fit


# ============================================================
# 场景E：多目标优化
# 提示: 加权求和, Pareto前沿, NSGA-II
# ============================================================

def pareto_front(scores):
    n = len(scores)
    is_pareto = np.ones(n, dtype=bool)
    for i in range(n):
        for j in range(n):
            if i != j and np.all(scores[j] <= scores[i]) and np.any(scores[j] < scores[i]):
                is_pareto[i] = False
                break
    return np.where(is_pareto)[0]
