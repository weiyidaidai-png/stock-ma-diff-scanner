import pandas as pd
from stock_data import StockDataFetcher
from config import convert_period_to_days

class StockAnalyzer:
    """股票分析器"""

    def __init__(self, fetcher=None):
        self.fetcher = fetcher or StockDataFetcher()

    def calculate_ma_diff(self, ts_code, long_period=20, long_period_unit='day',
                         short_period=5, short_period_unit='day'):
        """计算单只股票的均线差异"""
        try:
            # 将周期转换为交易日
            long_period_days = convert_period_to_days(long_period, long_period_unit)
            short_period_days = convert_period_to_days(short_period, short_period_unit)

            # 获取最近足够多的数据，增加额外的缓冲天数
            days_needed = max(long_period_days, short_period_days) + 20  # 增加缓冲天数
            df = self.fetcher.get_recent_data(ts_code, days_needed)

            if df.empty:
                print(f"警告: 股票 {ts_code} 没有数据")
                return None

            # 检查数据是否足够
            actual_days_available = len(df)
            required_days = max(long_period_days, short_period_days)

            if actual_days_available < required_days:
                print(f"警告: 股票 {ts_code} 数据不足 - 仅 {actual_days_available} 天，需要 {required_days} 天")
                return None

            # 计算长期均值（最近long_period天的平均值）
            recent_long_data = df.tail(long_period_days)
            long_mean = recent_long_data['close'].mean()

            # 计算短期均值（最近short_period天的平均值）
            recent_short_data = df.tail(short_period_days)
            short_mean = recent_short_data['close'].mean()

            # 计算差异百分比
            if long_mean == 0:
                print(f"警告: 股票 {ts_code} 长期均值为0，跳过计算")
# 检查是否有NaN值
            if pd.isna(long_mean) or pd.isna(short_mean):
                print(f"警告: 股票 {ts_code} 计算结果包含NaN值，跳过计算")
                return None
                return None
