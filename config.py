# 配置文件
# 请在此处配置您的tushare API token
# 您可以在https://tushare.pro/register免费注册获取

# 默认配置
DEFAULT_SHORT_PERIOD = 5  # 默认短期均值周期
DEFAULT_SHORT_PERIOD_UNIT = 'day'  # 默认短期周期单位 (day/month/year)
DEFAULT_LONG_PERIOD = 20  # 默认长期均值周期
DEFAULT_LONG_PERIOD_UNIT = 'day'  # 默认长期周期单位 (day/month/year)
DEFAULT_DIFF_THRESHOLD = 5  # 默认差异百分比阈值（%）
API_CALL_DELAY = 0.1  # API调用延迟（秒），避免超过tushare免费版限制

# 单位转换配置（转换为交易日）
DAY_TO_TRADING_DAYS = 1  # 1天=1个交易日
MONTH_TO_TRADING_DAYS = 20  # 1个月≈20个交易日
YEAR_TO_TRADING_DAYS = 240  # 1年≈240个交易日

# 用户需要配置的参数
TUSHARE_TOKEN = '2876ea85cb005fb5fa17c809a98174f2d5aae8b1f830110a5ead6211'  # 请在此处填入您的tushare API token

def validate_config():
    """验证配置"""
    if not TUSHARE_TOKEN:
        print("警告：请在config.py中配置您的tushare API token")
        print("您可以在https://tushare.pro/register免费注册获取")
        return False
    return True

def convert_period_to_days(period, unit):
    """将周期转换为交易日"""
    unit_map = {
        'day': DAY_TO_TRADING_DAYS,
        'month': MONTH_TO_TRADING_DAYS,
        'year': YEAR_TO_TRADING_DAYS
    }
    multiplier = unit_map.get(unit.lower(), DAY_TO_TRADING_DAYS)
    return period * multiplier

def get_period_display(period, unit):
    """获取周期的显示文本"""
    unit_map = {
        'day': '天',
        'month': '月',
        'year': '年'
    }
    return f"{period}{unit_map.get(unit.lower(), '天')}"