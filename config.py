# 配置文件
# 请在此处配置您的tushare API token
# 您可以在https://tushare.pro/register免费注册获取

# 默认配置
DEFAULT_LONG_PERIOD = 20  # 默认长期均值周期（天）
DEFAULT_DIFF_THRESHOLD = 5  # 默认差异百分比阈值（%）
API_CALL_DELAY = 0.1  # API调用延迟（秒），避免超过tushare免费版限制

# 用户需要配置的参数
TUSHARE_TOKEN = ''  # 请在此处填入您的tushare API token

# 验证配置
def validate_config():
    if not TUSHARE_TOKEN:
        print("警告：请在config.py中配置您的tushare API token")
        print("您可以在https://tushare.pro/register免费注册获取")
        return False
    return True