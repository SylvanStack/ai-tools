"""
技术指标工具类
提供基于核心指标和高级指标的技术分析函数，完美兼容通达信或同花顺
"""
import numpy as np
import pandas as pd
from utils.indicator_utils import *
from utils.advance_indicator import *


def MACD(close, short_period=12, long_period=26, signal_period=9):
    """
    计算MACD指标 (Moving Average Convergence Divergence)
    
    Args:
        close: 收盘价序列
        short_period: 短周期，默认12
        long_period: 长周期，默认26
        signal_period: 信号周期，默认9
        
    Returns:
        tuple: (DIF, DEA, MACD)
            - DIF: 差离值
            - DEA: 信号线
            - MACD: MACD柱状值 (DIF-DEA)*2
    """
    dif = EMA(close, short_period) - EMA(close, long_period)
    dea = EMA(dif, signal_period)
    macd = (dif - dea) * 2
    return RD(dif), RD(dea), RD(macd)


def KDJ(close, high, low, n=9, m1=3, m2=3):
    """
    计算KDJ指标 (随机指标)
    
    Args:
        close: 收盘价序列
        high: 最高价序列
        low: 最低价序列
        n: 周期，默认9
        m1: K值平滑因子，默认3
        m2: D值平滑因子，默认3
        
    Returns:
        tuple: (K, D, J)
            - K: 快速随机线
            - D: 慢速随机线
            - J: 三重强度线
    """
    rsv = (close - LLV(low, n)) / (HHV(high, n) - LLV(low, n)) * 100
    k = EMA(rsv, (m1 * 2 - 1))
    d = EMA(k, (m2 * 2 - 1))
    j = k * 3 - d * 2
    return k, d, j


def RSI(close, period=24):
    """
    计算RSI指标 (相对强弱指标)
    
    Args:
        close: 收盘价序列
        period: 周期，默认24
        
    Returns:
        numpy.ndarray: RSI值序列
    """
    price_diff = close - REF(close, 1)
    return RD(SMA(MAX(price_diff, 0), period) /
              SMA(ABS(price_diff), period) * 100)


def WR(close, high, low, n=10, n1=6):
    """
    计算威廉指标 (Williams %R)
    
    Args:
        close: 收盘价序列
        high: 最高价序列
        low: 最低价序列
        n: 第一个周期，默认10
        n1: 第二个周期，默认6
        
    Returns:
        tuple: (WR, WR1) - 两个不同周期的威廉指标
    """
    wr = (HHV(high, n) - close) / (HHV(high, n) - LLV(low, n)) * 100
    wr1 = (HHV(high, n1) - close) / (HHV(high, n1) - LLV(low, n1)) * 100
    return RD(wr), RD(wr1)


def BIAS(close, l1=6, l2=12, l3=24):
    """
    计算BIAS乖离率
    
    Args:
        close: 收盘价序列
        l1: 短周期，默认6
        l2: 中周期，默认12
        l3: 长周期，默认24
        
    Returns:
        tuple: (BIAS1, BIAS2, BIAS3) - 三个不同周期的乖离率
    """
    bias1 = (close - MA(close, l1)) / MA(close, l1) * 100
    bias2 = (close - MA(close, l2)) / MA(close, l2) * 100
    bias3 = (close - MA(close, l3)) / MA(close, l3) * 100
    return RD(bias1), RD(bias2), RD(bias3)


def BOLL(close, period=20, std_dev=2):
    """
    计算布林带指标 (Bollinger Bands)
    
    Args:
        close: 收盘价序列
        period: 周期，默认20
        std_dev: 标准差倍数，默认2
        
    Returns:
        tuple: (UPPER, MID, LOWER)
            - UPPER: 上轨
            - MID: 中轨
            - LOWER: 下轨
    """
    mid = MA(close, period)
    upper = mid + STD(close, period) * std_dev
    lower = mid - STD(close, period) * std_dev
    return RD(upper), RD(mid), RD(lower)


def PSY(close, n=12, m=6):
    """
    计算心理线指标 (PSY)
    
    Args:
        close: 收盘价序列
        n: 统计周期，默认12
        m: 平均周期，默认6
        
    Returns:
        tuple: (PSY, PSYMA) - 心理线及其平均线
    """
    psy = COUNT(close > REF(close, 1), n) / n * 100
    psyma = MA(psy, m)
    return RD(psy), RD(psyma)


def CCI(close, high, low, period=14):
    """
    计算顺势指标 (Commodity Channel Index)
    
    Args:
        close: 收盘价序列
        high: 最高价序列
        low: 最低价序列
        period: 周期，默认14
        
    Returns:
        numpy.ndarray: CCI值序列
    """
    tp = (high + low + close) / 3
    return (tp - MA(tp, period)) / (0.015 * AVEDEV(tp, period))


