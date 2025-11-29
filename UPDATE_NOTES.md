# 更新说明

## 更新概述

本项目已从 v1.0 版本升级到 v2.0 版本，主要新增了对短期和长期均值周期的灵活单位选择功能。

## 主要更新内容

### 1. 配置文件 (config.py)

**新增配置项：**
- `DEFAULT_LONG_PERIOD_UNIT`: 默认长期周期单位 (day/month/year)
- `DAY_TO_TRADING_DAYS`: 日转交易日的转换因子
- `MONTH_TO_TRADING_DAYS`: 月转交易日的转换因子
- `YEAR_TO_TRADING_DAYS`: 年转交易日的转换因子

**新增工具函数：**
- `convert_period_to_days()`: 将不同单位的周期转换为交易日
- `get_period_display()`: 获取周期的中文显示文本

### 2. 核心分析模块 (stock_analyzer.py)

**主要改进：**

1. **函数参数扩展**：
   - `calculate_ma_diff()` 函数新增 `long_period_unit` 和 `short_period_unit` 参数
   - `analyze_stocks()` 函数同步更新参数支持

2. **周期转换支持**：
   ```python
   # 自动将用户输入的周期转换为交易日
   long_period_days = convert_period_to_days(long_period, long_period_unit)
   short_period_days = convert_period_to_days(short_period, short_period_unit)
   ```

3. **智能数据检查**：
   ```python
   # 检查股票数据是否足够计算所选周期
   if actual_days_available < required_days:
       print(f"警告: 股票 {ts_code} 数据不足 - 仅 {actual_days_available} 天，需要 {required_days} 天")
       return None
   ```

4. **结果数据增强**：
   - 返回结果中包含原始的周期和单位信息
   - 新增跳过股票数量的统计

### 3. Web应用模块 (app.py)

**API接口更新：**

1. **参数处理增强**：
   - 新增 `long_period_unit` 和 `short_period_unit` 参数接收
   - 完善的参数验证和错误处理

2. **单位验证**：
   ```python
   valid_units = ['day', 'month', 'year']
   if long_period_unit not in valid_units:
       return jsonify({'success': False, 'message': '长期周期单位必须是day、month或year'})
   ```

3. **逻辑优化**：
   - 短期周期不能大于长期周期的验证
   - 最大周期限制（1000个交易日）
   - 结果统计包含跳过股票数量

### 4. 前端界面 (templates/index.html)

**用户界面改进：**

1. **周期选择控件**：
   ```html
   <!-- 短期周期选择 -->
   <div class="period-input-group">
       <input type="number" id="shortPeriod" value="5" min="1" max="100" required>
       <select id="shortPeriodUnit" required>
           <option value="day">日</option>
           <option value="month">月</option>
           <option value="year">年</option>
       </select>
   </div>
   ```

2. **界面布局优化**：
   - 更清晰的参数输入区域
   - 响应式设计，支持移动端
   - 实时参数验证提示

3. **结果展示增强**：
   - 表格新增周期设置列
   - 统计信息包含数据不足股票数量
   - 更友好的用户提示

## 数据流程改进

### v1.0 数据流程
```
用户输入 → 固定周期 → 数据获取 → 计算 → 结果
```

### v2.0 数据流程
```
用户输入 → 周期+单位 → 单位转换 → 数据获取 → 数据检查 → 计算 → 结果
```

## 单位转换规则

| 输入单位 | 转换为交易日 | 说明 |
|---------|-------------|------|
| 日 (day) | 1:1 | 直接使用输入数值 |
| 月 (month) | 1:20 | 假设每月20个交易日 |
| 年 (year) | 1:240 | 假设每年240个交易日 |

## 代码兼容性

### 向后兼容
- 支持 v1.0 版本的所有功能
- 现有配置文件格式保持兼容
- API 接口保持向下兼容

### 新增依赖
- 无新增Python依赖包

## 部署注意事项

1. **配置文件迁移**：
   - 原有的 `config.py` 可以直接使用
   - 建议检查并更新新的配置项

2. **数据清理**：
   - 无需清理原有数据
   - 系统会自动处理历史数据

3. **性能影响**：
   - 新增的单位转换计算几乎不影响性能
   - 数据检查会略微增加处理时间，但提高了结果质量

## 使用建议

### 推荐参数组合

1. **短线策略**：
   - 短期: 5日 / 10日
   - 长期: 20日 / 30日
   - 阈值: 3-5%

2. **中线策略**：
   - 短期: 1月 / 2月
   - 长期: 3月 / 6月
   - 阈值: 5-8%

3. **长线策略**：
   - 短期: 1年 / 2年
   - 长期: 3年 / 5年
   - 阈值: 8-15%

### 注意事项

1. **周期合理性**：短期周期应明显小于长期周期
2. **阈值设置**：根据市场情况调整，牛市可适当降低阈值
3. **数据完整性**：新上市股票可能因数据不足被跳过
4. **API限制**：避免过于频繁的请求，遵守Tushare使用规则

## 故障排除

### 常见问题

**Q: 为什么短期周期不能大于长期周期？**
A: 这是均线分析的基本逻辑，短期均线应该基于更短的时间窗口

**Q: 月和年的转换是否准确？**
A: 这是基于市场平均情况的近似值，实际交易日可能略有不同

**Q: 如何处理数据不足的股票？**
A: 系统会自动跳过并在统计中显示，您可以尝试缩短周期或选择其他股票

**Q: 是否支持自定义转换因子？**
A: 可以在 `config.py` 中修改转换配置

## 下一步计划

- [ ] 支持自定义转换因子的Web界面设置
- [ ] 增加更多技术指标
- [ ] 支持策略回测功能
- [ ] 优化大数据量处理性能

---

**更新时间**: 2024-10-27
**版本**: v2.0
**状态**: 正式发布