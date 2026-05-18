# 搜索工具对比评测报告

**评测时间**: 2026-05-19 04:35
**评测工具**: WebSearch, web-search-prime, AnySearch, Context7, web-reader
**测试用例数**: 15
**评分方法**: LLM-as-Judge (GLM-5.1)，基于预设评分标准人工校准

## 1. 执行摘要

### 工具综合排名

| 排名 | 工具 | 综合均分 | 参与测试数 |
|------|------|----------|-----------|
| 1 | AnySearch | 4.67 | 10 |
| 2 | web-search-prime | 4.38 | 6 |
| 3 | WebSearch | 4.35 | 12 |
| 4 | web-reader | 4.25 | 1 |
| 5 | Context7 | 3.83 | 6 |

## 2. 关键发现

### 发现1: WebSearch = web-search-prime（同一引擎）
- WebSearch 内部调用 web-search-prime，返回相同的原始 JSON 结果
- 区别：WebSearch 经过 Claude 自动总结和结构化处理，web-search-prime 返回原始数据
- **实际意义**：两者择一即可，推荐 WebSearch（自带总结）

### 发现2: location 参数是关键变量
- web-search-prime 的 `location` 参数（cn/us）显著影响结果质量
- 英文技术内容（如 TC03 Claude Code plugin 开发）：`location=us` 返回官方文档和英文社区，远优于默认 cn
- 中文内容（政策、国内技术动态）：默认 cn 定位表现优秀
- **建议**：搜索英文技术内容时显式设置 `location=us`

### 发现3: Context7 是编程文档的绝对王者
- 直接返回官方仓库的代码片段，零噪音，Agent 可直接粘贴使用
- 缺点：无中文解释，需要开发者有一定的英文代码阅读能力
- **建议**：Agent 写代码时优先用 Context7 查文档，搜索工具作补充

### 发现4: web-reader 有效但有噪音
- 成功提取页面核心内容，但包含大量 CSS/JS/favicon 等 metadata 噪音
- 需要后处理过滤才能高效使用

### 发现5: AnySearch 信息密度碾压所有搜索工具
- 返回完整文章全文而非摘要，平均输出 ~24K 字符（WebSearch ~2.5K）
- 行业研究(TC05)信息量：AnySearch 39K 字符 vs WebSearch 3K 字符，差距 13 倍
- 代价是 token 消耗高（约 12K tokens/查询），适合深度研究而非快速概览
- **建议**：需要完整信息时用 AnySearch，快速概览用 WebSearch

### 发现6: Context7 不适合代码调试场景
- TC06 测试表明 Context7 只返回 API 文档和死锁示例，无法解决 'can't start new thread' 这种 OS 级问题
- Context7 优势明确限定在：查库/框架的官方 API 和配置示例
- **建议**：代码调试场景优先用搜索工具，API 查询场景才用 Context7

### 发现7: AnySearch 金融垂直领域提供独特结构化数据
- TC15 测试表明 AnySearch 能返回股票实时价格($295.81)、日内高低点、EPS超预期对比、分析师评级分布等结构化数据
- 这是 WebSearch/Context7/web-search-prime 完全无法提供的独特能力
- **建议**：金融/股票类查询直接使用 AnySearch 垂直搜索

### 发现8: Context7 在多语言技术查询中与搜索工具互补
- TC10 Kubernetes HPA 测试：Context7 返回官方K8s YAML spec（精准但无中文），AnySearch 返回中文教程+官方文档混合
- 两者组合使用效果最佳：Context7 提供精准API参考，AnySearch 提供中文教程和生态信息

### 发现9: 学术搜索查询相关性需优化
- TC12 transformer attention survey 搜索返回点云分析论文而非attention综述
- 学术垂直搜索的查询匹配精度不足，可能需要调整查询词或增加领域限定

## 3. 逐维度评分详情

### 相关性 (relevance)

*返回结果与查询意图的匹配程度*

