from flask import Flask, render_template, request, jsonify
import threading
import time
from stock_analyzer import StockAnalyzer
from config import validate_config, DEFAULT_LONG_PERIOD, DEFAULT_LONG_PERIOD_UNIT, \
    DEFAULT_DIFF_THRESHOLD, DEFAULT_SHORT_PERIOD, DEFAULT_SHORT_PERIOD_UNIT, \
    convert_period_to_days, get_period_display

app = Flask(__name__)

# 全局变量
analyzer = None
analysis_result = None
analysis_status = 'idle'  # idle, running, completed, error
analysis_progress = 0

def initialize_analyzer():
    """初始化股票分析器"""
    global analyzer
    if validate_config():
        analyzer = StockAnalyzer()
        return True
    else:
        return False

def background_analysis(stock_list, long_period, long_period_unit,
                       diff_threshold, short_period, short_period_unit):
    """后台分析股票"""
    global analysis_result, analysis_status, analysis_progress

    try:
        analysis_status = 'running'
        analysis_progress = 0

        if analyzer is None:
            if not initialize_analyzer():
                raise Exception("无法初始化股票分析器，请检查tushare API token配置")

        # 开始分析
        total = len(stock_list)
        results = []
        skipped_count = 0

        for i, (_, stock) in enumerate(stock_list.iterrows()):
            ts_code = stock['ts_code']
            name = stock['name']

            # 更新进度（确保进度平滑更新）
            current_progress = int((i + 1) / total * 100)
            if current_progress != analysis_progress:
                analysis_progress = current_progress

            # 分析单只股票
            result = analyzer.calculate_ma_diff(ts_code, long_period, long_period_unit,
                                              short_period, short_period_unit)

            if result:
                result['name'] = name
                results.append(result)
            else:
                skipped_count += 1

            # 小延迟，避免API限制
            time.sleep(0.1)

        # 处理分析结果
        import pandas as pd
        df = pd.DataFrame(results)

        if not df.empty:
            # 筛选差异大于阈值的股票
            df = df[df['diff_percent'].abs() > diff_threshold]

            # 按差异百分比绝对值从大到小排序
            df = df.sort_values('diff_percent', key=lambda x: x.abs(), ascending=False)

            # 保留需要的列并排序
            df = df[['ts_code', 'name', 'diff_percent', 'latest_close', 'long_mean',
                    'short_mean', 'short_period', 'short_period_unit',
                    'long_period', 'long_period_unit']]

        # 添加跳过统计
        if hasattr(df, 'skipped_count'):
            df.skipped_count = skipped_count
        else:
            df = df.assign(skipped_count=skipped_count)

        analysis_result = df
        analysis_status = 'completed'

    except Exception as e:
        print(f"分析失败: {e}")
        analysis_status = 'error'
        analysis_result = str(e)

@app.route('/')
def index():
    """首页"""
    return render_template('index.html',
                         default_long_period=DEFAULT_LONG_PERIOD,
                         default_long_period_unit=DEFAULT_LONG_PERIOD_UNIT,
                         default_diff_threshold=DEFAULT_DIFF_THRESHOLD,
                         default_short_period=DEFAULT_SHORT_PERIOD,
                         default_short_period_unit=DEFAULT_SHORT_PERIOD_UNIT)

