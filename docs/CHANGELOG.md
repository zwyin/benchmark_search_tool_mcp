# Search Tool Benchmark — Iteration Summary

## Overview

Comparative evaluation of 5 search tools (WebSearch, web-search-prime, Context7, AnySearch, web-reader) across 15 test scenarios in the Claude Code environment.

**Final data**: 30 commits, 52 scored combinations (69% coverage), 47 LLM-Judge validations (deviation 0.46), +2200/-80 lines, 41 files changed.

---

## Phase 1: Framework Setup (Session 1, commits 1-3)

| Commit | Content |
|--------|---------|
| Initial | Project setup: test_cases.json (8 TCs) + scorer.py (manual scoring) + report.md + result files |
| LLM-Judge | Automated LLM-as-Judge scoring system + methodology docs |
| Expanded | Test set expanded to 15 TCs (TC08-TC15 covering English tech, multilingual, real-time data, academic, code docs, domestic ecosystem, finance) |

---

## Phase 2: Data Collection (Sessions 1-2, commits 4-11)

### WebSearch gap-filling
Added comparison data for TC09/TC11/TC12/TC13/TC14/TC15. Discovered that WebSearch's built-in Claude summary significantly boosts usability scores.

### Context7 boundary exploration

| TC | Score | Conclusion |
|----|-------|------------|
| TC07 Zhipu GLM-5 | 2/1/3/2 | Context7 only returns SDK APIs, cannot fetch model capabilities or tech specs |
| TC09 Rust tokio | 4/2/5/3 | Precise code but no competitor comparison; limited value for tech selection |
| TC04 CVE-2024-9264 | 1/1/2/1 | Cannot retrieve specific CVEs; only returns generic security scanner docs |

**Key insight**: Context7 is strictly limited to programming API/SDK documentation.

### AnySearch coverage expansion
Filled TC02/TC03/TC06/TC13 tests. Coverage reached 14/15 TCs. AnySearch information density dominates (avg 24K chars vs WebSearch 2.5K), but token cost ~10x.

### Academic search reversal
TC12 transformer attention survey:
- **WebSearch**: 5/5/5/5 — precise arXiv/OpenReview/Semantic Scholar matching
- **AnySearch vertical**: 3/3/4/3 — returned point cloud analysis papers, poor query matching

**Decision changed**: Academic search primary tool switched from AnySearch to WebSearch.

---

## Phase 3: Same-Engine Verification (Session 2, commits 12-13)

Systematically compared WebSearch and web-search-prime across 9+ TCs. Source lists are identical, confirming WebSearch internally calls web-search-prime.

| Dimension | WebSearch | web-search-prime | Gap |
|-----------|-----------|------------------|-----|
| Relevance | 4.57 | 4.64 | -0.07 |
| Completeness | 4.43 | 4.57 | -0.14 |
| Accuracy | 4.36 | 4.43 | -0.07 |
| **Agent Usability** | **4.36** | **3.36** | **+1.00** |

Claude's auto-summary contributes +1.0 on usability.

---

## Phase 4: LLM-as-Judge Validation (Sessions 1-2, 47 scores)

Called Zhipu GLM-4-Flash API to auto-score all result files. Handled JSON parsing issues (LLM returned markdown-wrapped JSON) via regex fallback.

Compared with Agent scoring:
- **Avg deviation**: 0.46 points
- **Directional consistency**: 15/15 TCs within 1.5-point deviation
- **Bias**: Manual +0.38 (Agent scoring systematically higher due to Claude summary usability bonus)

---

## Phase 5: Coverage Fill & Bug Fixes (Session 2, commits 14-21)

Filled remaining gaps to reach 52/75 combinations (69%).

Bug fix: `load_result()` glob pattern case mismatch (`TC02_*` vs `tc02_*`), fixed with `.lower()`.

---

## Phase 6: Documentation & Visualization (Session 2)

```
  AnySearch            █████████████████████████████████████░░░ 4.70 (14 tests)
  WebSearch            ███████████████████████████████████░░░░░ 4.43 (14 tests)
  web-search-prime     ██████████████████████████████████░░░░░░ 4.25 (14 tests)
  web-reader           ██████████████████████████████████░░░░░░ 4.25 (1 tests)
  Context7             ███████████████████████████░░░░░░░░░░░░░ 3.47 (9 tests)
```

---

## Phase 7: Tool Selector Engine (Session 3)

Created `search_selector.py` — a query-to-tool recommendation engine:
- 7 intent types: code, search, extract, research, finance, academic, security
- Language-aware: English → web-search-prime location=us; Chinese → WebSearch
- Comparison queries ("X vs Y") correctly classified as research, not code
- Each recommendation includes evaluation evidence, constraints, and fallback options

Also fixed misleading "人工评分" (manual scoring) terminology → "Agent 评分" (Agent scoring).

---

## Final Conclusions

### Overall Rankings

1. **AnySearch** 4.70 — Highest information density; unique finance/security verticals
2. **WebSearch** 4.43 — Claude summary bonus; best for quick overviews
3. **web-search-prime** 4.25 — Same engine, no summary; `location` param differentiator
4. **web-reader** 4.25 — URL extraction only
5. **Context7** 3.47 — Precise for programming docs but narrow scope

### Three-Line Decision Rule

1. **Writing code** → Context7; **reading pages** → web-reader
2. **Need completeness** → AnySearch; **need speed** → WebSearch
3. **English tech** → location=us; **Vertical domains** → AnySearch (finance/security); **Academic** → WebSearch

### Key Findings

- **WebSearch = web-search-prime**: Confirmed across 9 TCs; Claude summary contributes usability +1.0
- **Context7 boundary is clear**: Plugin docs perfect (5/5/5/5) vs release notes only 2 points
- **Academic search reversal**: WebSearch far superior to AnySearch vertical (TC12: 5/5/5/5 vs 3/3/4/3)
- **Finance vertical is unique**: AnySearch returns real-time prices/EPS/analyst ratings; other tools cannot provide this
