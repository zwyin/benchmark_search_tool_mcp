# benchmark_search_tool_mcp 项目配置

## 搜索工具选择策略

基于 2026-05-19 的 5 工具 × 15 测试用例 × 52 组合对比评测结论。评分方法：LLM-as-Judge (GLM-4-Flash)，4 维度 1-5 分。LLM-Judge 验证一致（avg deviation 0.46，47 条评分）。

### 决策规则（按查询类型匹配）

| 查询类型 | 首选工具 | 备选 | 原因 |
|----------|----------|------|------|
| 编程库/框架 API 文档 | **Context7** | WebSearch | 零噪音官方代码，1.3s，~650 tokens |
| 已知 URL 提取内容 | **web-reader** | AnySearch extract | 完整页面提取（需过滤 metadata 噪音） |
| CVE/股票代码等结构化金融数据 | **AnySearch 垂直** | 无替代 | 实时价格/分析师评级/EPS，其他工具无法提供 |
| 深度研究/行业分析/政策追踪 | **AnySearch 通用** | WebSearch | 完整全文 ~12K tokens，信息密度 10x WebSearch |
| 学术论文搜索 | **WebSearch** | AnySearch 垂直 | WebSearch 匹配精准(arxiv/OpenReview)，AnySearch 垂直学术匹配差 |
| 英文技术选型对比 | **WebSearch (us)** | AnySearch | Claude 自动生成对比表格，社区讨论全面 |
| 快速概要/中文日常搜索 | **WebSearch** | web-search-prime | 自带 Claude 总结，~1.25K tokens，最佳平衡 |
| 代码调试/报错排查 | **WebSearch** | web-search-prime | 中文社区方案全面，Context7 不适合此类场景 |
| 国内开源生态（Dify/智谱等） | **AnySearch** | WebSearch | 直接获取 GitHub Release 全文 |

### 关键约束

1. **WebSearch = web-search-prime**：同一引擎，择一即可。WebSearch 有 Claude 总结，web-search-prime 有 location 参数。不要同时调用两者。
2. **Context7 仅限编程文档**：不适合代码调试（OS 级运行时错误）、不适合国内技术（智谱 GLM 等）、不适合技术选型对比（只返回单库文档）、不适合版本追踪/release notes（TC14: 只返回 API 文档而非 changelog）。特定项目文档查询满分（TC03 Claude Code 插件: 5/5/5/5）。
3. **学术搜索用 WebSearch**：AnySearch 垂直学术搜索查询匹配精度差（TC12: WebSearch 5/5/5/5 vs AnySearch 3/3/4/3）。
4. **AnySearch token 成本高**：~12K tokens/查询（WebSearch 的 10 倍），仅在需要完整信息时使用。
5. **web-reader 有噪音**：输出含 CSS/JS/favicon 等 metadata，Agent 需过滤后才高效。

### 不用的工具组合

- 不要同时调用 WebSearch 和 web-search-prime（同引擎，浪费 token）
- 不要用 Context7 查国内技术（覆盖不到）或做技术选型对比（只返回单库文档）
- 不要用 AnySearch 垂直搜索查学术论文（匹配精度差，用 WebSearch 替代）
- 不要用 web-reader 做 URL 发现（它只能提取已知 URL）

## 项目文件说明

- `report.md` — 完整评测报告（8 章 + 附录 + LLM-Judge 一致性验证）
- `results/` — 原始测试结果 JSON（47 个文件，52 个工具-TC 组合）
- `scorer.py` — 评分脚本（手动 + LLM-as-Judge 双模式）
- `test_cases.json` — 测试用例定义（15 个 TC，12 个类别）
- `run_benchmark.py` — 一键运行脚本