# 检查差异百分比是否为NaN
            if pd.isna(diff_percent):
                print(f"警告: 股票 {ts_code} 差异百分比计算结果为NaN，跳过计算")
                return None

            diff_percent = ((short_mean - long_mean) / long_mean) * 100

            return {
                'ts_code': ts_code,
                'long_mean': long_mean,
                'short_mean': short_mean,
                'diff_percent': diff_percent,
                'latest_close': recent_long_data['close'].iloc[-1],
                'short_period': short_period,
                'short_period_unit': short_period_unit,
                'long_period': long_period,
                'long_period_unit': long_period_unit
            }
        except Exception as e:
            print(f"分析股票{ts_code}失败: {e}")
            return None

    def analyze_stocks(self, stock_list=None, long_period=20, long_period_unit='day',
                      diff_threshold=5, short_period=5, short_period_unit='day'):
        """批量分析股票"""
        if stock_list is None:
            stock_list = self.fetcher.get_stock_list()

        if stock_list.empty:
            return pd.DataFrame()

        results = []
        total = len(stock_list)
        skipped = 0

        print(f"开始分析 {total} 只股票...")
        print(f"参数设置: 短期周期={short_period}{short_period_unit}, 长期周期={long_period}{long_period_unit}, 阈值={diff_threshold}%")

        for i, (_, stock) in enumerate(stock_list.iterrows()):
            ts_code = stock['ts_code']
            name = stock['name']

            if (i + 1) % 10 == 0:
                print(f"已分析 {i + 1}/{total} 只股票，已跳过 {skipped} 只数据不足的股票")

            result = self.calculate_ma_diff(ts_code, long_period, long_period_unit,
                                          short_period, short_period_unit)

            if result:
                result['name'] = name
                results.append(result)
            else:
                skipped += 1

        # 转换为DataFrame
        df = pd.DataFrame(results)

        if df.empty:
            print(f"分析完成，没有找到符合条件的股票（共跳过 {skipped} 只数据不足的股票）")
            return df

        # 筛选差异大于阈值的股票
        df = df[df['diff_percent'].abs() > diff_threshold]

        # 按差异百分比绝对值从大到小排序
        df = df.sort_values('diff_percent', key=lambda x: x.abs(), ascending=False)

        # 保留需要的列并排序
        df = df[['ts_code', 'name', 'diff_percent', 'latest_close', 'long_mean',
                'short_mean', 'short_period', 'short_period_unit',
                'long_period', 'long_period_unit']]

        print(f"分析完成，找到 {len(df)} 只符合条件的股票（共跳过 {skipped} 只数据不足的股票）")

        return df

    def get_stock_details(self, ts_code, days=60):
        """获取股票详细数据（用于绘制图表）"""
        try:
            df = self.fetcher.get_recent_data(ts_code, days)

            if df.empty:
                return None

            # 计算移动平均线
            df['ma5'] = df['close'].rolling(window=5).mean()
            df['ma20'] = df['close'].rolling(window=20).mean()
            df['ma30'] = df['close'].rolling(window=30).mean()

            # 转换为字典格式，方便JSON序列化
            data = {
                'trade_dates': df['trade_date'].dt.strftime('%Y-%m-%d').tolist(),
                'close_prices': df['close'].tolist(),
                'ma5': df['ma5'].tolist(),
                'ma20': df['ma20'].tolist(),
                'ma30': df['ma30'].tolist(),
                'latest_data': {
                    'close': df['close'].iloc[-1],
                    'ma5': df['ma5'].iloc[-1],
                    'ma20': df['ma20'].iloc[-1],
                    'ma30': df['ma30'].iloc[-1]
                }
            }

            return data
        except Exception as e:
            print(f"获取股票{ts_code}详情失败: {e}")
            return None

    def filter_top_diff_stocks(self, df, top_n=10):
        """筛选差异最大的前N只股票"""
        if df.empty:
            return df

        # 按差异百分比绝对值排序
        df = df.sort_values('diff_percent', key=lambda x: x.abs(), ascending=False)
        return df.head(top_n)

    def get_stock_stats(self, df):
        """获取筛选结果的统计信息"""
        if df.empty:
            return {}

        stats = {
            'total_count': len(df),
            'avg_diff_percent': df['diff_percent'].mean(),
            'max_diff_percent': df['diff_percent'].max(),
            'min_diff_percent': df['diff_percent'].min(),
            'positive_count': len(df[df['diff_percent'] > 0]),
            'negative_count': len(df[df['diff_percent'] < 0])
        }

        return stats

# 测试用例
if __name__ == "__main__":
    from config import validate_config, get_period_display

    if validate_config():
        analyzer = StockAnalyzer()

        # 测试分析单只股票
        print("测试分析单只股票...")
        result = analyzer.calculate_ma_diff('000001.SZ', 20, 'day', 5, 'day')
        if result:
            print(f"股票: {result['ts_code']}")
            print(f"长期均值({get_period_display(result['long_period'], result['long_period_unit'])}): {result['long_mean']:.2f}")
            print(f"短期均值({get_period_display(result['short_period'], result['short_period_unit'])}): {result['short_mean']:.2f}")
            print(f"差异百分比: {result['diff_percent']:.2f}%")

        # 测试批量分析（只分析前5只股票）
        print("\n测试批量分析（前5只股票）...")
        stock_list = analyzer.fetcher.get_stock_list().head(5)
        result_df = analyzer.analyze_stocks(stock_list, 20, 'day', 3, 5, 'day')

        if not result_df.empty:
            print("\n筛选结果:")
            print(result_df.to_string(index=False))

            # 测试统计信息
            stats = analyzer.get_stock_stats(result_df)
            print("\n统计信息:")
            for key, value in stats.items():
                print(f"{key}: {value}")

        # 测试获取股票详情
        print("\n测试获取股票详情...")
        details = analyzer.get_stock_details('000001.SZ', 30)
        if details:
            print(f"获取到 {len(details['trade_dates'])} 天数据")
            print(f"最新收盘价: {details['latest_data']['close']:.2f}")
            print(f"最新5日均线: {details['latest_data']['ma5']:.2f}")