def ATR(close, high, low, period=20):
    """
    计算真实波动范围 (Average True Range)
    
    Args:
        close: 收盘价序列
        high: 最高价序列
        low: 最低价序列
        period: 周期，默认20
        
    Returns:
        numpy.ndarray: ATR值序列
    """
    tr = MAX(
        MAX((high - low), ABS(REF(close, 1) - high)),
        ABS(REF(close, 1) - low)
    )
    return MA(tr, period)


def BBI(close, m1=3, m2=6, m3=12, m4=20):
    """
    计算多空指标 (Bull and Bear Index)
    
    Args:
        close: 收盘价序列
        m1: 第一个周期，默认3
        m2: 第二个周期，默认6
        m3: 第三个周期，默认12
        m4: 第四个周期，默认20
        
    Returns:
        numpy.ndarray: BBI值序列
    """
    return (MA(close, m1) +
            MA(close, m2) +
            MA(close, m3) +
            MA(close, m4)) / 4


def DMI(close, high, low, m1=14, m2=6):
    """
    计算动向指标 (Directional Movement Index)
    
    Args:
        close: 收盘价序列
        high: 最高价序列
        low: 最低价序列
        m1: 统计周期，默认14
        m2: 平均周期，默认6
        
    Returns:
        tuple: (PDI, MDI, ADX, ADXR)
            - PDI: 正向指标
            - MDI: 负向指标
            - ADX: 平均方向指标
            - ADXR: 评估ADX值
    """
    tr = SUM(
        MAX(
            MAX(high - low, ABS(high - REF(close, 1))),
            ABS(low - REF(close, 1))
        ),
        m1
    )

    hd = high - REF(high, 1)
    ld = REF(low, 1) - low

    dmp = SUM(
        IF((hd > 0) & (hd > ld), hd, 0),
        m1
    )

    dmm = SUM(
        IF((ld > 0) & (ld > hd), ld, 0),
        m1
    )

    pdi = dmp * 100 / tr
    mdi = dmm * 100 / tr
    adx = MA(ABS(mdi - pdi) / (pdi + mdi) * 100, m2)
    adxr = (adx + REF(adx, m2)) / 2

    return pdi, mdi, adx, adxr


def TAQ(high, low, period):
    """
    计算海龟交易通道 (Turtle Trading Channel)
    
    Args:
        high: 最高价序列
        low: 最低价序列
        period: 周期
        
    Returns:
        tuple: (UP, MID, DOWN)
            - UP: 上轨
            - MID: 中轨
            - DOWN: 下轨
    """
    up = HHV(high, period)
    down = LLV(low, period)
    mid = (up + down) / 2
    return up, mid, down


def KTN(close, high, low, n=20, m=10):
    """
    计算肯特纳通道 (Keltner Channel)
    
    Args:
        close: 收盘价序列
        high: 最高价序列
        low: 最低价序列
        n: 平均周期，默认20
        m: ATR周期，默认10
        
    Returns:
        tuple: (UPPER, MID, LOWER)
            - UPPER: 上轨
            - MID: 中轨
            - LOWER: 下轨
    """
    mid = EMA((high + low + close) / 3, n)
    atr_val = calculate_atr(close, high, low, m)
    upper = mid + 2 * atr_val
    lower = mid - 2 * atr_val
    return upper, mid, lower


def TRIX(close, m1=12, m2=20):
    """
    计算三重指数平滑平均线 (Triple Exponential Average)
    
    Args:
        close: 收盘价序列
        m1: 平滑周期，默认12
        m2: 信号周期，默认20
        
    Returns:
        tuple: (TRIX, TRMA) - TRIX指标及其移动平均
    """
    tr = EMA(
        EMA(
            EMA(close, m1),
            m1
        ),
        m1
    )
    trix = (tr - REF(tr, 1)) / REF(tr, 1) * 100
    trma = MA(trix, m2)
    return trix, trma


def VR(close, volume, period=26):
    """
    计算容量比率 (Volume Ratio)
    
    Args:
        close: 收盘价序列
        volume: 成交量序列
        period: 周期，默认26
        
    Returns:
        numpy.ndarray: VR值序列
    """
    prev_close = REF(close, 1)
    return SUM(
        IF(close > prev_close, volume, 0),
        period
    ) / SUM(
        IF(close <= prev_close, volume, 0),
        period
    ) * 100


