# A股股票均线差异筛选工具

基于Python和Flask的A股股票均线差异筛选工具，支持用户自由选择短期和长期均值的单位（年、月、日）。

## 功能特性

### 核心功能
- 🔄 **灵活周期选择**: 支持日、月、年三种时间单位的短期和长期均值周期
- 📊 **智能数据分析**: 自动计算股票的短期均值与长期均值之间的差异
- 🎯 **阈值筛选**: 根据用户设定的差异百分比阈值筛选符合条件的股票
- 📈 **涨跌统计**: 自动统计上涨和下跌的股票数量
- 🎨 **直观界面**: 简洁的Web界面，支持实时进度显示和结果展示
- 📱 **响应式设计**: 支持移动端访问

### 新增功能
- **多单位支持**: 短期和长期周期均可选择日、月、年三种单位
- **智能数据检查**: 自动跳过数据不足的股票
- **参数验证**: 完善的参数验证和错误提示
- **周期转换**: 自动将月/年转换为交易日进行计算
- **统计优化**: 新增数据不足股票的统计信息

## 技术栈

- **后端**: Python 3.8+, Flask
- **数据来源**: Tushare Pro API
- **前端**: HTML5, CSS3, JavaScript, ECharts
- **数据处理**: Pandas

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

### Tushare API Token
1. 访问 [Tushare Pro](https://tushare.pro/register) 注册账号
2. 在 `config.py` 文件中配置您的 API token：

```python
# config.py
TUSHARE_TOKEN = 'your_tushare_api_token_here'
```

### 默认配置

```python
DEFAULT_SHORT_PERIOD = 5          # 默认短期周期
DEFAULT_SHORT_PERIOD_UNIT = 'day' # 默认短期单位 (day/month/year)
DEFAULT_LONG_PERIOD = 20          # 默认长期周期
DEFAULT_LONG_PERIOD_UNIT = 'day'  # 默认长期单位 (day/month/year)
DEFAULT_DIFF_THRESHOLD = 5        # 默认差异阈值 (%)
```

## 使用方法

### 启动应用

```bash
python run.py
```

或

```bash
python app.py
```

应用将在 http://localhost:5000 启动。

### 使用界面

1. **配置参数**：
   - 短期均值周期：输入数字 + 选择单位（日/月/年）
   - 长期均值周期：输入数字 + 选择单位（日/月/年）
   - 差异百分比阈值：设置筛选的差异阈值（0-100%）

2. **开始筛选**：点击"开始筛选"按钮

3. **查看结果**：
   - 实时显示筛选进度
   - 筛选完成后显示结果列表
   - 点击股票代码可查看价格走势图
   - 查看统计信息（总数量、上涨/下跌数量、数据不足股票数）

## API 接口

### POST /api/configure
配置分析参数并开始分析

**参数**：
- `short_period`: 短期周期数值
- `short_period_unit`: 短期周期单位 (day/month/year)
- `long_period`: 长期周期数值
- `long_period_unit`: 长期周期单位 (day/month/year)
- `diff_threshold`: 差异百分比阈值

**返回**：
```json
{
  "success": true,
  "total_stocks": 3800,
  "short_period_days": 5,
  "long_period_days": 20
}
```

### GET /api/status
获取分析状态

**返回**：
```json
{
  "status": "running",
  "progress": 50
}
```

### GET /api/results
获取分析结果

**返回**：
```json
{
  "success": true,
  "data": {
    "stocks": [...],
    "count": 150,
    "statistics": {
      "total": 150,
      "up": 80,
      "down": 70,
      "avg_diff": 3.5,
      "skipped": 25
    }
  }
}
```

## 项目结构

```
stock_ma_diff_tool2_new/
├── app.py                 # Flask 应用主文件
├── config.py              # 配置文件
├── stock_analyzer.py      # 股票分析核心逻辑
├── stock_data.py          # 股票数据获取模块
├── run.py                 # 应用启动文件
├── requirements.txt       # 依赖列表
├── templates/
│   └── index.html        # 前端界面模板
└── __pycache__/          # Python 缓存目录
```

## 核心算法

### 周期转换
```python
# 单位转换配置
DAY_TO_TRADING_DAYS = 1      # 1天=1个交易日
MONTH_TO_TRADING_DAYS = 20   # 1个月≈20个交易日
YEAR_TO_TRADING_DAYS = 240   # 1年≈240个交易日
```

### 差异计算
```python
# 计算差异百分比
diff_percent = ((short_mean - long_mean) / long_mean) * 100
```

## 注意事项

1. **API 限制**: Tushare 免费版有访问次数限制，请合理使用
2. **数据质量**: 部分股票可能因上市时间不足导致数据不完整，系统会自动跳过
3. **网络稳定性**: 确保网络连接稳定，避免数据获取失败
4. **参数设置**: 短期周期应小于长期周期，建议根据实际需求调整参数

## 更新日志

### v2.0 (当前版本)
- ✨ 新增短期和长期周期的单位选择功能
- ✨ 支持日、月、年三种时间单位
- ✨ 新增智能数据不足检查和跳过功能
- ✨ 优化前端界面，支持更灵活的参数配置
- ✨ 完善参数验证和错误提示
- ✨ 新增统计信息展示（数据不足股票数量）
- ✨ 优化后端API接口设计

### v1.0
- 📊 基本的均线差异计算功能
- 🎯 基于固定周期的筛选功能
- 📈 基础的涨跌统计
- 🎨 简单的Web界面

## License

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。