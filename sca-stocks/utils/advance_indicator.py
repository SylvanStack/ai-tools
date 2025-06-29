"""
高级指标工具类
提供基于核心指标的应用层函数，完美兼容通达信或同花顺
"""
from utils.indicator_utils import *
import numpy as np
import pandas as pd

# ------------------   1级：应用层函数(通过0级核心函数实现）使用方法请参考通达信--------------------------------
def COUNT(S, N):
    """
    COUNT(CLOSE>O, N):  最近N天满足S_BOO的天数  True的天数
    
    Args:
        S: 条件序列（布尔值）
        N: 统计窗口大小
        
    Returns:
        numpy.ndarray: 满足条件的天数序列
    """
    return SUM(S, N)


def EVERY(S, N):
    """
    EVERY(CLOSE>O, 5)   最近N天是否都是True
    
    Args:
        S: 条件序列（布尔值）
        N: 判断窗口大小
        
    Returns:
        numpy.ndarray: 布尔序列，表示是否所有天都满足条件
    """
    return IF(SUM(S, N) == N, True, False)


def EXIST(S, N):
    """
    EXIST(CLOSE>3010, N=5)  n日内是否存在一天大于3000点
    
    Args:
        S: 条件序列（布尔值）
        N: 判断窗口大小
        
    Returns:
        numpy.ndarray: 布尔序列，表示窗口内是否存在满足条件的情况
    """
    return IF(SUM(S, N) > 0, True, False)


def FILTER(S, N):
    """
    FILTER函数，S满足条件后，将其后N周期内的数据置为0, FILTER(C==H,5)
    例：FILTER(C==H,5) 涨停后，后5天不再发出信号
    
    Args:
        S: 条件序列（布尔值）
        N: 满足条件后要过滤的周期数
        
    Returns:
        numpy.ndarray: 过滤后的条件序列
    """
    result = S.copy()
    for i in range(len(S)):
        if S[i]:
            # 将后N个周期置为0
            end_idx = min(i + N + 1, len(S))
            result[i+1:end_idx] = 0
    return result


def BARSLAST(S):
    """
    上一次条件成立到当前的周期, BARSLAST(C/REF(C,1)>=1.1) 上一次涨停到今天的天数
    
    Args:
        S: 条件序列（布尔值）
        
    Returns:
        numpy.ndarray: 上一次条件成立到当前的天数序列
    """
    result = np.zeros(len(S))
    last_true_pos = -1
    
    for i in range(len(S)):
        if S[i]:
            last_true_pos = i
            result[i] = 0
        else:
            result[i] = i - last_true_pos if last_true_pos >= 0 else 0
            
    return result


def BARSLASTCOUNT(S):
    """
    统计连续满足S条件的周期数
    BARSLASTCOUNT(CLOSE>OPEN)表示统计连续收阳的周期数
    
    Args:
        S: 条件序列（布尔值）
        
    Returns:
        numpy.ndarray: 连续满足条件的天数序列
    """
    result = np.zeros(len(S))
    
    for i in range(len(S)):
        if S[i]:
            result[i] = result[i-1] + 1 if i > 0 else 1
        else:
            result[i] = 0
            
    return result


def BARSSINCEN(S, N):
    """
    N周期内第一次S条件成立到现在的周期数,N为常量
    
    Args:
        S: 条件序列（布尔值）
        N: 查找窗口大小
        
    Returns:
        numpy.ndarray: 第一次满足条件到现在的周期数序列
    """
    return pd.Series(S).rolling(N).apply(
        lambda x: N - 1 - np.argmax(x) if np.argmax(x) or x[0] else 0,
        raw=True
    ).fillna(0).values.astype(int)


def CROSS(S1, S2):
    """
    判断向上金叉穿越 CROSS(MA(C,5),MA(C,10))  判断向下死叉穿越 CROSS(MA(C,10),MA(C,5))
    不使用0级函数,移植方便
    
    Args:
        S1: 第一个数据序列
        S2: 第二个数据序列
        
    Returns:
        numpy.ndarray: 布尔序列，表示S1是否上穿S2
    """
    # 确保序列长度一致
    min_len = min(len(S1), len(S2))
    s1 = S1[:min_len]
    s2 = S2[:min_len]
    
    # 前一日s1<=s2且当日s1>s2
    result = np.zeros(min_len, dtype=bool)
    result[0] = False
    
    # 从第二个点开始判断
    for i in range(1, min_len):
        result[i] = (s1[i-1] <= s2[i-1]) and (s1[i] > s2[i])
        
    return result


def LONGCROSS(S1, S2, N):
    """
    两条线维持一定周期后交叉,S1在N周期内都小于S2,本周期从S1下方向上穿过S2时返回1,否则返回0
    N=1时等同于CROSS(S1, S2)
    
    Args:
        S1: 第一个数据序列
        S2: 第二个数据序列
        N: 维持的周期数
        
    Returns:
        numpy.ndarray: 布尔序列，表示是否发生长周期交叉
    """
    # 使用condition_last_period判断前N周期内是否都满足S1 < S2
    condition_before = LAST(S1 < S2, N, 1)
    
    # 当前周期S1 > S2
    condition_now = S1 > S2
    
    # 两个条件同时满足
    return np.logical_and(condition_before, condition_now)