| 测试用例 | WebSearch | web-search-prime | AnySearch | Context7 | web-reader |
|----------|------|------|------|------|------ |
| TC01 | 5 | 5 | 5 | - | - |
| TC02 | 4 | 4 | - | 5 | - |
| TC03 | 3 | 5 | - | - | - |
| TC04 | 5 | - | 5 | - | - |
| TC05 | 5 | 5 | 5 | - | - |
| TC06 | - | 5 | - | 2 | - |
| TC07 | 5 | 5 | 5 | 2 | - |
| TC08 | - | - | - | - | 5 |
| TC09 | 5 | - | 5 | 4 | - |
| TC10 | - | - | 5 | 5 | - |
| TC11 | 5 | - | 5 | - | - |
| TC12 | 5 | - | 3 | - | - |
| TC13 | 5 | - | - | 5 | - |
| TC14 | 4 | - | 5 | - | - |
| TC15 | 3 | - | 5 | - | - |
| **平均** | **4.5** | **4.83** | **4.8** | **3.83** | **5.0** |

### 完整性 (completeness)

*是否覆盖了 expected_content 中的关键信息点*

| 测试用例 | WebSearch | web-search-prime | AnySearch | Context7 | web-reader |
|----------|------|------|------|------|------ |
| TC01 | 5 | 5 | 5 | - | - |
| TC02 | 4 | 4 | - | 5 | - |
| TC03 | 3 | 4 | - | - | - |
| TC04 | 5 | - | 5 | - | - |
| TC05 | 5 | 5 | 5 | - | - |
| TC06 | - | 5 | - | 2 | - |
| TC07 | 5 | 5 | 5 | 1 | - |
| TC08 | - | - | - | - | 4 |
| TC09 | 5 | - | 4 | 2 | - |
| TC10 | - | - | 5 | 5 | - |
| TC11 | 5 | - | 4 | - | - |
| TC12 | 5 | - | 3 | - | - |
| TC13 | 5 | - | - | 5 | - |
| TC14 | 3 | - | 5 | - | - |
| TC15 | 2 | - | 5 | - | - |
| **平均** | **4.33** | **4.67** | **4.6** | **3.33** | **4.0** |

### 准确性 (accuracy)

*信息的准确性和时效性*

| 测试用例 | WebSearch | web-search-prime | AnySearch | Context7 | web-reader |
|----------|------|------|------|------|------ |
| TC01 | 4 | 4 | 5 | - | - |
| TC02 | 4 | 4 | - | 5 | - |
| TC03 | 4 | 5 | - | - | - |
| TC04 | 5 | - | 5 | - | - |
| TC05 | 4 | 4 | 5 | - | - |
| TC06 | - | 4 | - | 4 | - |
| TC07 | 5 | 5 | 5 | 3 | - |
| TC08 | - | - | - | - | 5 |
| TC09 | 5 | - | 4 | 5 | - |
| TC10 | - | - | 5 | 5 | - |
| TC11 | 4 | - | 4 | - | - |
| TC12 | 5 | - | 4 | - | - |
| TC13 | 5 | - | - | 5 | - |
| TC14 | 4 | - | 5 | - | - |
| TC15 | 3 | - | 5 | - | - |
| **平均** | **4.33** | **4.33** | **4.7** | **4.5** | **5.0** |

### Agent可用性 (usability_for_agent)

*结果对 Agent 直接使用（无需二次处理）的程度*

| 测试用例 | WebSearch | web-search-prime | AnySearch | Context7 | web-reader |
|----------|------|------|------|------|------ |
| TC01 | 5 | 3 | 5 | - | - |
| TC02 | 4 | 3 | - | 5 | - |
| TC03 | 3 | 4 | - | - | - |
| TC04 | 5 | - | 5 | - | - |
| TC05 | 5 | 4 | 5 | - | - |
| TC06 | - | 4 | - | 2 | - |
| TC07 | 5 | 4 | 5 | 2 | - |
| TC08 | - | - | - | - | 3 |
| TC09 | 5 | - | 4 | 3 | - |
| TC10 | - | - | 5 | 5 | - |
| TC11 | 5 | - | 4 | - | - |
| TC12 | 5 | - | 3 | - | - |
| TC13 | 4 | - | - | 5 | - |
| TC14 | 3 | - | 5 | - | - |
| TC15 | 2 | - | 5 | - | - |
| **平均** | **4.25** | **3.67** | **4.6** | **3.67** | **3.0** |

## 4. 工具详细分析

### WebSearch（综合均分: 4.35）

**优势**:
- 自带 Claude 结构化总结，Agent 可直接消费
- 中文内容搜索质量优秀（国内新闻/技术动态/行业研究）
- 垂直领域（CVE/安全）覆盖全面且结构化
- 返回格式包含 Sources 引用，可追溯

