"""
高级技术指标工具类
提供扩展的技术分析函数，完美兼容通达信或同花顺
"""
import math
import numpy as np
import pandas as pd
from utils.indicator_utils import *
from utils.advance_indicator import *


# 保留通达信风格的函数名称以保持兼容性
def HHV(series, period):
    """
    计算周期内最高值，支持period为序列版本
    
    Args:
        series: 输入数据序列
        period: 周期，可以是固定值或序列
        
    Returns:
        numpy.ndarray: 周期内最高值序列
        
    Examples:
        HHV(CLOSE, 5)  # 最近5天收盘最高价
    """
    if isinstance(period, (int, float)):
        # 使用indicator_utils中的highest_in_period函数
        return HHV(series, period)
    else:
        result = np.repeat(np.nan, len(series))
        for i in range(len(series)):
            if (not np.isnan(period[i])) and period[i] <= i + 1:
                result[i] = np.max(series[i + 1 - int(period[i]):i + 1])
        return result


def LLV(series, period):
    """
    计算周期内最低值，支持period为序列版本
    
    Args:
        series: 输入数据序列
        period: 周期，可以是固定值或序列
        
    Returns:
        numpy.ndarray: 周期内最低值序列
        
    Examples:
        LLV(CLOSE, 5)  # 最近5天收盘最低价
    """
    if isinstance(period, (int, float)):
        # 使用indicator_utils中的lowest_in_period函数
        return LLV(series, period)
    else:
        result = np.repeat(np.nan, len(series))
        for i in range(len(series)):
            if (not np.isnan(period[i])) and period[i] <= i + 1:
                result[i] = np.min(series[i + 1 - int(period[i]):i + 1])
        return result


def DSMA(series, period):
    """
    计算偏差自适应移动平均线 (Deviation Scaled Moving Average)
    
    Args:
        series: 输入数据序列
        period: 周期
        
    Returns:
        numpy.ndarray: DSMA值序列
        
    Notes:
        由jqz1226于2021-12-27实现
    """
    # 计算系数
    a1 = math.exp(- 1.414 * math.pi * 2 / period)
    b1 = 2 * a1 * math.cos(1.414 * math.pi * 2 / period)
    c2 = b1
    c3 = -a1 * a1
    c1 = 1 - c2 - c3
    
    # 计算两日差值序列
    zeros = np.pad(series[2:] - series[:-2], (2, 0), 'constant')
    
    # 滤波
    filt = np.zeros(len(series))
    for i in range(2, len(series)):
        filt[i] = c1 * (zeros[i] + zeros[i - 1]) / 2 + c2 * filt[i - 1] + c3 * filt[i - 2]

    # 计算均方根
    rms = np.sqrt(SUM(np.square(filt), period) / period)
    
    # 缩放滤波值
    scaled_filt = np.divide(filt, rms, out=np.zeros_like(filt), where=rms!=0)
    
    # 计算自适应系数
    alpha = np.abs(scaled_filt) * 5 / period
    
    # 计算动态移动平均
    return DMA(series, alpha)


def SUMBARS(series, target):
    """
    计算向前累加直到大于等于目标值所需的周期数
    
    Args:
        series: 被累计的源数据，所有元素必须大于0
        target: 累加截止的界限数，可以是单值或序列
        
    Returns:
        numpy.ndarray: 各点对应的周期数
        
    Examples:
        SUMBARS(VOLUME, CAPITAL) # 求完全换手的周期数
        
    Notes:
        由jqz1226实现
    """
    # 检查输入数据有效性
    if np.any(series <= 0):
        raise ValueError('数组series的每个元素都必须大于0！')

    # 倒转序列便于计算
    series_reversed = np.flipud(series)
    length = len(series)

    # 将单值target转换为序列
    if isinstance(target * 1.0, float):
        target = np.repeat(target, length)
    
    target_reversed = np.flipud(target)
    result = np.zeros(length)
    
    # 计算累积和
    cumsum = np.insert(np.cumsum(series_reversed), 0, 0.0)

    # 计算每个点所需的周期数
    for i in range(length):
        k = np.searchsorted(cumsum[i + 1:], target_reversed[i] + cumsum[i])
        if k < length - i:  # 找到
            result[length - i - 1] = k + 1
            
    return result.astype(int)