def VALUEWHEN(S, X):
    """
    当S条件成立时,取X的当前值,否则取VALUEWHEN的上个成立时的X值
    
    Args:
        S: 条件序列（布尔值）
        X: 值序列
        
    Returns:
        numpy.ndarray: 条件成立时对应的值序列
    """
    # 确保序列长度一致
    min_len = min(len(S), len(X))
    cond = S[:min_len]
    values = X[:min_len]
    
    # 当条件成立时取值，否则为NaN
    temp = np.where(cond, values, np.nan)
    
    # 向前填充NaN值
    return pd.Series(temp).ffill().values


def BETWEEN(S, A, B):
    """
    S处于A和B之间时为真。 包括 A<S<B 或 A>S>B
    
    Args:
        S: 数据序列
        A: 下限值或序列
        B: 上限值或序列
        
    Returns:
        numpy.ndarray: 布尔序列，表示是否在范围内
    """
    # 处理A和B可能是常数的情况
    if not hasattr(A, "__len__"):
        A = np.full_like(S, A)
    if not hasattr(B, "__len__"):
        B = np.full_like(S, B)
    
    # 确保序列长度一致
    min_len = min(len(S), len(A), len(B))
    s = S[:min_len]
    a = A[:min_len]
    b = B[:min_len]
    
    # 判断是否在两者之间（包括上下限可能颠倒的情况）
    return np.logical_or(
        np.logical_and(a < s, s < b),
        np.logical_and(a > s, s > b)
    )


def TOPRANGE(S):
    """
    TOPRANGE(HIGH)表示当前最高价是近多少周期内最高价的最大值
    
    Args:
        S: 数据序列
        
    Returns:
        numpy.ndarray: 周期数序列
    """
    result = np.zeros(len(S))
    
    for i in range(1, len(S)):
        # 从当前位置向前查找，直到找到大于等于当前值的位置
        for j in range(i-1, -1, -1):
            if S[j] >= S[i]:
                break
        result[i] = i - j if j >= 0 else i + 1
        
    return result.astype(int)


def LOWRANGE(S):
    """
    LOWRANGE(LOW)表示当前最低价是近多少周期内最低价的最小值
    
    Args:
        S: 数据序列
        
    Returns:
        numpy.ndarray: 周期数序列
    """
    result = np.zeros(len(S))
    
    for i in range(1, len(S)):
        # 从当前位置向前查找，直到找到小于等于当前值的位置
        for j in range(i-1, -1, -1):
            if S[j] <= S[i]:
                break
        result[i] = i - j if j >= 0 else i + 1
        
    return result.astype(int)


if __name__ == '__main__':
    # 测试数据
    test_series = np.array([1.1, 2.2, 3.3, 2.2, 1.1, 2.2, 3.3, 4.4, 5.5, 6.6])
    test_series2 = np.array([2.0, 2.0, 2.0, 3.0, 3.0, 1.0, 1.0, 2.0, 3.0, 4.0])
    test_condition = np.array([True, False, True, False, True, False, True, True, True, False])
    
    print("=" * 50)
    print("高级指标函数测试用例")
    print("=" * 50)
    
    # 测试COUNT
    print("\n1. COUNT 函数测试:")
    window = 3
    result = COUNT(test_condition, window)
    print(f"COUNT({test_condition}, {window}) = {result}")
    
    # 测试EVERY
    print("\n2. EVERY 函数测试:")
    window = 3
    result = EVERY(test_condition, window)
    print(f"EVERY({test_condition}, {window}) = {result}")
    
    # 测试EXIST
    print("\n3. EXIST 函数测试:")
    window = 3
    result = EXIST(test_condition, window)
    print(f"EXIST({test_condition}, {window}) = {result}")
    
    # 测试FILTER
    print("\n4. FILTER 函数测试:")
    periods = 2
    result = FILTER(test_condition, periods)
    print(f"FILTER({test_condition}, {periods}) = {result}")
    
    # 测试BARSLAST
    print("\n5. BARSLAST 函数测试:")
    result = BARSLAST(test_condition)
    print(f"BARSLAST({test_condition}) = {result}")
    
    # 测试BARSLASTCOUNT
    print("\n6. BARSLASTCOUNT 函数测试:")
    result = BARSLASTCOUNT(test_condition)
    print(f"BARSLASTCOUNT({test_condition}) = {result}")
    
    # 测试BARSSINCEN
    print("\n7. BARSSINCEN 函数测试:")
    window = 5
    result = BARSSINCEN(test_condition, window)
    print(f"BARSSINCEN({test_condition}, {window}) = {result}")
    
    # 测试CROSS
    print("\n8. CROSS 函数测试:")
    result = CROSS(test_series, test_series2)
    print(f"CROSS({test_series}, {test_series2}) = {result}")
    
    # 测试LONGCROSS
    print("\n10. LONGCROSS 函数测试:")
    window = 2
    result = LONGCROSS(test_series, test_series2, window)
    print(f"LONGCROSS({test_series}, {test_series2}, {window}) = {result}")
    
    # 测试VALUEWHEN
    print("\n11. VALUEWHEN 函数测试:")
    result = VALUEWHEN(test_condition, test_series)
    print(f"VALUEWHEN({test_condition}, {test_series}) = {result}")
    
    # 测试BETWEEN
    print("\n12. BETWEEN 函数测试:")
    result = BETWEEN(test_series, 2.0, 4.0)
    print(f"BETWEEN({test_series}, 2.0, 4.0) = {result}")
    
    # 测试TOPRANGE
    print("\n13. TOPRANGE 函数测试:")
    result = TOPRANGE(test_series)
    print(f"TOPRANGE({test_series}) = {result}")
    
    # 测试LOWRANGE
    print("\n14. LOWRANGE 函数测试:")
    result = LOWRANGE(test_series)
    print(f"LOWRANGE({test_series}) = {result}")