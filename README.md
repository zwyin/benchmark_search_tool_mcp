# 搜索工具对比评测框架

对比 Claude Code 环境下 5 个搜索工具在 15 个测试场景中的表现。

## 评测工具

| 工具 | 类型 | 特点 |
|------|------|------|
| WebSearch | 内置 | 自带 Claude 结构化总结 |
| web-search-prime | 智谱 MCP | 支持 location(cn/us) 参数 |
| Context7 | MCP | 官方代码文档，零噪音 |
| AnySearch | Skill | 23 个垂直领域，完整全文 |
| web-reader | MCP | 已知 URL 内容提取 |

## 快速开始

```bash
# 评分并生成报告（使用内置评分）
python scorer.py

# LLM-as-Judge 自动评分（需要 ZHIPU_API_KEY）
ZHIPU_API_KEY=xxx python scorer.py --llm-judge

# 运行搜索测试（仅 AnySearch 和 Context7 可通过 CLI 调用）
python run_benchmark.py run

# 运行 + 评分
python run_benchmark.py full
```

## 项目结构

```
.
├── test_cases.json       # 15 个测试用例定义
├── scorer.py             # 评分脚本（手动 + LLM-as-Judge 双模式）
├── run_benchmark.py      # CLI 一键运行
├── report.md             # 评测报告（自动生成）
├── CLAUDE.md             # 项目级搜索策略
└── results/              # 测试结果 JSON
    ├── tc01_websearch.json
    ├── tc01_web-search-prime.json
    ├── ...
    └── scoring_consistency.json  # LLM-Judge 一致性分析
```

## 综合排名

| 排名 | 工具 | 综合均分 | 参与测试数 |
|------|------|----------|-----------|
| 1 | AnySearch | 4.70 | 14 |
| 2 | WebSearch | 4.43 | 14 |
| 3 | web-search-prime | 4.25 | 14 |
| 4 | web-reader | 4.25 | 1 |
| 5 | Context7 | 3.47 | 9 |

## 三句话决策规则

1. **写代码 → Context7；读网页 → web-reader**
2. **要完整 → AnySearch；要快速 → WebSearch**
3. **英文技术 → location=us；垂直领域 → AnySearch（金融/安全），学术用 WebSearch**

## 关键发现

- **WebSearch = web-search-prime**：同一引擎，9 个 TC 全面验证。WebSearch 高 0.18 分（Claude 自动总结加成）
- **Context7 严格限定于编程 API 文档**：Claude Code 插件开发满分(5/5/5/5)，但 CVE 仅 1 分、国内技术 2 分、无法获取 release notes
- **AnySearch 金融垂直是独有能力**：实时价格/分析师评级/EPS 超预期对比，其他工具无法提供
- **学术搜索用 WebSearch**：AnySearch 垂直学术匹配精度差（TC12: 3/3/4/3 vs WebSearch 5/5/5/5）
- **AnySearch token 成本约 10x WebSearch**：深度研究才值得

## 测试覆盖

15 个类别 × 5 个工具 × 4 维度评分 = 52 个有效组合（69% 覆盖率，剩余为工具不适用场景）。47 条 LLM-as-Judge 自动评分验证，avg deviation 0.46 分，排名方向完全一致。
