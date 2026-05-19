# Search Tool Selection Guide

Based on a 5-tool × 15-test-case × 52-combination evaluation (2026-05-19). Scoring: LLM-as-Judge (GLM-4-Flash), 4 dimensions, 1-5 scale. Judge-Agent deviation: avg 0.46 across 47 scored results.

## Overall Rankings

1. **AnySearch** 4.70 — Highest information density; unique finance/security verticals
2. **WebSearch** 4.43 — Claude summary bonus; best for quick overviews
3. **web-search-prime** 4.25 — Same engine, no summary; `location` param is the differentiator
4. **web-reader** 4.25 — URL extraction only
5. **Context7** 3.47 — Precise for programming docs but narrow scope

## Decision Rules (by Query Type)

| Query Type | Primary Tool | Fallback | Reason |
|------------|-------------|----------|--------|
| Programming library/framework API docs | **Context7** | WebSearch | Zero-noise official code snippets, ~1.3s, ~650 tokens |
| Extract content from a known URL | **web-reader** | AnySearch extract | Full page extraction (filter metadata noise) |
| CVE / stock tickers / structured financial data | **AnySearch vertical** | No alternative | Real-time prices, analyst ratings, EPS — other tools can't provide this |
| Deep research / industry analysis / policy tracking | **AnySearch general** | WebSearch | Full article text ~12K tokens, 10x information density vs WebSearch |
| Academic paper search | **WebSearch** | AnySearch vertical | WebSearch matches arXiv/OpenReview precisely; AnySearch academic vertical has poor query matching |
| English tech comparison / selection | **WebSearch (us)** | AnySearch | Claude auto-generates comparison tables; comprehensive community discussions |
| Quick summary / general search | **WebSearch** | web-search-prime | Built-in Claude summary, ~1.25K tokens, best balance |
| Code debugging / error troubleshooting | **WebSearch** | web-search-prime | Community solutions are comprehensive; Context7 doesn't fit this scenario |
| Domestic open-source ecosystem (Dify, Zhipu, etc.) | **AnySearch** | WebSearch | Direct access to GitHub Release full text |

## Key Constraints

1. **WebSearch = web-search-prime**: Same engine confirmed across 9 test cases. Use one only. WebSearch has Claude summaries; web-search-prime has `location` parameter. Never call both simultaneously.
2. **Context7 is programming-docs-only**: Not suitable for OS-level debugging, domestic tech (Zhipu GLM etc.), tech comparison (returns single-library docs only), or release notes (TC14: returned API docs instead of changelog). Perfect for specific project docs (TC03 Claude Code plugin: 5/5/5/5).
3. **Use WebSearch for academic search**: AnySearch academic vertical has poor query matching (TC12: WebSearch 5/5/5/5 vs AnySearch 3/3/4/3).
4. **AnySearch has high token cost**: ~12K tokens/query (10x WebSearch). Only worthwhile for deep research.
5. **web-reader has noise**: Output includes CSS/JS/favicon metadata; agents need to filter.

## Anti-patterns

- Never call WebSearch and web-search-prime together (same engine, wastes tokens)
- Don't use Context7 for domestic tech (not covered) or tech comparisons (single-library only)
- Don't use AnySearch vertical for academic papers (poor matching; use WebSearch instead)
- Don't use web-reader for URL discovery (it can only extract known URLs)

## Quick Reference

1. **Writing code** → Context7; **reading pages** → web-reader
2. **Need completeness** → AnySearch; **need speed** → WebSearch
3. **English tech** → location=us; **Vertical domains** → AnySearch (finance/security); **Academic** → WebSearch
