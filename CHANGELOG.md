# 搜索工具对比评测 - 迭代总结

## 项目概览

对比 Claude Code 环境下 5 个搜索工具（WebSearch、web-search-prime、Context7、AnySearch、web-reader）在 15 个测试场景中的表现。

**最终数据**: 28 commits, 52 评分组合 (69%), 47 条 LLM-Judge 验证 (deviation 0.46), +2148/-78 行, 41 个文件变更。

---

## 一、框架搭建 (Session 1, commits 1-3)

| Commit | 内容 |
|--------|------|
| 98acbbf | 项目初始化：test_cases.json (8 TC) + scorer.py (手动评分) + report.md + 结果文件 |
| 9f6f30a | LLM-as-Judge 自动评分系统 + 方法论对比文档 |
| 233b1b7 | 测试集扩展至 15 个 TC（新增 TC08-TC15 覆盖英文技术/多语言/实时数据/学术/代码文档/国内生态/金融） |

**关键产出**: 评分框架（4 维度 1-5 分）+ 自动报告生成 + 15 个 TC 定义

---

## 二、数据收集与对比 (Session 1-2, commits 4-11)

### WebSearch 补充 (commits 4, 6, 7)

补齐 WebSearch 在 TC09/TC11/TC12/TC13/TC14/TC15 的对比数据。

**发现**: WebSearch 自带 Claude 结构化总结，usability 显著高于原始搜索结果。

### Context7 边界探索 (commits 8, 9, 12)

| TC | 分数 | 结论 |
|----|------|------|
| TC07 智谱 GLM-5 | 2/1/3/2 | Context7 只返回 SDK API，无法获取模型能力和技术规格 |
| TC09 Rust tokio | 4/2/5/3 | 代码精准但不提供竞品对比，技术选型场景价值有限 |
| TC04 CVE-2024-9264 | 1/1/2/1 | 完全无法检索特定 CVE，只返回通用安全扫描工具文档 |

**关键结论**: Context7 严格限定于编程 API/SDK 文档。

### AnySearch 覆盖扩展 (commits 5, 10, 11)

补齐 AnySearch 在 TC02/TC03/TC06/TC13 的测试，覆盖率达到 14/15 TCs。

**发现**: AnySearch 信息密度碾压（平均 24K 字符 vs WebSearch 2.5K），但 token 消耗约 10x。

### 学术搜索反转 (commit 6)

TC12 transformer attention survey:
- **WebSearch**: 5/5/5/5 — arXiv/OpenReview/Semantic Scholar 精准匹配
- **AnySearch 垂直**: 3/3/4/3 — 返回点云分析论文，查询匹配精度差

**决策变更**: 学术搜索首选从 AnySearch 改为 WebSearch。

---

## 三、同引擎验证 (Session 2, commits 12-13)

### web-search-prime 系统性验证

通过 9 个 TC (TC01/TC03/TC04/TC05/TC07/TC09/TC10/TC11/TC12/TC13/TC14/TC15) 对比 WebSearch 和 web-search-prime 的返回来源。

**结论**: 来源列表完全一致，确认 WebSearch 内部调用 web-search-prime。

### Claude 总结价值量化

| 维度 | WebSearch | web-search-prime | 差距 |
|------|-----------|------------------|------|
| 相关性 | 4.57 | 4.64 | -0.07 |
| 完整性 | 4.43 | 4.57 | -0.14 |
| 准确性 | 4.36 | 4.43 | -0.07 |
| **Agent 可用性** | **4.36** | **3.36** | **+1.00** |

Claude 自动总结在 usability 维度贡献 +1.0 分。

---

## 四、LLM-as-Judge 验证 (Session 1-2, commits 5-6, 18)

### 第一轮 (35 条评分)

调用智谱 GLM-4-Flash API，对所有结果文件自动评分。遇到 JSON 解析问题（LLM 返回 markdown 包裹的 JSON），通过 regex 容错修复。

### 第二轮 (47 条评分)

覆盖所有 47 个结果文件。与手动评分对比：

