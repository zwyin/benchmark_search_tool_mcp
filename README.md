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
| 1 | AnySearch | 4.67 | 10 |
| 2 | web-search-prime | 4.38 | 6 |
| 3 | Context7 | 4.38 | 5 |
| 4 | WebSearch | 4.35 | 12 |
| 5 | web-reader | 4.25 | 1 |

## 三句话决策规则

1. **写代码 → Context7；读网页 → web-reader**
2. **要完整 → AnySearch；要快速 → WebSearch**
3. **英文技术 → location=us；垂直领域 → AnySearch（金融/安全），学术用 WebSearch**

## 测试覆盖

15 个类别：国内新闻、技术文档、开源社区、垂直领域、行业研究、代码调试、国内技术、URL提取、英文技术、多语言查询、实时数据、学术搜索、深度代码文档、国内生态、金融垂直。

35 个工具-TC 组合，4 维度评分（relevance/completeness/accuracy/usability_for_agent），LLM-as-Judge 验证一致。
