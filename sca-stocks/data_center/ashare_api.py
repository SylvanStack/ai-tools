import datetime
import json
import requests
from typing import List, Union

import pandas as pd


class AshareStockData:
    """
    股票数据获取类，负责从不同数据源获取股票行情数据
    """

    @staticmethod
    def _format_code(code: str) -> str:
        """格式化股票代码，统一代码格式
        
        Args:
            code: 原始股票代码，如'000001.XSHG'或'sh000001'
            
        Returns:
            格式化后的代码，如'sh000001'
        """
        xcode = code.replace('.XSHG', '').replace('.XSHE', '')
        return f"sh{xcode}" if 'XSHG' in code else f"sz{xcode}" if 'XSHE' in code else code

    @staticmethod
    def _format_date(date: Union[str, datetime.date, None]) -> str:
        """格式化日期为字符串格式
        
        Args:
            date: 日期对象或字符串
            
        Returns:
            格式化后的日期字符串，如果是今天则返回空字符串
        """
        if not date:
            return ''

        if isinstance(date, datetime.date):
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = str(date).split(' ')[0]

        # 如果日期是今天就返回空字符串
        if date_str == datetime.datetime.now().strftime('%Y-%m-%d'):
            return ''

        return date_str

    def get_price_day_tx(self,
                         code: str,
                         end_date: Union[str, datetime.date, None] = '',
                         count: int = 10,
                         frequency: str = '1d') -> pd.DataFrame:
        """从腾讯接口获取日线数据
        
        Args:
            code: 股票代码
            end_date: 结束日期
            count: 获取数据的数量
            frequency: 频率，'1d'日线，'1w'周线，'1M'月线
            
        Returns:
            包含股票日线数据的DataFrame
        """
        unit = 'week' if frequency in '1w' else 'month' if frequency in '1M' else 'day'
        end_date_str = self._format_date(end_date)

        url = f'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},{unit},,{end_date_str},{count},qfq'
        response = requests.get(url)
        st = json.loads(response.content)

        ms = 'qfq' + unit
        stk = st['data'][code]
        buf = stk[ms] if ms in stk else stk[unit]  # 指数返回不是qfqday,是day

        df = pd.DataFrame(buf, columns=['time', 'open', 'close', 'high', 'low', 'volume'], dtype='float')
        df.time = pd.to_datetime(df.time)
        df.set_index(['time'], inplace=True)
        df.index.name = ''  # 处理索引

        return df

    def get_price_min_tx(self, code: str, end_date: Union[str, datetime.date, None] = None,
                         count: int = 10, frequency: str = '1m') -> pd.DataFrame:
        """从腾讯接口获取分钟线数据
        
        Args:
            code: 股票代码
            end_date: 结束日期
            count: 获取数据的数量
            frequency: 频率，如'1m'，'5m'等
            
        Returns:
            包含股票分钟线数据的DataFrame
        """
        # 解析K线周期数
        ts = int(frequency[:-1]) if frequency[:-1].isdigit() else 1

        end_date_str = ''
        if end_date:
            if isinstance(end_date, datetime.date):
                end_date_str = end_date.strftime('%Y-%m-%d')
            else:
                end_date_str = str(end_date).split(' ')[0]

        url = f'http://ifzq.gtimg.cn/appstock/app/kline/mkline?param={code},m{ts},,{count}'
        response = requests.get(url)
        st = json.loads(response.content)

        buf = st['data'][code]['m' + str(ts)]
        df = pd.DataFrame(buf, columns=['time', 'open', 'close', 'high', 'low', 'volume', 'n1', 'n2'])
        df = df[['time', 'open', 'close', 'high', 'low', 'volume']]
        df[['open', 'close', 'high', 'low', 'volume']] = df[['open', 'close', 'high', 'low', 'volume']].astype('float')

        df.time = pd.to_datetime(df.time)
        df.set_index(['time'], inplace=True)
        df.index.name = ''  # 处理索引

        # 最新基金数据是3位的
        df['close'].iloc[-1] = float(st['data'][code]['qt'][code][3])

        return df

    def get_price_sina(self, code: str, end_date: Union[str, datetime.date, None] = '',
                       count: int = 10, frequency: str = '60m') -> pd.DataFrame:
        """从新浪接口获取全周期数据
        
        Args:
            code: 股票代码
            end_date: 结束日期
            count: 获取数据的数量
            frequency: 频率，分钟线 5m,15m,30m,60m  日线1d=240m  周线1w=1200m  月线1M=7200m
            
        Returns:
            包含股票数据的DataFrame
        """
        # 转换频率格式
        frequency = frequency.replace('1d', '240m').replace('1w', '1200m').replace('1M', '7200m')
        mcount = count

        # 解析K线周期数
        ts = int(frequency[:-1]) if frequency[:-1].isdigit() else 1

        # 处理结束日期
        if (end_date != '') and (frequency in ['240m', '1200m', '7200m']):
            end_date = pd.to_datetime(end_date) if not isinstance(end_date, datetime.date) else end_date

            # 确定单位
            unit = 4 if frequency == '1200m' else 29 if frequency == '7200m' else 1

            # 计算需要获取的数据量
            count = count + (datetime.datetime.now() - end_date).days // unit

        url = f'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={code}&scale={ts}&ma=5&datalen={count}'
        response = requests.get(url)
        dstr = json.loads(response.content)

        df = pd.DataFrame(dstr, columns=['day', 'open', 'high', 'low', 'close', 'volume'])
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)

        df.day = pd.to_datetime(df.day)
        df.set_index(['day'], inplace=True)
        df.index.name = ''  # 处理索引

        # 处理日线带结束时间的情况
        if (end_date != '') and (frequency in ['240m', '1200m', '7200m']):
            return df[df.index <= end_date][-mcount:]

        return df

    def get_price(self, code: str, end_date: Union[str, datetime.date, None] = '',
                  count: int = 10, frequency: str = '1d', fields: List = None) -> pd.DataFrame:
        """统一的股票数据获取接口
        
        Args:
            code: 股票代码，支持'000001.XSHG'或'sh000001'格式
            end_date: 结束日期
            count: 获取数据的数量
            frequency: 频率，支持'1d'日线,'1w'周线,'1M'月线,'1m','5m','15m','30m','60m'分钟线
            fields: 返回字段，暂未使用
            
        Returns:
            包含股票数据的DataFrame
        """
        if fields is None:
            fields = []

        # 格式化股票代码
        xcode = self._format_code(code)

        # 根据频率选择不同的数据获取方式
        if frequency in ['1d', '1w', '1M']:  # 日线、周线、月线
            try:
                return self.get_price_sina(xcode, end_date=end_date, count=count, frequency=frequency)  # 主力
            except Exception:
                return self.get_price_day_tx(xcode, end_date=end_date, count=count, frequency=frequency)  # 备用

        elif frequency in ['1m', '5m', '15m', '30m', '60m']:  # 分钟线
            if frequency == '1m':
                return self.get_price_min_tx(xcode, end_date=end_date, count=count, frequency=frequency)
            try:
                return self.get_price_sina(xcode, end_date=end_date, count=count, frequency=frequency)  # 主力
            except Exception:
                return self.get_price_min_tx(xcode, end_date=end_date, count=count, frequency=frequency)  # 备用

        # 不支持的频率返回空DataFrame
        return pd.DataFrame()


