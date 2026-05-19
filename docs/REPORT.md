# Search Tool Benchmark Report

**Date**: 2026-05-19
**Tools Evaluated**: WebSearch, web-search-prime, AnySearch, Context7, web-reader
**Test Cases**: 15
**Scoring**: Agent scoring (based on predefined rubric) + LLM-as-Judge (GLM-4-Flash) cross-validation (avg deviation 0.46)

## 1. Executive Summary

### Overall Rankings

| Rank | Tool | Avg Score | Tests |
|------|------|-----------|-------|
| 1 | AnySearch | 4.70 | 14 |
| 2 | WebSearch | 4.43 | 14 |
| 3 | web-search-prime | 4.25 | 14 |
| 4 | web-reader | 4.25 | 1 |
| 5 | Context7 | 3.47 | 9 |

### Score Visualization

```
  AnySearch            █████████████████████████████████████░░░ 4.70 (14 tests)
  WebSearch            ███████████████████████████████████░░░░░ 4.43 (14 tests)
  web-search-prime     ██████████████████████████████████░░░░░░ 4.25 (14 tests)
  web-reader           ██████████████████████████████████░░░░░░ 4.25 (1 tests)
  Context7             ███████████████████████████░░░░░░░░░░░░░ 3.47 (9 tests)
```

## 2. Key Findings

### Finding 1: WebSearch = web-search-prime (Same Engine)
- WebSearch internally calls web-search-prime, returning identical raw JSON results
- Difference: WebSearch applies Claude auto-summarization and structuring; web-search-prime returns raw data
- **Implication**: Use one only; prefer WebSearch for built-in summaries

### Finding 2: Location Parameter is the Key Variable
- web-search-prime's `location` parameter (cn/us) significantly impacts result quality
- English tech content (e.g., TC03 Claude Code plugin dev): `location=us` returns official docs + English community sources
- Chinese content (policy, domestic tech): default `cn` performs excellently
- **Recommendation**: Set `location=us` explicitly for English technical searches

### Finding 3: Context7 is the Undisputed King of Programming Docs — But Only for API/SDK Docs
- Returns official code snippets directly from repos, zero noise, agent-ready
- TC03 Claude Code plugin dev: perfect 5/5/5/5, precisely hitting plugin.json/Agent SDK/hooks/MCP config
- TC14 Dify v0.15 release notes: only 2/1/3/2, returned Workflow API docs instead of changelog
- **Clear boundary**: Suitable for library/framework API and config examples; not for version tracking, changelogs, or release notes

### Finding 4: web-reader Works but Has Noise
- Successfully extracts page core content but includes CSS/JS/favicon metadata noise
- Requires post-processing filtering for efficient use

### Finding 5: AnySearch Information Density Dominates All Search Tools
- Returns full article text rather than summaries, average output ~24K chars (WebSearch ~2.5K)
- Industry research (TC05) information volume: AnySearch 39K chars vs WebSearch 3K chars, 13x gap
- Tradeoff: high token consumption (~12K tokens/query); suited for deep research, not quick overviews
- **Recommendation**: Use AnySearch for completeness, WebSearch for speed

### Finding 6: Context7 is Not Suitable for Code Debugging
- TC06 testing shows Context7 only returns API docs and deadlock examples, cannot solve OS-level issues like 'can't start new thread'
- Context7's strength is clearly limited to: querying library/framework official API and config examples
- **Recommendation**: Prioritize search tools for debugging, use Context7 only for API queries

### Finding 7: AnySearch Finance Vertical Provides Unique Structured Data
- TC15 testing shows AnySearch returns stock real-time prices ($295.81), intraday highs/lows, EPS surprise comparisons, analyst rating distributions
- This is a unique capability that WebSearch/Context7/web-search-prime completely cannot provide
- **Recommendation**: Use AnySearch vertical search directly for finance/stock queries