@app.route('/api/configure', methods=['POST'])
def configure():
    """配置分析参数并开始分析"""
    global analysis_result, analysis_status, analysis_progress

    try:
        # 获取参数
        long_period = int(request.form.get('long_period', DEFAULT_LONG_PERIOD))
        long_period_unit = request.form.get('long_period_unit', DEFAULT_LONG_PERIOD_UNIT)
        diff_threshold = float(request.form.get('diff_threshold', DEFAULT_DIFF_THRESHOLD))
        short_period = int(request.form.get('short_period', DEFAULT_SHORT_PERIOD))
        short_period_unit = request.form.get('short_period_unit', DEFAULT_SHORT_PERIOD_UNIT)

        # 验证参数
        if long_period <= 0:
            return jsonify({'success': False, 'message': '长期周期必须大于0'})

        if short_period <= 0:
            return jsonify({'success': False, 'message': '短期周期必须大于0'})

        if diff_threshold < 0 or diff_threshold > 100:
            return jsonify({'success': False, 'message': '差异阈值应在0-100之间'})

        # 验证单位合法性
        valid_units = ['day', 'month', 'year']
        if long_period_unit not in valid_units:
            return jsonify({'success': False, 'message': '长期周期单位必须是day、month或year'})

        if short_period_unit not in valid_units:
            return jsonify({'success': False, 'message': '短期周期单位必须是day、month或year'})

        # 转换为实际交易日进行合理性检查
        long_period_days = convert_period_to_days(long_period, long_period_unit)
        short_period_days = convert_period_to_days(short_period, short_period_unit)

        if long_period_days > 1000:  # 限制最大周期为1000天
            return jsonify({'success': False, 'message': '长期周期不能超过约4年（1000个交易日）'})

        if short_period_days > long_period_days:
            return jsonify({'success': False, 'message': '短期周期不能大于长期周期'})

        # 初始化分析器
        if analyzer is None:
            if not initialize_analyzer():
                return jsonify({'success': False, 'message': '无法初始化股票分析器，请检查tushare API token配置'})

        # 获取股票列表
        stock_list = analyzer.fetcher.get_stock_list()
        if stock_list.empty:
            return jsonify({'success': False, 'message': '无法获取股票列表'})

        # 重置状态
        analysis_result = None
        analysis_status = 'running'
        analysis_progress = 0

        # 启动后台分析线程
        thread = threading.Thread(target=background_analysis,
                                args=(stock_list, long_period, long_period_unit,
                                      diff_threshold, short_period, short_period_unit))
        thread.daemon = True
        thread.start()

        return jsonify({'success': True,
                       'total_stocks': len(stock_list),
                       'short_period_days': short_period_days,
                       'long_period_days': long_period_days})

    except Exception as e:
        return jsonify({'success': False, 'message': f'配置失败: {str(e)}'})

@app.route('/api/status')
def get_status():
    """获取分析状态"""
    global analysis_status, analysis_progress

    return jsonify({
        'status': analysis_status,
        'progress': analysis_progress
    })

@app.route('/api/results')
def get_results():
    """获取分析结果"""
    global analysis_result, analysis_status

    if analysis_status != 'completed':
        return jsonify({'success': False, 'message': '分析尚未完成'})

    if analysis_result is None or analysis_result.empty:
        return jsonify({'success': False, 'message': '没有找到符合条件的股票'})

    # 计算统计信息
    total_count = len(analysis_result)
    up_count = len(analysis_result[analysis_result['diff_percent'] > 0])
    down_count = len(analysis_result[analysis_result['diff_percent'] < 0])
    avg_diff = analysis_result['diff_percent'].mean()

    # 获取跳过的股票数量
    skipped_count = getattr(analysis_result, 'skipped_count', 0)

    # 转换为JSON格式
    results = {
        'stocks': analysis_result.to_dict('records'),
        'count': total_count,
        'statistics': {
            'total': total_count,
            'up': up_count,
            'down': down_count,
            'avg_diff': float(avg_diff),
            'skipped': skipped_count
        }
    }

    return jsonify({'success': True, 'data': results})

@app.route('/api/stock_details/<ts_code>')
def get_stock_details(ts_code):
    """获取股票详细数据"""
    try:
        if analyzer is None:
            if not initialize_analyzer():
                return jsonify({'success': False, 'message': '无法初始化股票分析器'})

        details = analyzer.get_stock_details(ts_code, 60)
        if details is None:
            return jsonify({'success': False, 'message': '无法获取股票详情'})

        return jsonify({'success': True, 'data': details})

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取股票详情失败: {str(e)}'})

@app.route('/api/stock_list')
def get_stock_list():
    """获取股票列表（用于搜索）"""
    try:
        if analyzer is None:
            if not initialize_analyzer():
                return jsonify({'success': False, 'message': '无法初始化股票分析器'})

        stock_list = analyzer.fetcher.get_stock_list()
        if stock_list.empty:
            return jsonify({'success': False, 'message': '无法获取股票列表'})

        # 转换为JSON格式
        stocks = stock_list[['ts_code', 'name']].to_dict('records')

        return jsonify({'success': True, 'data': stocks})

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取股票列表失败: {str(e)}'})

@app.route('/api/reset')
def reset_analysis():
    """重置分析状态"""
    global analysis_result, analysis_status, analysis_progress

    analysis_result = None
    analysis_status = 'idle'
    analysis_progress = 0

    return jsonify({'success': True, 'message': '分析状态已重置'})

if __name__ == '__main__':
    # 初始化分析器
    initialize_analyzer()

    print("A股股票均线差异筛选工具已启动")
    print("请访问 http://localhost:5000")
    print("首次使用请在 config.py 中配置您的 tushare API token")

    app.run(debug=True)