# 创建一个默认实例，方便直接调用
stock_data = AshareStockData()


# 为了保持向后兼容，提供与原来相同的函数接口
def get_price_day_tx(code, end_date='', count=10, frequency='1d'):
    """腾讯日线数据获取，保持向后兼容"""
    return stock_data.get_price_day_tx(code, end_date, count, frequency)


def get_price_min_tx(code, end_date=None, count=10, frequency='1d'):
    """腾讯分钟线数据获取，保持向后兼容"""
    return stock_data.get_price_min_tx(code, end_date, count, frequency)


def get_price_sina(code, end_date='', count=10, frequency='60m'):
    """新浪数据获取，保持向后兼容"""
    return stock_data.get_price_sina(code, end_date, count, frequency)


def get_price(code, end_date='', count=10, frequency='1d', fields=[]):
    """统一的股票数据获取接口，保持向后兼容"""
    return stock_data.get_price(code, end_date, count, frequency, fields)


if __name__ == '__main__':
    # # 使用示例
    # df = get_price('sh000001', frequency='1d', count=10)  # 支持'1d'日, '1w'周, '1M'月
    # print('上证指数日线行情\n', df)
    #
    # df = get_price('000001.XSHG', frequency='15m', count=10)  # 支持'1m','5m','15m','30m','60m'
    # print('上证指数分钟线\n', df)

    # 面向对象方式使用示例
    stock = AshareStockData()
    df = stock.get_price('sh000001', frequency='1d', count=10)
    print('上证指数日线行情\n', df)