### Finding 8: Context7 Complements Search Tools in Multilingual Tech Queries
- TC10 Kubernetes HPA testing: Context7 returns official K8s YAML specs (precise but no Chinese), AnySearch returns Chinese tutorials + official docs
- Best results when combined: Context7 provides precise API reference, AnySearch provides Chinese tutorials and ecosystem info

### Finding 9: Use WebSearch for Academic Search, Not AnySearch Vertical
- TC12 transformer attention survey: AnySearch academic vertical returned point cloud analysis papers instead of attention surveys (3/3/4/3)
- Same query on WebSearch returned arXiv/OpenReview/Semantic Scholar precise matches (5/5/5/5)
- **Recommendation**: Use WebSearch for academic search; do not use AnySearch academic vertical

## 3. Dimension Scores

### Relevance

| TC | WebSearch | web-search-prime | AnySearch | Context7 | web-reader |
|----|-----------|------------------|-----------|----------|------------|
| TC01 | 5 | 5 | 5 | - | - |
| TC02 | 4 | 4 | 5 | 5 | - |
| TC03 | 3 | 5 | 5 | 5 | - |
| TC04 | 5 | 5 | 5 | 1 | - |
| TC05 | 5 | 5 | 5 | - | - |
| TC06 | 5 | 5 | 5 | 2 | - |
| TC07 | 5 | 5 | 5 | 2 | - |
| TC08 | - | - | - | - | 5 |
| TC09 | 5 | 5 | 5 | 4 | - |
| TC10 | 5 | 5 | 5 | 5 | - |
| TC11 | 5 | 5 | 5 | - | - |
| TC12 | 5 | 5 | 3 | - | - |
| TC13 | 5 | 5 | 5 | 5 | - |
| TC14 | 4 | 2 | 5 | 2 | - |
| TC15 | 3 | 4 | 5 | - | - |
| **Avg** | **4.57** | **4.64** | **4.86** | **3.44** | **5.0** |

### Completeness

| TC | WebSearch | web-search-prime | AnySearch | Context7 | web-reader |
|----|-----------|------------------|-----------|----------|------------|
| TC01 | 5 | 5 | 5 | - | - |
| TC02 | 4 | 4 | 5 | 5 | - |
| TC03 | 3 | 4 | 5 | 5 | - |
| TC04 | 5 | 5 | 5 | 1 | - |
| TC05 | 5 | 5 | 5 | - | - |
| TC06 | 5 | 5 | 5 | 2 | - |
| TC07 | 5 | 5 | 5 | 1 | - |
| TC08 | - | - | - | - | 4 |
| TC09 | 5 | 5 | 4 | 2 | - |
| TC10 | 5 | 5 | 5 | 5 | - |
| TC11 | 5 | 5 | 4 | - | - |
| TC12 | 5 | 5 | 3 | - | - |
| TC13 | 5 | 5 | 5 | 5 | - |
| TC14 | 3 | 2 | 5 | 1 | - |
| TC15 | 2 | 4 | 5 | - | - |
| **Avg** | **4.43** | **4.57** | **4.71** | **3.0** | **4.0** |

### Accuracy

| TC | WebSearch | web-search-prime | AnySearch | Context7 | web-reader |
|----|-----------|------------------|-----------|----------|------------|
| TC01 | 4 | 4 | 5 | - | - |
| TC02 | 4 | 4 | 5 | 5 | - |
| TC03 | 4 | 5 | 5 | 5 | - |
| TC04 | 5 | 5 | 5 | 2 | - |
| TC05 | 4 | 4 | 5 | - | - |
| TC06 | 4 | 4 | 5 | 4 | - |
| TC07 | 5 | 5 | 5 | 3 | - |
| TC08 | - | - | - | - | 5 |
| TC09 | 5 | 5 | 4 | 5 | - |
| TC10 | 5 | 5 | 5 | 5 | - |
| TC11 | 4 | 4 | 4 | - | - |
| TC12 | 5 | 5 | 4 | - | - |
| TC13 | 5 | 5 | 5 | 5 | - |
| TC14 | 4 | 3 | 5 | 3 | - |
| TC15 | 3 | 4 | 5 | - | - |
| **Avg** | **4.36** | **4.43** | **4.79** | **4.11** | **5.0** |

