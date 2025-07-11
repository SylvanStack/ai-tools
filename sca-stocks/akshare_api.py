import akshare as ak
import pandas as pd
import datetime

# 获取深交所股票总貌
def get_szse_summary(date=None):
    """
    获取深交所股票总貌数据
    
    Args:
        date: 日期，格式为YYYYMMDD，如"20200619"
        
    Returns:
        DataFrame: 深交所股票总貌数据
    """
    try:
        if date is None:
            date = datetime.datetime.now().strftime("%Y%m%d")
        stock_szse_summary_df = ak.stock_szse_summary(date=date)
        return stock_szse_summary_df
    except Exception as e:
        print(f"获取深交所股票总貌数据失败: {e}")
        return pd.DataFrame()

# 获取上交所股票总貌
def get_sse_summary():
    """
    获取上交所股票总貌数据
    
    Returns:
        DataFrame: 上交所股票总貌数据
    """
    try:
        # 上交所总貌函数不接受日期参数
        stock_sse_summary_df = ak.stock_sse_summary()
        return stock_sse_summary_df
    except Exception as e:
        print(f"获取上交所股票总貌数据失败: {e}")
        return pd.DataFrame()

# 获取沪深京A股列表
def get_stock_list():
    """
    获取沪深京A股列表
    
    Returns:
        DataFrame: 沪深京A股列表
    """
    try:
        # 使用正确的函数名称获取A股列表
        stock_list_df = ak.stock_info_a_code_name()
        return stock_list_df
    except Exception as e:
        print(f"获取沪深京A股列表失败: {e}")
        return pd.DataFrame()

# 获取个股历史行情
def get_stock_history(symbol, period="daily", start_date=None, end_date=None, adjust=""):
    """
    获取个股历史行情数据
    
    Args:
        symbol: 股票代码，如"000001"
        period: 周期，可选daily, weekly, monthly
        start_date: 开始日期，格式为YYYYMMDD，如"20200101"
        end_date: 结束日期，格式为YYYYMMDD，如"20200619"
        adjust: 复权类型，可选"", "qfq", "hfq"
        
    Returns:
        DataFrame: 个股历史行情数据
    """
    try:
        if start_date is None:
            start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime("%Y%m%d")
        if end_date is None:
            end_date = datetime.datetime.now().strftime("%Y%m%d")
        # 使用正确的函数名称获取历史行情
        stock_history_df = ak.stock_zh_a_hist(symbol=symbol, period=period, start_date=start_date, end_date=end_date, adjust=adjust)
        return stock_history_df
    except Exception as e:
        print(f"获取个股历史行情数据失败: {e}")
        return pd.DataFrame()

# 测试代码
if __name__ == "__main__":
    # 测试获取深交所股票总貌
    szse_summary_df = get_szse_summary(date="20230619")
    print("深交所股票总貌数据:")
    print(szse_summary_df)

    # # 测试获取上交所股票总貌
    sse_summary_df = get_sse_summary()
    print("\n上交所股票总貌数据:")
    print(sse_summary_df)
    
    # 测试获取沪深京A股列表
    stock_list_df = get_stock_list()
    print("\n沪深京A股列表:")
    print(stock_list_df.head())
    
    # # 测试获取个股历史行情
    stock_history_df = get_stock_history(symbol="000001", start_date="20230101", end_date="20230619")
    print("\n平安银行历史行情数据:")
    print(stock_history_df.head())