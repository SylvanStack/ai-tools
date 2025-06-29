"""
核心指标工具类
提供常用的金融和数学计算函数
"""
import numpy as np
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP


# 应用层1级函数完美兼容通达信或同花顺，具体使用方法请参考通达信
# 以下所有函数如无特别说明，输入参数S均为numpy序列或者列表list，N为整型int

def RD(N, D=3):
    """
    四舍五入取3位小数
    """
    return np.round(N, D)


def RET(series, n=1):
    """
    返回序列倒数第N个值，默认返回最后一个
    
    Args:
        series: 输入数据序列
        n: 倒数第n个，默认为1（最后一个）
        
    Returns:
        float: 序列中的倒数第n个值
    """
    return np.array(series)[-n]


def ABS(series):
    """
    返回序列的绝对值
    
    Args:
        series: 输入数据序列
        
    Returns:
        numpy.ndarray: 绝对值序列
    """
    return np.abs(series)


def LN(series):
    """
    求序列的自然对数（底为e）
    
    Args:
        series: 输入数据序列
        
    Returns:
        numpy.ndarray: 自然对数序列
    """
    return np.log(series)


def POW(series, exponent):
    """
    求序列的指数次方
    
    Args:
        series: 输入数据序列
        exponent: 指数
        
    Returns:
        numpy.ndarray: 指数序列
    """
    return np.power(series, exponent)


def SQRT(series):
    """
    求序列的平方根
    
    Args:
        series: 输入数据序列
        
    Returns:
        numpy.ndarray: 平方根序列
    """
    return np.sqrt(series)


def SIN(series):
    """
    求序列的正弦值（弧度）
    
    Args:
        series: 输入数据序列（弧度）
        
    Returns:
        numpy.ndarray: 正弦值序列
    """
    return np.sin(series)


def COS(series):
    """
    求序列的余弦值（弧度）
    
    Args:
        series: 输入数据序列（弧度）
        
    Returns:
        numpy.ndarray: 余弦值序列
    """
    return np.cos(series)


def TAN(series):
    """
    求序列的正切值（弧度）
    
    Args:
        series: 输入数据序列（弧度）
        
    Returns:
        numpy.ndarray: 正切值序列
    """
    return np.tan(series)


def MAX(series1, series2):
    """
    返回两个序列对应位置的较大值
    
    Args:
        series1: 第一个输入数据序列
        series2: 第二个输入数据序列
        
    Returns:
        numpy.ndarray: 较大值序列
    """
    return np.maximum(series1, series2)


def MIN(series1, series2):
    """
    返回两个序列对应位置的较小值
    
    Args:
        series1: 第一个输入数据序列
        series2: 第二个输入数据序列
        
    Returns:
        numpy.ndarray: 较小值序列
    """
    return np.minimum(series1, series2)


def IF(condition, value_if_true, value_if_false):
    """
    序列布尔判断，类似三元运算符
    
    Args:
        condition: 布尔条件序列
        value_if_true: 条件为真时的值序列
        value_if_false: 条件为假时的值序列
        
    Returns:
        numpy.ndarray: 条件选择后的序列
    """
    return np.where(condition, value_if_true, value_if_false)


def REF(series, periods=1):
    """
    对序列整体移动N个周期，向前为正，向后为负
    
    Args:
        series: 输入数据序列
        periods: 移动周期数，默认为1（向后移动1位）
        
    Returns:
        numpy.ndarray: 移动后的序列，移动产生的空位用NaN填充
    """
    return pd.Series(series).shift(periods).values


def DIFF(series, periods=1):
    """
    计算序列的差分（当前值减去n个周期前的值）
    
    Args:
        series: 输入数据序列
        periods: 差分周期数，默认为1
        
    Returns:
        numpy.ndarray: 差分序列，前n个值为NaN
    """
    return pd.Series(series).diff(periods).values


def STD(series, window):
    """
    计算序列的滚动标准差
    
    Args:
        series: 输入数据序列
        window: 计算标准差的窗口大小
        
    Returns:
        numpy.ndarray: 标准差序列，前window-1个值为NaN
    """
    return pd.Series(series).rolling(window).std(ddof=0).values


def SUM(series, window):
    """
    计算序列的滚动求和
    
    Args:
        series: 输入数据序列
        window: 求和的窗口大小，若为0则计算累计和
        
    Returns:
        numpy.ndarray: 滚动求和序列，若window>1则前window-1个值为NaN
    """
    return pd.Series(series).rolling(window).sum().values if window > 0 else pd.Series(series).cumsum().values