### Agent Usability

| TC | WebSearch | web-search-prime | AnySearch | Context7 | web-reader |
|----|-----------|------------------|-----------|----------|------------|
| TC01 | 5 | 3 | 5 | - | - |
| TC02 | 4 | 3 | 4 | 5 | - |
| TC03 | 3 | 4 | 4 | 5 | - |
| TC04 | 5 | 3 | 5 | 1 | - |
| TC05 | 5 | 4 | 5 | - | - |
| TC06 | 5 | 4 | 4 | 2 | - |
| TC07 | 5 | 4 | 5 | 2 | - |
| TC08 | - | - | - | - | 3 |
| TC09 | 5 | 3 | 4 | 3 | - |
| TC10 | 5 | 4 | 5 | 5 | - |
| TC11 | 5 | 4 | 4 | - | - |
| TC12 | 5 | 3 | 3 | - | - |
| TC13 | 4 | 3 | 4 | 5 | - |
| TC14 | 3 | 2 | 5 | 2 | - |
| TC15 | 2 | 3 | 5 | - | - |
| **Avg** | **4.36** | **3.36** | **4.43** | **3.33** | **3.0** |

### Dimension Summary

| Tool | Relevance | Completeness | Accuracy | Agent Usability | Overall |
|------|-----------|-------------|----------|----------------|---------|
| WebSearch | 4.57 | 4.43 | 4.36 | 4.36 | **4.43** |
| web-search-prime | 4.64 | 4.57 | 4.43 | 3.36 | **4.25** |
| AnySearch | 4.86 | 4.71 | 4.79 | 4.43 | **4.70** |
| Context7 | 3.44 | 3.0 | 4.11 | 3.33 | **3.47** |
| web-reader | 5.0 | 4.0 | 5.0 | 3.0 | **4.25** |

## 4. Tool Analysis

### WebSearch (Overall: 4.43)

**Strengths**: Built-in Claude structuring; excellent Chinese content search; comprehensive vertical coverage (CVE/security); includes source citations.

**Weaknesses**: No `location` parameter; internally calls web-search-prime (redundancy risk); cannot access raw JSON.

**Best for**: Chinese content search, structured summaries, daily agent use.

### web-search-prime (Overall: 4.25)

**Strengths**: `location` parameter (cn/us) for targeted results; raw JSON output for flexibility; slightly more results than WebSearch (10 vs 8-9).

**Weaknesses**: No auto-summarization; same engine as WebSearch; requires custom parsing logic.

**Best for**: English tech search (set location=us), custom data processing.

### Context7 (Overall: 3.47)

**Strengths**: Official code snippets with zero noise; directly pasteable; covers mainstream frameworks; highest token efficiency.

**Weaknesses**: Only supports documented libraries/frameworks; no Chinese explanations; requires two-step call (resolve → query); no coverage for domestic tech (Zhipu GLM etc.).

**Best for**: API doc lookups while coding, official config examples.

### web-reader (Overall: 4.25)

**Strengths**: Complete page content extraction; markdown output; high accuracy for known URLs.

**Weaknesses**: Metadata noise (CSS/JS/favicon); requires known URL (not for discovery); two instances (web-reader and web_reader) return identical results.

**Best for**: Reading specific webpages, deep extraction of search result links.

### AnySearch (Overall: 4.70)

**Strengths**: Full article text (avg 24K chars/result); broadest coverage (Chinese + English sources); 23 vertical domains; precise latency data (~2s avg); industry research and policy search far exceeds other tools.

**Weaknesses**: High token consumption (~12K tokens/query); requires Skill installation; some results contain garbled text; API key needed for higher rate limits.

**Best for**: Deep research, industry analysis, policy tracking, scenarios requiring complete information.

## 5. Token Efficiency & Latency

