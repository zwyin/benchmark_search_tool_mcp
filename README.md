# Search Tool Benchmark for Claude Code

Comparative evaluation of 5 search tools across 15 test scenarios in the Claude Code environment.

[中文版](docs/README_CN.md) | [Full Report](docs/REPORT.md) | [Tool Selection Guide](docs/TOOL_SELECTION_GUIDE.md) | [Changelog](docs/CHANGELOG.md)

## Evaluated Tools

| Tool | Type | Key Feature |
|------|------|-------------|
| WebSearch | Built-in | Auto-summarized by Claude |
| web-search-prime | MCP Plugin | `location` parameter (cn/us) |
| Context7 | MCP Plugin | Official code docs, zero noise |
| AnySearch | Skill Plugin | 23 vertical domains, full-text articles |
| web-reader | MCP Plugin | Known URL content extraction |

## Quick Start

```bash
# Score and generate report (using built-in scores)
python scorer.py

# LLM-as-Judge auto-scoring (requires ZHIPU_API_KEY)
ZHIPU_API_KEY=xxx python scorer.py --llm-judge

# Run search tests (only AnySearch and Context7 are callable via CLI)
python run_benchmark.py run

# Run + score
python run_benchmark.py full
```

## Reproducing This Setup

To replicate this evaluation environment in your Claude Code setup:

### 1. WebSearch (Built-in, No Installation)

Available by default in Claude Code. No configuration needed.

### 2. web-search-prime (Zhipu MCP)

This is the official search MCP from [Zhipu AI (BigModel.cn)](https://open.bigmodel.cn). Add to your Claude Code MCP config:

```json
// ~/.claude.json → mcpServers
"web-search-prime": {
  "type": "http",
  "url": "https://open.bigmodel.cn/api/mcp/web_search_prime/mcp",
  "headers": {
    "Authorization": "Bearer YOUR_ZHIPU_API_KEY"
  }
}
```

Get your API key at [open.bigmodel.cn](https://open.bigmodel.cn) (free tier available). This MCP is included with Zhipu Coding Plan subscriptions.

### 3. Context7 (MCP Plugin)

Install via Claude Code plugin marketplace or add manually:

```json
// ~/.claude.json → mcpServers
"context7": {
  "type": "http",
  "url": "https://mcp.context7.com/mcp"
}
```

No API key required. Free to use. Docs: [context7.com](https://context7.com)

### 4. AnySearch (Skill Plugin)

Install via the `/anysearch` skill. Requires an API key from [Z.ai](https://z.ai). Supports 23 vertical domains including finance, academic, and security.

### 5. web-reader (MCP Plugin)

Install via Claude Code plugin marketplace or add manually:

```json
// ~/.claude.json → mcpServers
"web-reader": {
  "type": "http",
  "url": "https://mcp.web-reader.com/mcp"
}
```

No API key required for basic usage.

### Verifying Your Setup

After installation, run `python run_benchmark.py run` to test that all tools are accessible.

## Project Structure

```
.
├── test_cases.json          # 15 test case definitions
├── scorer.py                # Scoring script (built-in + LLM-as-Judge dual mode)
├── run_benchmark.py         # CLI runner
├── search_selector.py       # Query→tool recommendation engine
├── report.md                # Full evaluation report (auto-generated, Chinese)
├── 搜索工具选择指南.md       # Tool selection guide (Chinese)
├── docs/
│   ├── TOOL_SELECTION_GUIDE.md  # Tool selection guide (English)
│   └── CHANGELOG.md             # Iteration summary (English)
├── CLAUDE.md                # Project-level search strategy
└── results/                 # Test result JSON files
    ├── tc01_websearch.json
    ├── tc01_web-search-prime.json
    ├── ...
    └── scoring_consistency.json
```

## Overall Rankings

| Rank | Tool | Avg Score | Tests |
|------|------|-----------|-------|
| 1 | AnySearch | 4.70 | 14 |
| 2 | WebSearch | 4.43 | 14 |
| 3 | web-search-prime | 4.25 | 14 |
| 4 | web-reader | 4.25 | 1 |
| 5 | Context7 | 3.47 | 9 |

## Three-Line Decision Rule

1. **Writing code** → Context7; **reading pages** → web-reader
2. **Need completeness** → AnySearch; **need speed** → WebSearch
3. **English tech** → location=us; **Vertical domains** → AnySearch (finance/security); **Academic** → WebSearch

## Key Findings

- **WebSearch = web-search-prime**: Same engine confirmed across 9 test cases. WebSearch scores +0.18 higher (Claude auto-summary bonus).
- **Context7 is strictly for programming API docs**: Claude Code plugin docs scored 5/5/5/5, but CVE search scored 1/1/2/1, domestic tech scored 2/1/3/2, and release notes scored 2/1/3/2.
- **AnySearch finance vertical is a unique capability**: Real-time stock prices, analyst ratings, EPS surprise comparisons — no other tool provides structured financial data.
- **Use WebSearch for academic search**: AnySearch academic vertical has poor query matching (TC12: 3/3/4/3 vs WebSearch 5/5/5/5).
- **AnySearch token cost is ~10x WebSearch**: Only worthwhile for deep research.

## Test Coverage

15 categories × 5 tools × 4-dimension scoring = 52 valid combinations (69% coverage; remaining are tool-not-applicable scenarios). 47 LLM-as-Judge auto-scores validated, avg deviation 0.46 points, ranking direction fully consistent.

## Tool Recommendation Engine

`search_selector.py` provides programmatic tool selection:

```python
from search_selector import recommend_tool, format_recommendation

rec = recommend_tool("Next.js middleware configuration")
print(format_recommendation(rec))
# → Primary: Context7 (code docs, zero noise)
# → Fallback: WebSearch
```

Supports 7 intent types (code, search, extract, research, finance, academic, security), automatic language detection (zh/en), and depth-aware recommendations (quick/deep).

## License

MIT