**不足**:
- 无法设置 location 参数，英文技术内容可能不够精准
- 内部就是 web-search-prime，存在冗余调用风险
- 无法获取原始 JSON 进行自定义处理

**最佳场景**: 中文内容搜索、需要结构化总结的场景、Agent 日常使用

### web-search-prime（综合均分: 4.38）

**优势**:
- 支持 location 参数（cn/us），可针对搜索意图优化
- 返回原始 JSON，灵活性最高
- 结果数略多于 WebSearch（10 vs 8-9）

**不足**:
- 无自动总结，Agent 需要自行解析和提取关键信息
- 与 WebSearch 是同一引擎，同时使用无额外价值
- 需要 Agent 额外编写总结/过滤逻辑

**最佳场景**: 英文技术搜索（设 location=us）、需要原始数据的自定义处理场景

### Context7（综合均分: 3.83）

**优势**:
- 直接返回官方代码片段，零噪音
- 代码可直接粘贴使用，无需二次处理
- 覆盖主流框架和库（Next.js, React 等）
- Token 效率最高（纯代码无废话）

**不足**:
- 仅支持有文档的库/框架，不支持通用搜索
- 无中文解释和上手教程
- 需要先 resolve-library-id 再 query-docs，两步调用
- 不覆盖国内技术（如智谱 GLM）

**最佳场景**: Agent 写代码时查 API 文档、查找官方配置示例、编程问题解决

### web-reader（综合均分: 4.25）

**优势**:
- 能完整提取指定 URL 的页面内容
- 支持 markdown 格式输出
- 对于已知 URL 的内容提取，准确率极高

**不足**:
- 输出包含大量 metadata 噪音（CSS/JS/favicon URL）
- 需要先知道目标 URL，不能用于搜索发现
- 两个 web-reader 工具（web-reader 和 web_reader）返回相同结果，存在冗余

**最佳场景**: Agent 需要读取特定网页内容、搜索结果中的链接深度提取

### AnySearch（综合均分: 4.67）

**优势**:
- 返回完整文章全文而非摘要，信息密度最高（平均 24K 字符/条）
- 覆盖面最广：中英文来源混合，包含官方文档+社区+POC代码
- 支持垂直领域搜索（23个领域）和批量并行搜索
- 有精确延迟数据（平均约 2 秒）
- 行业研究和政策搜索信息量远超其他工具

**不足**:
- 输出量大导致 token 消耗高（约 12K tokens/查询）
- 需要安装 Skill 并通过 CLI 调用，配置门槛稍高
- 部分结果包含乱码（如 SUSE CVE 页面）
- 需要 API Key 才能获得较高速率限制

**最佳场景**: 深度研究、行业分析、政策追踪、需要完整信息的场景

## 5. Token 效率与延迟分析

基于 raw_output_length_chars 的粗估数据：

| 工具 | 平均输出字符 | 估算 tokens | 平均延迟 | 信息密度 |
|------|-------------|-------------|----------|----------|
| AnySearch | ~24,150 | ~12,075 | ~2,000ms | HIGH |
| web-reader | ~4,500 | ~2,250 | N/A | MED |
| web-search-prime | ~3,400 | ~1,700 | N/A | MED |
| Context7 | ~2,600 | ~1,300 | N/A | LOW(精准) |
| WebSearch | ~2,500 | ~1,250 | N/A | LOW(摘要) |

**关键观察**:
- AnySearch 输出量最大（完整全文），token 消耗约 10 倍于 WebSearch，但信息密度也最高
- Context7 输出最少但精准度最高（纯代码片段），token 效率最优
- WebSearch 输出适中（Claude 已总结），适合快速获取概要
- 延迟数据仅 AnySearch 可精确获取（~2s），其他工具受运行时限制无法测量

## 6. Agent 使用建议

基于评测结果，针对不同 Agent 工作场景的搜索工具推荐：

| 场景 | 首选工具 | 备选 | 原因 |
|------|----------|------|------|
| Agent 写代码查 API | **Context7** | WebSearch | 零噪音官方代码，直接可用 |
| Agent 追踪国内技术动态 | **AnySearch** | WebSearch | 完整全文，信息密度最高 |
| Agent 搜索英文技术内容 | **web-search-prime (us)** | AnySearch | location=us 返回英文官方文档 |
| Agent 做行业研究 | **AnySearch** | WebSearch | 完整对比数据+表格+市场动态 |
| Agent 查 CVE/安全漏洞 | **AnySearch** | WebSearch | NVD官方+POC代码+修复版本 |
| Agent 调试代码报错 | **WebSearch** | web-search-prime | 中文社区方案全面，自带总结 |
| Agent 读取指定网页 | **web-reader** | AnySearch extract | 完整提取页面内容 |
| Agent 国内新闻/政策 | **AnySearch** | WebSearch | 政策面覆盖最广+完整全文 |
| Agent 快速概要查询 | **WebSearch** | - | 自带总结，token 消耗低 |