| Tool | Avg Output (chars) | Est. Tokens | Avg Latency | Info Density |
|------|-------------------|-------------|-------------|-------------|
| AnySearch | ~24,150 | ~12,075 | ~2,000ms | HIGH |
| web-reader | ~4,500 | ~2,250 | N/A | MED |
| web-search-prime | ~3,400 | ~1,700 | N/A | MED |
| Context7 | ~2,600 | ~1,300 | N/A | LOW (precise) |
| WebSearch | ~2,500 | ~1,250 | N/A | LOW (summary) |

## 6. Agent Recommendations

| Scenario | Primary Tool | Fallback | Reason |
|----------|-------------|----------|--------|
| Agent writing code, needs API docs | **Context7** | WebSearch | Zero-noise official code, directly usable |
| Agent tracking domestic tech trends | **AnySearch** | WebSearch | Full text, highest information density |
| Agent searching English tech content | **web-search-prime (us)** | AnySearch | location=us returns English official docs |
| Agent doing industry research | **AnySearch** | WebSearch | Complete comparison data + market dynamics |
| Agent checking CVE/security vulnerabilities | **AnySearch** | WebSearch | NVD official + POC code + fix versions |
| Agent debugging code errors | **WebSearch** | web-search-prime | Comprehensive community solutions, auto-summarized |
| Agent reading a specific webpage | **web-reader** | AnySearch extract | Complete page extraction |
| Agent tracking domestic news/policy | **AnySearch** | WebSearch | Broadest policy coverage + full text |
| Agent quick summary query | **WebSearch** | — | Auto-summarized, low token cost |

## 7. Test Coverage & Limitations

### Covered
- 15 test cases across 15 categories × 5 tools = 52 valid tool-TC combinations (69% coverage)
- 5 tools: WebSearch (14 TCs), web-search-prime (14 TCs), AnySearch (14 TCs), Context7 (9 TCs), web-reader (1 TC)
- 4 scoring dimensions × Agent scoring + LLM-as-Judge cross-validation (47 auto-scores, avg deviation 0.46)

### Not Covered
- Precise token counts for WebSearch/web-search-prime/Context7
- Concurrent multi-tool call stability and rate limiting
- AnySearch vertical domains beyond finance/academic/security
- Temporal decay of search results across time points

## 8. LLM-as-Judge Consistency

Using glm-4-flash for auto-scoring all result files, cross-validated with Agent scoring.

| TC | LLM Avg | Agent Avg | Deviation | Notes |
|----|---------|-----------|-----------|-------|
| TC01 | 3.58 | 4.67 | +1.08 | LLM underrates raw JSON usability |
| TC02 | 4.25 | 4.38 | +0.12 | High agreement |
| TC03 | 4.33 | 4.38 | +0.04 | Excellent agreement |
| TC04 | 3.62 | 3.94 | +0.31 | Context7 CVE mismatch affects average |
| TC05 | 4.25 | 4.75 | +0.50 | Reasonable |
| TC06 | 4.25 | 4.12 | -0.12 | LLM slightly higher |
| TC07 | 3.92 | 4.19 | +0.27 | Reasonable |
| TC08 | 4.75 | 4.25 | -0.50 | LLM higher on web-reader |
| TC09 | 3.19 | 4.31 | +1.12 | LLM underrates technical depth |
| TC10 | 4.31 | 4.94 | +0.62 | Agent values K8s doc completeness |
| TC11 | 3.42 | 4.50 | +1.08 | LLM underrates data precision |
| TC12 | 3.58 | 4.25 | +0.67 | LLM underrates academic sources |
| TC13 | 4.50 | 4.75 | +0.25 | Good agreement |
| TC14 | 3.19 | 3.19 | +0.00 | Perfect agreement |
| TC15 | 3.50 | 3.75 | +0.25 | Good agreement |

- 47 LLM-Judge scores vs 52 Agent scores, avg deviation 0.46, ranking direction fully consistent
- Agent scoring systematically higher by +0.38, mainly due to Claude auto-summary usability bonus
- 15/15 TCs within 1.5-point deviation; no ranking inversions
- Overall ranking consistent: AnySearch > WebSearch > web-search-prime > web-reader ≈ Context7