def CR(close, high, low, period=20):
    """
    计算能量指标 (CR)
    
    Args:
        close: 收盘价序列
        high: 最高价序列
        low: 最低价序列
        period: 周期，默认20
        
    Returns:
        numpy.ndarray: CR值序列
    """
    mid = REF((high + low + close) / 3, 1)
    return SUM(
        MAX(0, high - mid),
        period
    ) / SUM(
        MAX(0, mid - low),
        period
    ) * 100


def EMV(high, low, volume, n=14, m=9):
    """
    计算简易波动指标 (Ease of Movement Value)
    
    Args:
        high: 最高价序列
        low: 最低价序列
        volume: 成交量序列
        n: 周期，默认14
        m: 信号周期，默认9
        
    Returns:
        tuple: (EMV, MAEMV) - EMV指标及其移动平均
    """
    vol_ratio = MA(volume, n) / volume
    mid = 100 * (high + low - REF(high + low, 1)) / (high + low)
    emv = MA(
        mid * vol_ratio * (high - low) / MA(high - low, n),
        n
    )
    maemv = MA(emv, m)
    return emv, maemv


def DPO(close, m1=20, m2=10, m3=6):
    """
    计算区间震荡线 (Detrended Price Oscillator)
    
    Args:
        close: 收盘价序列
        m1: 周期，默认20
        m2: 位移，默认10
        m3: 平均周期，默认6
        
    Returns:
        tuple: (DPO, MADPO) - DPO指标及其移动平均
    """
    dpo = close - REF(MA(close, m1), m2)
    madpo = MA(dpo, m3)
    return dpo, madpo


def BRAR(open_price, close, high, low, period=26):
    """
    计算情绪指标 (BR-AR)
    
    Args:
        open_price: 开盘价序列
        close: 收盘价序列
        high: 最高价序列
        low: 最低价序列
        period: 周期，默认26
        
    Returns:
        tuple: (AR, BR) - AR指标和BR指标
    """
    ar = SUM(high - open_price, period) / SUM(open_price - low, period) * 100
    br = SUM(
        MAX(0, high - REF(close, 1)),
        period
    ) / SUM(
        MAX(0, REF(close, 1) - low),
        period
    ) * 100
    return ar, br


def DFMA(close, n1=10, n2=50, m=10):
    """
    计算平行线差指标 (Different of Moving Average)
    
    Args:
        close: 收盘价序列
        n1: 短周期，默认10
        n2: 长周期，默认50
        m: 信号周期，默认10
        
    Returns:
        tuple: (DIF, DIFMA) - DMA差值及其移动平均
    """
    dif = MA(close, n1) - MA(close, n2)
    difma = MA(dif, m)
    return dif, difma


def MTM(close, n=12, m=6):
    """
    计算动量指标 (Momentum)
    
    Args:
        close: 收盘价序列
        n: 周期，默认12
        m: 信号周期，默认6
        
    Returns:
        tuple: (MTM, MTMMA) - 动量值及其移动平均
    """
    mtm = close - REF(close, n)
    mtmma = MA(mtm, m)
    return mtm, mtmma


def MASS(high, low, n1=9, n2=25, m=6):
    """
    计算梅斯线 (Mass Index)
    
    Args:
        high: 最高价序列
        low: 最低价序列
        n1: 短周期，默认9
        n2: 长周期，默认25
        m: 信号周期，默认6
        
    Returns:
        tuple: (MASS, MA_MASS) - 梅斯线及其移动平均
    """
    mass = SUM(
        MA(high - low, n1) / MA(MA(high - low, n1), n1),
        n2
    )
    ma_mass = MA(mass, m)
    return mass, ma_mass


def ROC(close, n=12, m=6):
    """
    计算变动率指标 (Rate of Change)
    
    Args:
        close: 收盘价序列
        n: 周期，默认12
        m: 信号周期，默认6
        
    Returns:
        tuple: (ROC, MAROC) - 变动率及其移动平均
    """
    roc = 100 * (close - REF(close, n)) / REF(close, n)
    maroc = MA(roc, m)
    return roc, maroc


def EXPMA(close, n1=12, n2=50):
    """
    计算EMA指数平均数指标
    
    Args:
        close: 收盘价序列
        n1: 短周期，默认12
        n2: 长周期，默认50
        
    Returns:
        tuple: (EMA1, EMA2) - 两个不同周期的EMA
    """
    return EMA(close, n1), EMA(close, n2)


