# benchmark_search_tool_mcp 项目配置

## 搜索工具选择策略

基于 2026-05-18 的 5 工具 × 8 测试用例对比评测结论。评分方法：LLM-as-Judge (GLM-5.1)，4 维度 1-5 分。

### 决策规则（按查询类型匹配）

| 查询类型 | 首选工具 | 备选 | 原因 |
|----------|----------|------|------|
| 编程库/框架 API 文档 | **Context7** | WebSearch | 零噪音官方代码，1.3s，~650 tokens |
| 已知 URL 提取内容 | **web-reader** | AnySearch extract | 完整页面提取（需过滤 metadata 噪音） |
| CVE/股票代码/学术等结构化标识符 | **AnySearch 垂直领域** | WebSearch | security/finance/academic 等独有能力 |
| 深度研究/行业分析/政策追踪 | **AnySearch 通用** | WebSearch | 完整全文 ~12K tokens，信息密度 10x WebSearch |
| 英文官方文档/英文社区 | **web-search-prime (location=us)** | AnySearch | location 参数显著提升英文结果质量 |
| 快速概要/中文日常搜索 | **WebSearch** | web-search-prime | 自带 Claude 总结，~1.25K tokens，最佳平衡 |
| 代码调试/报错排查 | **WebSearch** | web-search-prime | 中文社区方案全面，Context7 不适合此类场景 |

### 关键约束

1. **WebSearch = web-search-prime**：同一引擎，择一即可。WebSearch 有 Claude 总结，web-search-prime 有 location 参数。不要同时调用两者。
2. **Context7 仅限编程文档**：不适合代码调试（OS 级运行时错误）、不适合国内技术（智谱 GLM 等）、不适合通用搜索。
3. **AnySearch token 成本高**：~12K tokens/查询（WebSearch 的 10 倍），仅在需要完整信息时使用。
4. **web-reader 有噪音**：输出含 CSS/JS/favicon 等 metadata，Agent 需过滤后才高效。

### 不用的工具组合

- 不要同时调用 WebSearch 和 web-search-prime（同引擎，浪费 token）
- 不要用 Context7 查国内技术（覆盖不到）
- 不要用 web-reader 做 URL 发现（它只能提取已知 URL）

## 项目文件说明

- `report.md` — 完整评测报告（9 章 + 附录）
- `results/` — 原始测试结果 JSON
- `scorer.py` — 评分脚本（可复用于后续迭代）
- `test_cases.json` — 测试用例定义