def CONST(series):
    """
    返回一个常量序列，值为输入序列的最后一个值
    
    Args:
        series: 输入数据序列
        
    Returns:
        numpy.ndarray: 常量序列
    """
    return np.full(len(series), series[-1])


def HHV(series, window):
    """
    计算序列在窗口期内的最高值
    
    Args:
        series: 输入数据序列
        window: 窗口大小
        
    Returns:
        numpy.ndarray: 窗口内最高值序列，前window-1个值为NaN
    """
    return pd.Series(series).rolling(window).max().values


def LLV(series, window):
    """
    计算序列在窗口期内的最低值
    
    Args:
        series: 输入数据序列
        window: 窗口大小
        
    Returns:
        numpy.ndarray: 窗口内最低值序列，前window-1个值为NaN
    """
    return pd.Series(series).rolling(window).min().values


def HHVBARS(series, window):
    """
    计算窗口内最高值距离当前位置的周期数
    
    Args:
        series: 输入数据序列
        window: 窗口大小
        
    Returns:
        numpy.ndarray: 最高值位置序列，前window-1个值为NaN
    """
    return pd.Series(series).rolling(window).apply(lambda x: np.argmax(x[::-1]), raw=True).values


def LLVBARS(series, window):
    """
    计算窗口内最低值距离当前位置的周期数
    
    Args:
        series: 输入数据序列
        window: 窗口大小
        
    Returns:
        numpy.ndarray: 最低值位置序列，前window-1个值为NaN
    """
    return pd.Series(series).rolling(window).apply(lambda x: np.argmin(x[::-1]), raw=True).values


def MA(series, window):
    """
    计算简单移动平均线
    
    Args:
        series: 输入数据序列
        window: 移动平均的窗口大小
        
    Returns:
        numpy.ndarray: 简单移动平均序列，前window-1个值为NaN
    """
    return pd.Series(series).rolling(window).mean().values


def EMA(series, span):
    """
    计算指数移动平均线
    为了精度，建议series长度大于4*span
    
    Args:
        series: 输入数据序列
        span: 平滑参数，相当于移动平均的窗口大小
        
    Returns:
        numpy.ndarray: 指数移动平均序列
    """
    return pd.Series(series).ewm(span=span, adjust=False).mean().values


def SMA(series, window, weight=1):
    """
    计算平滑移动平均线（中国式SMA）
    为了精度，建议series长度大于120
    
    Args:
        series: 输入数据序列
        window: 移动平均的窗口大小
        weight: 权重因子，默认为1
        
    Returns:
        numpy.ndarray: 平滑移动平均序列
    """
    return pd.Series(series).ewm(alpha=weight / window, adjust=False).mean().values


def WMA(series, window):
    """
    计算加权移动平均线
    权重计算公式：(1*X1+2*X2+3*X3+...+n*Xn)/(1+2+3+...+n)
    
    Args:
        series: 输入数据序列
        window: 移动平均的窗口大小
        
    Returns:
        numpy.ndarray: 加权移动平均序列，前window-1个值为NaN
    """
    return pd.Series(series).rolling(window).apply(
        lambda x: x[::-1].cumsum().sum() * 2 / window / (window + 1),
        raw=True
    ).values


def DMA(series, alpha):
    """
    计算动态移动平均线
    
    Args:
        series: 输入数据序列
        alpha: 平滑因子，可以是常数（0<alpha<1）或序列
        
    Returns:
        numpy.ndarray: 动态移动平均序列
    """
    if isinstance(alpha, (int, float)):
        return pd.Series(series).ewm(alpha=alpha, adjust=False).mean().values

    alpha = np.array(alpha)
    alpha[np.isnan(alpha)] = 1.0
    result = np.zeros(len(series))
    result[0] = series[0]

    for i in range(1, len(series)):
        result[i] = alpha[i] * series[i] + (1 - alpha[i]) * result[i - 1]

    return result


def AVEDEV(series, window):
    """
    计算平均绝对偏差（序列与其平均值的绝对差的平均值）
    
    Args:
        series: 输入数据序列
        window: 计算窗口大小
        
    Returns:
        numpy.ndarray: 平均绝对偏差序列，前window-1个值为NaN
    """
    return pd.Series(series).rolling(window).apply(
        lambda x: (np.abs(x - x.mean())).mean()
    ).values