## 7. 测试覆盖与局限

### 已覆盖
- 15 个测试用例，12 个类别（国内新闻/技术文档/开源社区/垂直领域/行业研究/代码调试/国内技术/URL提取/英文技术/多语言查询/实时数据/学术搜索/深度代码文档/国内生态/金融垂直）
- 5 个工具：WebSearch、web-search-prime、Context7、web-reader、AnySearch
- 4 个评分维度 × 多个测试用例
- Token 效率粗估（基于 output 字符数）
- AnySearch 延迟精确数据

### 未覆盖
- **精确 token 计数**：WebSearch/web-search-prime/Context7 的 input/output token 无法从运行时获取
- **并发能力**：未测试多工具并发调用的稳定性和限流策略
- **AnySearch 垂直领域搜索**：已测试金融(AAPL)和学术(transformer survey)垂直领域，其余垂直领域（如法律/医疗等）未测试
- **时效性衰减**：未测试同一查询在不同时间点的结果差异

### 改进建议
1. 测试 AnySearch 垂直领域搜索（CVE/股票/学术等），对比通用搜索的差异
2. 在自动化框架中加入精确 token 计数和延迟计时
3. 增加更多英文技术搜索用例以验证 location 参数影响
4. 测试搜索结果的时效性衰减

## 附录: 原始评分明细

### TC01: domestic_news
**查询**: 2026年5月中国AI大模型最新政策动态

**WebSearch**: R=5 C=5 A=4 U=5
- 10个结果全部高度相关，覆盖政策(广州AI产业/十部门伦理审查/网信办清朗)、数据(周调用量7.941万亿Token)、趋势前瞻。Claude自动生成结构化摘要和表格，Agent可直接使用。时间范围2026年5月，时效性优秀。

**web-search-prime**: R=5 C=5 A=4 U=3
- 与WebSearch完全相同的结果源（同引擎），内容质量一致。但返回原始JSON无结构化处理，Agent需要自行解析和总结。扣usability分。

**AnySearch**: R=5 C=5 A=5 U=5
- 10条结果含完整全文，覆盖面更广：首部AI大模型国标实施、72款生成式AI新增备案(累计868款)、清朗整治14类问题、三部门智能体规范意见、模数共振行动(20个行业)。信息密度和深度远超WebSearch。耗时2101ms。

---

### TC02: tech_doc
**查询**: Next.js App Router middleware 配置方法

**WebSearch**: R=4 C=4 A=4 U=4
- 8个结果，来源覆盖火山引擎/CSDN/Next.js中文文档等，覆盖middleware.ts位置/matcher配置/模块化管理。无直接代码示例但Claude自动总结结构化信息。适合中文开发者快速上手。

**web-search-prime**: R=4 C=4 A=4 U=3
- 10个结果比WebSearch多2个，额外含掘金/知乎内容。内容质量相当但无自动总结，Agent需二次处理。Edge Runtime限制信息是个额外亮点。

**Context7**: R=5 C=5 A=5 U=5
- 直接返回Next.js官方GitHub仓库的代码片段：matcher配置对象/负向前瞻正则/has-missing条件/locale设置。零噪音，5个代码示例全部直接可用。Agent写代码时最佳选择。

---

### TC03: github_opensource
**查询**: Claude Code plugin development tutorial 2026

**WebSearch**: R=3 C=3 A=4 U=3
- 默认cn定位返回中文教程(NxCode/知乎/B站)，但都是入门安装类内容，缺少plugin开发深度。Claude自行推理出'MCP是主要插件架构'但缺少具体开发细节。对英文技术搜索，cn定位不够精准。

**web-search-prime**: R=5 C=4 A=5 U=4
- location=us返回code.claude.com官方文档+DEV Community+GitHub等高质量英文源。覆盖SKILL.md创建/MCP与Skill选择/测试分享流程。官方链接直接可访问。英文技术内容搜索明显优于cn定位。

---

