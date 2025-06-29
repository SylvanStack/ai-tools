"""
decimal 工具类，提供精确的十进制数学运算
"""
from decimal import Decimal, ROUND_HALF_UP, getcontext


class DecimalUtils:
    """
    Decimal工具类，提供精确的十进制数学运算
    所有方法均为静态方法，遵循单一职责原则
    """

    # 设置全局精度
    DEFAULT_PRECISION = 10
    getcontext().prec = DEFAULT_PRECISION

    @staticmethod
    def to_decimal(value):
        """
        将输入值转换为Decimal类型
        
        Args:
            value: 需要转换的值，可以是数字或字符串
            
        Returns:
            Decimal: 转换后的Decimal对象
        """
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))

    @staticmethod
    def add(a, b, scale=None):
        """
        精确加法
        
        Args:
            a: 第一个加数
            b: 第二个加数
            scale: 结果保留的小数位数，默认为None不进行四舍五入
            
        Returns:
            Decimal: 加法结果
        """
        result = DecimalUtils.to_decimal(a) + DecimalUtils.to_decimal(b)
        return DecimalUtils.round(result, scale) if scale is not None else result

    @staticmethod
    def subtract(a, b, scale=None):
        """
        精确减法
        
        Args:
            a: 被减数
            b: 减数
            scale: 结果保留的小数位数，默认为None不进行四舍五入
            
        Returns:
            Decimal: 减法结果
        """
        result = DecimalUtils.to_decimal(a) - DecimalUtils.to_decimal(b)
        return DecimalUtils.round(result, scale) if scale is not None else result

    @staticmethod
    def multiply(a, b, scale=None):
        """
        精确乘法
        
        Args:
            a: 第一个因数
            b: 第二个因数
            scale: 结果保留的小数位数，默认为None不进行四舍五入
            
        Returns:
            Decimal: 乘法结果
        """
        result = DecimalUtils.to_decimal(a) * DecimalUtils.to_decimal(b)
        return DecimalUtils.round(result, scale) if scale is not None else result

    @staticmethod
    def divide(a, b, scale=None):
        """
        精确除法
        
        Args:
            a: 被除数
            b: 除数
            scale: 结果保留的小数位数，默认为None不进行四舍五入
            
        Returns:
            Decimal: 除法结果
            
        Raises:
            ZeroDivisionError: 当除数为0时抛出
        """
        if DecimalUtils.to_decimal(b) == Decimal('0'):
            raise ZeroDivisionError("除数不能为0")

        result = DecimalUtils.to_decimal(a) / DecimalUtils.to_decimal(b)
        return DecimalUtils.round(result, scale) if scale is not None else result

    @staticmethod
    def round(value, scale=2):
        """
        标准四舍五入
        
        Args:
            value: 需要四舍五入的数值
            scale: 保留的小数位数，默认为2
            
        Returns:
            Decimal: 四舍五入后的结果
        """
        decimal_value = DecimalUtils.to_decimal(value)
        return decimal_value.quantize(Decimal('0.' + '0' * scale), rounding=ROUND_HALF_UP)

    @staticmethod
    def to_float(value, scale=None):
        """
        将Decimal转换为float，可选择是否进行四舍五入
        
        Args:
            value: 需要转换的值
            scale: 保留的小数位数，默认为None不进行四舍五入
            
        Returns:
            float: 转换后的浮点数
        """
        decimal_value = DecimalUtils.to_decimal(value)
        if scale is not None:
            decimal_value = DecimalUtils.round(decimal_value, scale)
        return float(decimal_value)


if __name__ == '__main__':
    # 测试用例
    print("加法测试:", DecimalUtils.add(1.1, 2.2, 2))  # 应为3.30
    print("减法测试:", DecimalUtils.subtract(1.1, 0.2, 2))  # 应为0.90
    print("乘法测试:", DecimalUtils.multiply(1.1, 2.2, 2))  # 应为2.42
    print("除法测试:", DecimalUtils.divide(1.1, 2, 2))  # 应为0.55
    print("四舍五入测试:", DecimalUtils.round(1.235, 2))  # 应为1.24
    print("四舍五入测试:", DecimalUtils.round(1.5, 0))  # 应为2
    print("四舍五入测试:", DecimalUtils.round(2.5, 0))  # 应为3