def calculate_parabolic_sar(high, low, period=10, step=2, max_step=20):
    """
    计算抛物线转向指标 (Parabolic SAR)
    
    Args:
        high: 最高价序列
        low: 最低价序列
        period: 计算周期，默认10
        step: 步长（百分比），默认2
        max_step: 步长极限（百分比），默认20
        
    Returns:
        numpy.ndarray: SAR值序列
        
    Notes:
        由jqz1226于2021-11-24首次发表于聚宽(www.joinquant.com)
    """
    f_step = step / 100
    f_max = max_step / 100
    af = 0.0
    is_long = high[period - 1] > high[period - 2]
    b_first = True
    length = len(high)

    # 计算前期最高价和最低价
    s_hhv = REF(HHV(high, period), 1)
    s_llv = REF(LLV(low, period), 1)
    
    # 初始化SAR序列
    sar = np.repeat(np.nan, length)
    
    # 计算SAR值
    for i in range(period, length):
        if b_first:  # 第一步
            af = f_step
            sar[i] = s_llv[i] if is_long else s_hhv[i]
            b_first = False
        else:  # 继续多或空
            ep = s_hhv[i] if is_long else s_llv[i]  # 极值
            if (is_long and high[i] > ep) or ((not is_long) and low[i] < ep):  # 顺势：多创新高或空创新低
                af = min(af + f_step, f_max)
            
            sar[i] = sar[i - 1] + af * (ep - sar[i - 1])

        # 判断是否转向
        if (is_long and low[i] < sar[i]) or ((not is_long) and high[i] > sar[i]):  # 反空或反多
            is_long = not is_long
            b_first = True
            
    return sar


def calculate_tdx_sar(high, low, step=2, limit=20):
    """
    计算通达信SAR指标，与通达信SAR对比完全一致
    
    Args:
        high: 最高价序列
        low: 最低价序列
        step: AF步长（百分比），默认2
        limit: AF极限值（百分比），默认20
        
    Returns:
        numpy.ndarray: SAR值序列
    """
    af_step = step / 100
    af_limit = limit / 100
    sar = np.zeros(len(high))  # 初始化返回数组

    # 第一个bar
    bull = True  # 初始为多头
    af = af_step
    ep = high[0]
    sar[0] = low[0]
    
    # 第2个bar及其以后
    for i in range(1, len(high)):
        # 1.更新：极值点和加速因子
        if bull:  # 多头
            if high[i] > ep:  # 创新高
                ep = high[i]
                af = min(af + af_step, af_limit)
        else:  # 空头
            if low[i] < ep:  # 创新低
                ep = low[i]
                af = min(af + af_step, af_limit)
                
        # 2.计算SAR
        sar[i] = sar[i - 1] + af * (ep - sar[i - 1])

        # 3.修正SAR
        if bull:
            sar[i] = max(sar[i - 1], min(sar[i], low[i], low[i - 1]))
        else:
            sar[i] = min(sar[i - 1], max(sar[i], high[i], high[i - 1]))

        # 4. 判断是否转向
        if bull:  # 多头
            if low[i] < sar[i]:  # 向下跌破，转空
                bull = False
                tmp_sar = ep  # 上阶段的最高点
                ep = low[i]
                af = af_step
                if high[i - 1] == tmp_sar:  # 紧邻即最高点
                    sar[i] = tmp_sar
                else:
                    sar[i] = tmp_sar + af * (ep - tmp_sar)
        else:  # 空头
            if high[i] > sar[i]:  # 向上突破, 转多
                bull = True
                ep = high[i]
                af = af_step
                sar[i] = min(low[i], low[i - 1])
                
    return sar


if __name__ == '__main__':
    # 测试数据
    test_high = np.array([10.2, 10.8, 11.5, 11.0, 11.8, 12.2, 12.0, 12.5, 13.0, 13.2])
    test_low = np.array([9.8, 10.3, 10.9, 10.5, 11.2, 11.7, 11.5, 12.0, 12.5, 12.7])
    test_close = np.array([10.0, 10.5, 11.2, 10.8, 11.5, 12.0, 11.8, 12.3, 12.8, 13.0])
    test_volume = np.array([1000, 1200, 1500, 1100, 1300, 1600, 1400, 1700, 1800, 1900])
    
    print("=" * 50)
    print("扩展技术指标函数测试用例")
    print("=" * 50)
    
    # 测试HHV
    print("\n1. HHV函数测试:")
    period = 3
    result = HHV(test_close, period)
    print(f"HHV(test_close, {period}) = {result}")
    
    # 测试LLV
    print("\n2. LLV函数测试:")
    period = 3
    result = LLV(test_close, period)
    print(f"LLV(test_close, {period}) = {result}")
    
    # 测试DSMA
    print("\n3. DSMA函数测试:")
    period = 5
    result = DSMA(test_close, period)
    print(f"DSMA(test_close, {period}) = {result}")
    
    # 测试SUMBARS
    print("\n4. SUMBARS函数测试:")
    target = 3000
    result = SUMBARS(test_volume, target)
    print(f"SUMBARS(test_volume, {target}) = {result}")
    
    # 测试SAR
    print("\n5. calculate_parabolic_sar函数测试:")
    result = calculate_parabolic_sar(test_high, test_low)
    print(f"calculate_parabolic_sar(test_high, test_low) = {result}")
    
    # 测试TDX_SAR
    print("\n6. calculate_tdx_sar函数测试:")
    result = calculate_tdx_sar(test_high, test_low)
    print(f"calculate_tdx_sar(test_high, test_low) = {result}")