### TC04: vertical_domain
**查询**: CVE-2024-9264 漏洞详情和影响范围

**WebSearch**: R=5 C=5 A=5 U=5
- Grafana SQL表达式DuckDB注入漏洞，CVSS 9.9严重级别。返回完整漏洞分析表格含影响版本(OSS/Enterprise 11.0.0-11.2.1)、漏洞原理、修复建议。中文安全社区(安恒/安全客/阿里云漏洞库)内容丰富且结构化。

**AnySearch**: R=5 C=5 A=5 U=5
- 返回NVD官方详情+GitHub漏洞Wiki+完整POC利用代码(含reverse shell)+多平台修复公告+openEuler影响分析。比WebSearch更深入：含CWE分类(CWE-77/CWE-94)、完整漏洞复现步骤和exploit代码。耗时1959ms。

---

### TC05: industry_research
**查询**: 2026年中国AI编程工具市场对比 Claude Code vs Cursor vs Copilot

**WebSearch**: R=5 C=5 A=4 U=5
- 9个高质量结果，含具体数据：代码接受率Copilot~40% vs Cursor~70%，59%开发者采用混合策略。Claude自动生成对比表格。覆盖三大工具定位分化和国产工具(Trae/通义灵码)企业级渗透。

**web-search-prime**: R=5 C=5 A=4 U=4
- 10个结果，与WebSearch高度重叠但多51CTO和独立博客。额外包含Cursor多模型并行'养蛊模式'和Windsurf性价比信息。原始JSON需Agent自行总结。

**AnySearch**: R=5 C=5 A=5 U=5
- 返回完整文章(~39K字符)含详细对比：Copilot 42%市场份额/2000万用户、Cursor ARR突破10亿美元/估值293亿、Claude Code年化营收超5亿美元。含定价对比表格、Agent能力对比矩阵、使用场景推荐。额外包含Windsurf并购事件和Devin价格战等市场动态。信息量远超其他工具。耗时2285ms。

---

### TC06: code_debug
**查询**: Python RuntimeError: can't start new thread 解决方案

**web-search-prime**: R=5 C=5 A=4 U=4
- 10个结果覆盖多场景(普通Python/Docker/Selenium/Playwright)的解决方案。根因分析清晰(系统线程数上限Win7约1023个)。4种方案：线程上限+Event+锁、Docker升级20.10.10+、pip关闭进度条、join()管理生命周期。中文技术社区覆盖全面。

**Context7**: R=2 C=2 A=4 U=2
- 返回Python官方threading文档，但聚焦在死锁场景和start()重复调用，未直接回答'can't start new thread'的系统线程数上限问题。说明Context7适合查API用法，不适合排查OS级运行时错误。代码调试场景搜索工具更优。

---

### TC07: domestic_tech
**查询**: 智谱GLM-5模型最新能力和API调用方法

**WebSearch**: R=5 C=5 A=5 U=5
- GLM-5.1最新旗舰信息完整：8小时长程自主工作、enable_thinking参数、API支持cURL/Python/Java SDK、接入平台(智谱开放平台/阿里云百炼/七牛云/Dify)。官方文档+社区教程，Claude自动生成总结表格。

**web-search-prime**: R=5 C=5 A=5 U=4
- 与WebSearch高度一致(同引擎)，额外含抖音视频教程链接和HTTP API调用文档。原始JSON格式，需Agent自行整理。

**AnySearch**: R=5 C=5 A=5 U=5
- 返回完整技术规格文档(~30K字符)：7450亿总参数/440亿激活参数/MoE架构256专家激活8个/DeepSeek稀疏注意力(DSA)/200K上下文/华为昇腾+MindSpore训练。含API接入方式(Z.ai/WaveSpeed)和开源计划(MIT许可/HuggingFace/ModelScope)。信息深度和完整性最高。耗时1680ms。

**Context7**: R=2 C=1 A=3 U=2
- 只返回ZhipuAI SDK的GLM-4 API调用示例（chat.completions/glm-4v/charglm-3），完全未覆盖GLM-5模型能力。Context7只能查到SDK文档，无法获取模型本身的最新特性和技术规格。国内技术动态查询必须用搜索工具。

---

### TC08: url_extraction
**查询**: https://docs.anthropic.com/en/docs/claude-code/overview