- **Avg deviation**: 0.46 分
- **方向一致性**: 15/15 TCs 偏差 < 1.5 分
- **Bias**: Manual +0.38（手动评分系统性偏高，因为考虑了 Claude 总结的 usability 加成）

---

## 五、覆盖填补与收尾 (Session 2, commits 14-21)

### 补齐缺口 (commit 14)

| 新增组合 | 分数 | 说明 |
|----------|------|------|
| WebSearch TC06 | 5/5/4/5 | 代码调试，Claude 生成解决方案表格 |
| WebSearch TC10 | 5/5/5/5 | K8s HPA，遇 429 限流后重试成功 |
| Context7 TC03 | 5/5/5/5 | Claude Code 插件文档，精准满分 |
| Context7 TC14 | 2/1/3/2 | Dify v0.15 release notes，只能查到 API 文档 |

**覆盖率**: 42 → 52 组合 (56% → 69%)

### Bug 修复 (commit 20)

`load_result()` 中 glob 模式大小写不匹配（`TC02_*` vs `tc02_*`），导致 all_tools 和 individual 文件无法合并。修复为 `.lower()`。

### 报告健壮性 (commits 21-22)

将 findings 文本从 report.md 直接编辑改为更新 scorer.py 的 `generate_report()` 源码，确保重新生成不丢失更新。

---

## 六、文档与可视化 (Session 2, commits 15, 17, 23-28)

### ASCII 柱状图 (commit 15)

```
  AnySearch            █████████████████████████████████████░░░ 4.70 (14 tests)
  WebSearch            ███████████████████████████████████░░░░░ 4.43 (14 tests)
  web-search-prime     ██████████████████████████████████░░░░░░ 4.25 (14 tests)
  web-reader           ██████████████████████████████████░░░░░░ 4.25 (1 tests)
  Context7             ███████████████████████████░░░░░░░░░░░░░ 3.47 (9 tests)
```

### 维度汇总表 (commit 25)

| 工具 | 相关性 | 完整性 | 准确性 | Agent 可用性 | 综合 |
|------|--------|--------|--------|------------|------|
| WebSearch | 4.57 | 4.43 | 4.36 | 4.36 | **4.43** |
| web-search-prime | 4.64 | 4.57 | 4.43 | 3.36 | **4.25** |
| AnySearch | 4.86 | 4.71 | 4.79 | 4.43 | **4.70** |
| Context7 | 3.44 | 3.0 | 4.11 | 3.33 | **3.47** |
| web-reader | 5.0 | 4.0 | 5.0 | 3.0 | **4.25** |

### 文档同步

- README.md: 排名/覆盖数据/关键发现
- CLAUDE.md (项目): 决策规则/约束/文件说明
- CLAUDE.md (全局): 搜索策略表
- test_cases.json: applicable_tools 更新
- memory: 评测结论持久化

---

## 七、最终结论

### 综合排名

1. **AnySearch** 4.70 — 信息密度最高，金融/安全垂直独有能力
2. **WebSearch** 4.43 — Claude 总结加持，快速概览首选
3. **web-search-prime** 4.25 — 同引擎无总结，location 参数是唯一差异化
4. **web-reader** 4.25 — URL 提取专用
5. **Context7** 3.47 — 编程文档精准但范围窄

### 三句话决策规则

1. 写代码 → Context7；读网页 → web-reader
2. 要完整 → AnySearch；要快速 → WebSearch
3. 英文技术 → location=us；垂直领域 → AnySearch（金融/安全），学术用 WebSearch

### 关键发现

- **WebSearch = web-search-prime**: 9 个 TC 全面验证，Claude 总结贡献 usability +1.0
- **Context7 边界清晰**: 插件文档满分 (5/5/5/5) vs release notes 仅 2 分
- **学术搜索反转**: WebSearch 远优于 AnySearch 垂直 (TC12: 5/5/5/5 vs 3/3/4/3)
- **金融垂直独有**: AnySearch 能返回实时价格/EPS/分析师评级，其他工具无法提供