def SLOPE(series, window):
    """
    计算线性回归斜率
    
    Args:
        series: 输入数据序列
        window: 回归窗口大小
        
    Returns:
        numpy.ndarray: 线性回归斜率序列，前window-1个值为NaN
    """
    return pd.Series(series).rolling(window).apply(
        lambda x: np.polyfit(range(window), x, deg=1)[0],
        raw=True
    ).values


def FORCAST(series, window):
    """
    计算线性回归预测值
    
    Args:
        series: 输入数据序列
        window: 回归窗口大小
        
    Returns:
        numpy.ndarray: 线性回归预测值序列，前window-1个值为NaN
    """
    return pd.Series(series).rolling(window).apply(
        lambda x: np.polyval(np.polyfit(range(window), x, deg=1), window - 1),
        raw=True
    ).values


def LAST(condition_series, start_period, end_period):
    """
    判断从前start_period日到前end_period日是否一直满足条件
    
    Args:
        condition_series: 条件序列（布尔值）
        start_period: 开始周期（必须大于end_period且大于0）
        end_period: 结束周期（必须大于等于0）
        
    Returns:
        numpy.ndarray: 布尔序列，表示是否满足条件
    """
    assert start_period > end_period and start_period > 0 and end_period >= 0, "参数必须满足: start_period > end_period > 0"
    return np.array(
        pd.Series(condition_series).rolling(start_period + 1).apply(
            lambda x: np.all(x[::-1][end_period:]),
            raw=True
        ),
        dtype=bool
    )