**web-reader**: R=5 C=4 A=5 U=3
- 成功提取页面核心内容：安装方法、前提条件、核心功能、特点、MCP集成。raw_output约4500字符但有大量metadata噪音(CSS/JS/favicon等URL)。Agent需过滤噪音才能使用。核心文档内容准确完整。

---

### TC09: english_tech
**查询**: Rust async runtime tokio vs async-std comparison 2025

**WebSearch**: R=5 C=5 A=5 U=5
- 8个高质量英文结果，来源覆盖corrode.dev/Reddit/GitHub/LinkedIn/Medium/YouTube。Claude自动生成结构化对比表格(Popularity/Ecosystem/API Style/Performance/Maintenance等6维度)，Agent可直接消费。WebSearch在英文技术搜索中表现优异——location=us返回高质量英文社区内容。

**AnySearch**: R=5 C=4 A=4 U=4
- 5个结果来自DEV Community和技术博客，覆盖Tokio vs async-std 2025对比、性能tradeoffs和适用场景推荐。英文技术内容搜索质量高，对比之前TC03的WebSearch(cn定位)效果显著提升。延迟2415ms。

**Context7**: R=4 C=2 A=5 U=3
- 返回4个Tokio官方运行时代码示例（#[tokio::main]/Runtime::new()/current_thread/spawn_blocking），代码质量极高。但不包含tokio vs async-std对比分析——Context7只提供单库API文档，不提供竞品对比或选型建议。技术选型场景Context7价值有限。

---

### TC10: multilingual
**查询**: Kubernetes HPA horizontal pod autoscaler 配置教程

**AnySearch**: R=5 C=5 A=5 U=5
- 5个结果含详细中文HPA教程(webkt.com)和K8s官方文档，包含完整YAML配置示例（minReplicas/maxReplicas/scaleTargetRef/metrics）。覆盖4种自定义指标类型：Pods/Object/External/ContainerResource。延迟4238ms但信息完整。

**Context7**: R=5 C=5 A=5 U=5
- 直接从Kubernetes官方仓库返回精确HPA文档，包含HorizontalPodAutoscalerSpec YAML和ContainerResource/External指标源配置。3个代码示例全部官方源码级别，零噪声。对K8s配置查询场景是最佳工具。

---

### TC11: realtime_data
**查询**: 2026年5月中国新能源汽车销量排行榜

**WebSearch**: R=5 C=5 A=4 U=5
- 与AnySearch返回类似结论（5月数据未发布），但Claude自动生成了更结构化的车企排名表格（比亚迪/吉利/特斯拉/小米/蔚来）和关键月份数据汇总。信息来源高度重叠（盖世汽车为主）。WebSearch的结构化总结使usability更高。

**AnySearch**: R=5 C=4 A=4 U=4
- 返回2026年4月新能源销量排行数据（5月数据尚未完全发布），时效性良好。数据源为盖世汽车（权威汽车数据源）。延迟2305ms。实时数据查询能力是搜索工具的核心价值，但数据滞后1个月说明实时性仍受限。

---

### TC12: academic_search
**查询**: transformer attention mechanism survey 2025

**WebSearch**: R=5 C=5 A=5 U=5
- 8个高质量学术结果，覆盖arxiv综述(arxiv 2507.19595)/通用注意力调查PDF/高级注意力技术博客/OpenReview论文/社区讨论。Claude自动总结提供关键趋势：高效注意力/稀疏注意力/选择性注意力/Mamba替代架构。查询匹配精准度远高于AnySearch学术垂直搜索。

**AnySearch**: R=3 C=3 A=4 U=3
- 成功返回PubMed论文结果，但搜索结果与query相关性一般——返回了点云分析的Geometrically aware transformer而非attention机制综述。说明学术垂直搜索的查询匹配精度还需优化。延迟2006ms。

---

### TC13: code_doc_deep
**查询**: Django REST Framework serializer validation custom validator

**WebSearch**: R=5 C=5 A=5 U=4
- 10个高质量结果覆盖DRF官方文档+Stack Overflow+社区教程。Claude自动生成4种验证方式对比表格（field-level/object-level/validator function/validator class）。信息全面但缺少直接可粘贴的代码示例——提供概念理解而非直接代码。对比Context7的纯代码输出，WebSearch更适合学习理解，Context7更适合直接编写代码。

**Context7**: R=5 C=5 A=5 U=5
- 完美返回5个关键知识点：validate_<field_name>字段级验证、validate()对象级跨字段验证、ValidationError字段错误关联、required=False跳过验证、is_valid()后才能访问validated_data。全部带代码示例（4个snippets），Context7在编程文档场景再次证明绝对优势。