def OBV(close, volume):
    """
    计算能量潮指标 (On Balance Volume)
    
    Args:
        close: 收盘价序列
        volume: 成交量序列
        
    Returns:
        numpy.ndarray: OBV值序列
    """
    return SUM(
        IF(
            close > REF(close, 1),
            volume,
            IF(close < REF(close, 1), -volume, 0)
        ),
        0
    ) / 10000


def MFI(close, high, low, volume, period=14):
    """
    计算资金流量指标 (Money Flow Index)
    
    Args:
        close: 收盘价序列
        high: 最高价序列
        low: 最低价序列
        volume: 成交量序列
        period: 周期，默认14
        
    Returns:
        numpy.ndarray: MFI值序列
    """
    typ = (high + low + close) / 3
    v1 = SUM(
        IF(typ > REF(typ, 1), typ * volume, 0),
        period
    ) / SUM(
        IF(typ < REF(typ, 1), typ * volume, 0),
        period
    )
    return 100 - (100 / (1 + v1))


def ASI(open_price, close, high, low, m1=26, m2=10):
    """
    计算振动升降指标 (Accumulation Swing Index)
    
    Args:
        open_price: 开盘价序列
        close: 收盘价序列
        high: 最高价序列
        low: 最低价序列
        m1: 周期，默认26
        m2: 信号周期，默认10
        
    Returns:
        tuple: (ASI, ASIT) - ASI指标及其移动平均
    """
    lc = REF(close, 1)
    aa = ABS(high - lc)
    bb = ABS(low - lc)
    cc = ABS(high - REF(low, 1))
    dd = ABS(lc - REF(open_price, 1))

    r = IF(
        (aa > bb) & (aa > cc),
        aa + bb / 2 + dd / 4,
        IF(
            (bb > cc) & (bb > aa),
            bb + aa / 2 + dd / 4,
            cc + dd / 4
        )
    )

    x = (close - lc + (close - open_price) / 2 + lc - REF(open_price, 1))
    si = 16 * x / r * MAX(aa, bb)
    asi = SUM(si, m1)
    asit = MA(asi, m2)
    return asi, asit


def XSII(close, high, low, n=102, m=7):
    """
    计算薛斯通道II (XS II Channel)
    
    Args:
        close: 收盘价序列
        high: 最高价序列
        low: 最低价序列
        n: 百分比参数，默认102
        m: 百分比参数，默认7
        
    Returns:
        tuple: (TD1, TD2, TD3, TD4) - 四条通道线
    """
    aa = MA((2 * close + high + low) / 4, 5)
    td1 = aa * n / 100
    td2 = aa * (200 - n) / 100

    cc = ABS((2 * close + high + low) / 4 - MA(close, 20)) / MA(close, 20)
    dd = DMA(close, cc)

    td3 = (1 + m / 100) * dd
    td4 = (1 - m / 100) * dd

    return td1, td2, td3, td4


if __name__ == '__main__':
    # 测试数据
    test_close = np.array([10.0, 10.5, 11.2, 10.8, 11.5, 12.0, 11.8, 12.3, 12.8, 13.0])
    test_high = np.array([10.2, 10.8, 11.5, 11.0, 11.8, 12.2, 12.0, 12.5, 13.0, 13.2])
    test_low = np.array([9.8, 10.3, 10.9, 10.5, 11.2, 11.7, 11.5, 12.0, 12.5, 12.7])
    test_open = np.array([9.9, 10.1, 10.6, 11.0, 10.7, 11.6, 12.0, 11.7, 12.1, 12.9])
    test_volume = np.array([1000, 1200, 1500, 1100, 1300, 1600, 1400, 1700, 1800, 1900])

    print("=" * 50)
    print("技术指标函数测试用例")
    print("=" * 50)

    # 测试MACD
    print("\n1. MACD指标测试:")
    dif, dea, macd = calculate_macd(test_close)
    print(f"DIF: {dif}")
    print(f"DEA: {dea}")
    print(f"MACD: {macd}")

    # 测试KDJ
    print("\n2. KDJ指标测试:")
    k, d, j = calculate_kdj(test_close, test_high, test_low)
    print(f"K: {k}")
    print(f"D: {d}")
    print(f"J: {j}")

    # 测试RSI
    print("\n3. RSI指标测试:")
    rsi = calculate_rsi(test_close)
    print(f"RSI: {rsi}")

    # 测试布林带
    print("\n4. 布林带指标测试:")
    upper, mid, lower = calculate_bollinger_bands(test_close)
    print(f"上轨: {upper}")
    print(f"中轨: {mid}")
    print(f"下轨: {lower}")

    # 测试ATR
    print("\n5. ATR指标测试:")
    atr = calculate_atr(test_close, test_high, test_low)
    print(f"ATR: {atr}")