if __name__ == '__main__':
    # 创建测试数据
    test_series = np.array([1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 10.0])
    test_series2 = np.array([0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5])
    test_condition = np.array([True, False, True, False, True, False, True, False, True, False])

    print("=" * 50)
    print("函数测试用例")
    print("=" * 50)

    # round_number 测试
    print("\n1. round_number 函数测试:")
    print(f"round_number(1.2345, 3) = {RD(1.2345, 3)}")  # 应为1.235
    print(f"round_number(1.5, 0) = {RD(1.5, 0)}")  # 应为2.0
    print(f"round_number(2.5, 0) = {RD(2.5, 0)}")  # 应为3.0

    # get_last_value 测试
    print("\n2. get_last_value 函数测试:")
    print(f"get_last_value({test_series}) = {RET(test_series)}")  # 应为10.0
    print(f"get_last_value({test_series}, 3) = {RET(test_series, 3)}")  # 应为8.8

    # absolute_value 测试
    print("\n3. absolute_value 函数测试:")
    neg_series = np.array([-1.1, 2.2, -3.3, 4.4, -5.5])
    print(f"absolute_value({neg_series}) = {ABS(neg_series)}")  # 应为[1.1, 2.2, 3.3, 4.4, 5.5]

    # natural_log 测试
    print("\n4. natural_log 函数测试:")
    print(f"natural_log([1, 2, 3]) = {LN(np.array([1, 2, 3]))}")  # 应为[0, 0.693, 1.099]

    # power 测试
    print("\n5. power 函数测试:")
    print(f"power([1, 2, 3], 2) = {POW(np.array([1, 2, 3]), 2)}")  # 应为[1, 4, 9]

    # square_root 测试
    print("\n6. square_root 函数测试:")
    print(f"square_root([1, 4, 9]) = {SQRT(np.array([1, 4, 9]))}")  # 应为[1, 2, 3]

    # sine 测试
    print("\n7. sine 函数测试:")
    print(f"sine([0, np.pi/2, np.pi]) = {SIN(np.array([0, np.pi / 2, np.pi]))}")  # 应为[0, 1, 0]

    # cosine 测试
    print("\n8. cosine 函数测试:")
    print(f"cosine([0, np.pi/2, np.pi]) = {COS(np.array([0, np.pi / 2, np.pi]))}")  # 应为[1, 0, -1]

    # tangent 测试
    print("\n9. tangent 函数测试:")
    print(f"tangent([0, np.pi/4]) = {TAN(np.array([0, np.pi / 4]))}")  # 应为[0, 1]

    # maximum 测试
    print("\n10. maximum 函数测试:")
    print(f"maximum({test_series[:5]}, {test_series2[:5]}) = {MAX(test_series[:5], test_series2[:5])}")

    # minimum 测试
    print("\n11. minimum 函数测试:")
    print(f"minimum({test_series[:5]}, {test_series2[:5]}) = {MIN(test_series[:5], test_series2[:5])}")

    # conditional_select 测试
    print("\n12. conditional_select 函数测试:")
    print(
        f"conditional_select({test_condition[:5]}, {test_series[:5]}, {test_series2[:5]}) = {IF(test_condition[:5], test_series[:5], test_series2[:5])}")

    # shift 测试
    print("\n13. shift 函数测试:")
    print(f"shift({test_series[:5]}) = {REF(test_series[:5])}")
    print(f"shift({test_series[:5]}, 2) = {REF(test_series[:5], 2)}")

    # difference 测试
    print("\n14. difference 函数测试:")
    print(f"difference({test_series[:5]}) = {DIFF(test_series[:5])}")
    print(f"difference({test_series[:5]}, 2) = {DIFF(test_series[:5], 2)}")

    # standard_deviation 测试
    print("\n15. standard_deviation 函数测试:")
    print(f"standard_deviation({test_series}, 3) = {STD(test_series, 3)}")

    # rolling_sum 测试
    print("\n16. rolling_sum 函数测试:")
    print(f"rolling_sum({test_series[:5]}, 3) = {SUM(test_series[:5], 3)}")
    print(f"rolling_sum({test_series[:5]}, 0) = {SUM(test_series[:5], 0)}")  # 累计和

    # constant_series 测试
    print("\n17. constant_series 函数测试:")
    print(f"constant_series({test_series[:5]}) = {CONST(test_series[:5])}")

    # highest_in_period 测试
    print("\n18. highest_in_period 函数测试:")
    print(f"highest_in_period({test_series}, 3) = {HHV(test_series, 3)}")

    # lowest_in_period 测试
    print("\n19. lowest_in_period 函数测试:")
    print(f"lowest_in_period({test_series}, 3) = {LLV(test_series, 3)}")

    # highest_value_position 测试
    print("\n20. highest_value_position 函数测试:")
    test_for_position = np.array([1, 3, 5, 2, 4])
    print(f"highest_value_position({test_for_position}, 3) = {HHVBARS(test_for_position, 3)}")

    # lowest_value_position 测试
    print("\n21. lowest_value_position 函数测试:")
    print(f"lowest_value_position({test_for_position}, 3) = {LLVBARS(test_for_position, 3)}")

    # simple_moving_average 测试
    print("\n22. simple_moving_average 函数测试:")
    print(f"simple_moving_average({test_series}, 3) = {MA(test_series, 3)}")

    # exponential_moving_average 测试
    print("\n23. exponential_moving_average 函数测试:")
    print(f"exponential_moving_average({test_series}, 3) = {EMA(test_series, 3)}")

    # smoothed_moving_average 测试
    print("\n24. smoothed_moving_average 函数测试:")
    print(f"smoothed_moving_average({test_series}, 3) = {SMA(test_series, 3)}")
    print(f"smoothed_moving_average({test_series}, 3, 2) = {SMA(test_series, 3, 2)}")

    # weighted_moving_average 测试
    print("\n25. weighted_moving_average 函数测试:")
    print(f"weighted_moving_average({test_series}, 3) = {WMA(test_series, 3)}")

    # dynamic_moving_average 测试
    print("\n26. dynamic_moving_average 函数测试:")
    print(f"dynamic_moving_average({test_series}, 0.5) = {DMA(test_series, 0.5)}")
    alpha_series = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.5])
    print(
        f"dynamic_moving_average({test_series}, {alpha_series}) = {DMA(test_series, alpha_series)}")

    # average_absolute_deviation 测试
    print("\n27. average_absolute_deviation 函数测试:")
    print(f"average_absolute_deviation({test_series}, 3) = {AVEDEV(test_series, 3)}")

    # linear_regression_slope 测试
    print("\n28. linear_regression_slope 函数测试:")
    print(f"linear_regression_slope({test_series}, 5) = {SLOPE(test_series, 5)}")

    # linear_regression_forecast 测试
    print("\n29. linear_regression_forecast 函数测试:")
    print(f"linear_regression_forecast({test_series}, 5) = {FORCAST(test_series, 5)}")

    # condition_last_period 测试
    print("\n30. condition_last_period 函数测试:")
    test_bool_series = np.array([True, True, False, True, True, True, False, True, True, True])
    print(f"condition_last_period({test_bool_series}, 3, 1) = {LAST(test_bool_series, 3, 1)}")