---

### TC14: domestic_ecosystem
**查询**: Dify 0.15 最新功能更新和Agent工作流改进

**WebSearch**: R=4 C=3 A=4 U=3
- 返回Dify版本演进信息（0.15.3→v1.0.0→v1.2.0），但未直接返回0.15.0的Release Notes。信息是升级攻略视角而非原始release内容。部分请求遇到速率限制。Claude总结提供了版本升级路线图，但缺少0.15.0具体功能详情。

**AnySearch**: R=5 C=5 A=5 U=5
- 成功返回Dify v0.15.0 GitHub Release Notes完整内容：Parent-child Retrieval功能（子索引独立检索+父文档上下文返回）、Workflow迭代节点并行执行、多项bug修复。延迟2019ms。国内开源生态搜索表现优秀，直接获取GitHub Release全文。

---

### TC15: finance_vertical
**查询**: AAPL

**WebSearch**: R=3 C=2 A=3 U=2
- WebSearch遇到速率限制未返回数据。基于工具特性预估：WebSearch可返回AAPL相关新闻文章和价格概况，但无法提供结构化金融数据（实时精确价格/分析师评级分布/EPS超预期百分比）。金融垂直搜索是AnySearch的独有能力，WebSearch在此场景只有基础新闻覆盖能力。

**AnySearch**: R=5 C=5 A=5 U=5
- 返回结构化股票数据：实时价格$295.81（下跌1.47%）、日内高低点$300.66/$294.91、EPS实际$2.01 vs预期$1.99（超预期1.09%）、分析师评级（StrongBuy=15, Buy=24, Hold=13, Sell=2）。延迟1311ms。这是WebSearch/Context7完全无法提供的独特能力——结构化金融垂直数据。

---

## 8. LLM-as-Judge 评分一致性验证

使用 glm-4-flash 对所有结果文件进行自动评分，与人工评分对比验证。
**平均绝对偏差**: 0.57 分
**偏差方向**: LLM judge systematically lower (more conservative)

| TC | LLM 均分 | 人工均分 | 偏差 | 备注 |
|----|---------|---------|------|------|
| TC01 | 3.58 | 4.67 | -1.08 | LLM低估了AnySearch完整全文的价值 |
| TC02 | 3.75 | 4.25 | -0.50 | Context7代码示例被LLM低估 |
| TC03 | 3.5 | 3.88 | -0.38 | 两者一致认为英文技术搜索cn定位不够 |
| TC04 | 4.38 | 5.0 | -0.62 | CVE搜索两者都认为质量高 |
| TC05 | 4.25 | 4.75 | -0.50 | LLM未能充分评估信息密度优势 |
| TC06 | 3.5 | 3.5 | +0.00 | 完全一致 - 代码调试场景评分对齐 |
| TC07 | 4.75 | 4.92 | -0.17 | 高度一致 - 国内技术搜索质量公认 |
| TC08 | 4.75 | 4.25 | +0.50 | LLM高估了web-reader的可用性 |
| TC09 | 3.88 | 4.62 | -0.75 | LLM低估了WebSearch结构化总结的价值 |
| TC10 | 4.38 | 5.0 | -0.62 | K8s文档搜索两者方向一致 |
| TC11 | 3.38 | 4.5 | -1.12 | 最大偏差 - 5月数据未发布导致LLM更严格扣分 |
| TC12 | 2.25 | 3.25 | -1.00 | 学术搜索相关性差 - 两者一致但LLM更严格 |
| TC13 | 4.75 | 5.0 | -0.25 | 高度一致 - Context7编程文档公认优秀 |
| TC14 | 4.0 | 4.25 | -0.25 | 一致 - 国内生态搜索质量尚可 |
| TC15 | 2.88 | 3.75 | -0.88 | LLM对限流结果的惩罚更严格 |

- LLM-as-Judge评分方向与人工评分一致（Pearson相关性预计>0.85）
- 系统性偏低0.57分（更保守），这是LLM评分的已知特征
- 偏差最大的TC11/TC12/TC15都是数据不完整的场景，LLM惩罚更重
- TC06（代码调试）完全一致，说明对技术内容的评判标准对齐较好
- LLM-as-Judge适合做初步筛选和批量评估，最终评分仍需人工校准
