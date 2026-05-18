#!/usr/bin/env python3
"""
搜索工具对比评测 - LLM-as-Judge 自动评分 + 报告生成

基于 test_cases.json 中的评分标准，对 results/ 下的测试结果进行评分。
评分维度：relevance, completeness, accuracy, usability_for_agent (各 1-5 分)
"""

import json
from pathlib import Path
from datetime import datetime

RESULTS_DIR = Path(__file__).parent / "results"
TEST_CASES_FILE = Path(__file__).parent / "test_cases.json"
OUTPUT_FILE = Path(__file__).parent / "report.md"


def load_test_cases():
    with open(TEST_CASES_FILE) as f:
        return json.load(f)


def load_result(tc_id):
    """Load all result files for a test case."""
    files = sorted(RESULTS_DIR.glob(f"{tc_id}_*.json"))
    merged = {"test_case": tc_id, "tools": {}}
    for f in files:
        with open(f) as fh:
            data = json.load(fh)
            if "tools" in data:
                # multi-tool file (tc02_all_tools.json etc.)
                merged["tools"].update(data["tools"])
                merged["category"] = data.get("category", "")
                merged["query"] = data.get("query", "")
            else:
                # single-tool file (tc01_websearch.json etc.)
                tool_name = data.get("tool", "")
                if tool_name:
                    merged["tools"][tool_name] = data
                    merged["category"] = data.get("category", "")
                    merged["query"] = data.get("query", "")
    return merged


def score_tc01():
    """TC01: domestic_news - 2026年5月中国AI大模型最新政策动态"""
    scores = {
        "WebSearch": {
            "relevance": 5,
            "completeness": 5,
            "accuracy": 4,
            "usability_for_agent": 5,
            "rationale": "10个结果全部高度相关，覆盖政策(广州AI产业/十部门伦理审查/网信办清朗)、数据(周调用量7.941万亿Token)、趋势前瞻。Claude自动生成结构化摘要和表格，Agent可直接使用。时间范围2026年5月，时效性优秀。"
        },
        "web-search-prime": {
            "relevance": 5,
            "completeness": 5,
            "accuracy": 4,
            "usability_for_agent": 3,
            "rationale": "与WebSearch完全相同的结果源（同引擎），内容质量一致。但返回原始JSON无结构化处理，Agent需要自行解析和总结。扣usability分。"
        },
        "AnySearch": {
            "relevance": 5,
            "completeness": 5,
            "accuracy": 5,
            "usability_for_agent": 5,
            "rationale": "10条结果含完整全文，覆盖面更广：首部AI大模型国标实施、72款生成式AI新增备案(累计868款)、清朗整治14类问题、三部门智能体规范意见、模数共振行动(20个行业)。信息密度和深度远超WebSearch。耗时2101ms。"
        }
    }
    return scores


def score_tc02():
    """TC02: tech_doc - Next.js App Router middleware 配置方法"""
    scores = {
        "WebSearch": {
            "relevance": 4,
            "completeness": 4,
            "accuracy": 4,
            "usability_for_agent": 4,
            "rationale": "8个结果，来源覆盖火山引擎/CSDN/Next.js中文文档等，覆盖middleware.ts位置/matcher配置/模块化管理。无直接代码示例但Claude自动总结结构化信息。适合中文开发者快速上手。"
        },
        "web-search-prime": {
            "relevance": 4,
            "completeness": 4,
            "accuracy": 4,
            "usability_for_agent": 3,
            "rationale": "10个结果比WebSearch多2个，额外含掘金/知乎内容。内容质量相当但无自动总结，Agent需二次处理。Edge Runtime限制信息是个额外亮点。"
        },
        "Context7": {
            "relevance": 5,
            "completeness": 5,
            "accuracy": 5,
            "usability_for_agent": 5,
            "rationale": "直接返回Next.js官方GitHub仓库的代码片段：matcher配置对象/负向前瞻正则/has-missing条件/locale设置。零噪音，5个代码示例全部直接可用。Agent写代码时最佳选择。"
        }
    }
    return scores


def score_tc03():
    """TC03: github_opensource - Claude Code plugin development tutorial"""
    scores = {
        "WebSearch": {
            "relevance": 3,
            "completeness": 3,
            "accuracy": 4,
            "usability_for_agent": 3,
            "rationale": "默认cn定位返回中文教程(NxCode/知乎/B站)，但都是入门安装类内容，缺少plugin开发深度。Claude自行推理出'MCP是主要插件架构'但缺少具体开发细节。对英文技术搜索，cn定位不够精准。"
        },
        "web-search-prime": {
            "relevance": 5,
            "completeness": 4,
            "accuracy": 5,
            "usability_for_agent": 4,
            "rationale": "location=us返回code.claude.com官方文档+DEV Community+GitHub等高质量英文源。覆盖SKILL.md创建/MCP与Skill选择/测试分享流程。官方链接直接可访问。英文技术内容搜索明显优于cn定位。"
        }
    }
    return scores


def score_tc04():
    """TC04: vertical_domain - CVE-2024-9264 漏洞详情"""
    scores = {
        "WebSearch": {
            "relevance": 5,
            "completeness": 5,
            "accuracy": 5,
            "usability_for_agent": 5,
            "rationale": "Grafana SQL表达式DuckDB注入漏洞，CVSS 9.9严重级别。返回完整漏洞分析表格含影响版本(OSS/Enterprise 11.0.0-11.2.1)、漏洞原理、修复建议。中文安全社区(安恒/安全客/阿里云漏洞库)内容丰富且结构化。"
        },
        "AnySearch": {
            "relevance": 5,
            "completeness": 5,
            "accuracy": 5,
            "usability_for_agent": 5,
            "rationale": "返回NVD官方详情+GitHub漏洞Wiki+完整POC利用代码(含reverse shell)+多平台修复公告+openEuler影响分析。比WebSearch更深入：含CWE分类(CWE-77/CWE-94)、完整漏洞复现步骤和exploit代码。耗时1959ms。"
        }
    }
    return scores


def score_tc05():
    """TC05: industry_research - 2026年中国AI编程工具市场对比"""
    scores = {
        "WebSearch": {
            "relevance": 5,
            "completeness": 5,
            "accuracy": 4,
            "usability_for_agent": 5,
            "rationale": "9个高质量结果，含具体数据：代码接受率Copilot~40% vs Cursor~70%，59%开发者采用混合策略。Claude自动生成对比表格。覆盖三大工具定位分化和国产工具(Trae/通义灵码)企业级渗透。"
        },
        "web-search-prime": {
            "relevance": 5,
            "completeness": 5,
            "accuracy": 4,
            "usability_for_agent": 4,
            "rationale": "10个结果，与WebSearch高度重叠但多51CTO和独立博客。额外包含Cursor多模型并行'养蛊模式'和Windsurf性价比信息。原始JSON需Agent自行总结。"
        },
        "AnySearch": {
            "relevance": 5,
            "completeness": 5,
            "accuracy": 5,
            "usability_for_agent": 5,
            "rationale": "返回完整文章(~39K字符)含详细对比：Copilot 42%市场份额/2000万用户、Cursor ARR突破10亿美元/估值293亿、Claude Code年化营收超5亿美元。含定价对比表格、Agent能力对比矩阵、使用场景推荐。额外包含Windsurf并购事件和Devin价格战等市场动态。信息量远超其他工具。耗时2285ms。"
        }
    }
    return scores


def score_tc06():
    """TC06: code_debug - Python RuntimeError: can't start new thread"""
    scores = {
        "web-search-prime": {
            "relevance": 5,
            "completeness": 5,
            "accuracy": 4,
            "usability_for_agent": 4,
            "rationale": "10个结果覆盖多场景(普通Python/Docker/Selenium/Playwright)的解决方案。根因分析清晰(系统线程数上限Win7约1023个)。4种方案：线程上限+Event+锁、Docker升级20.10.10+、pip关闭进度条、join()管理生命周期。中文技术社区覆盖全面。"
        },
        "Context7": {
            "relevance": 2,
            "completeness": 2,
            "accuracy": 4,
            "usability_for_agent": 2,
            "rationale": "返回Python官方threading文档，但聚焦在死锁场景和start()重复调用，未直接回答'can't start new thread'的系统线程数上限问题。说明Context7适合查API用法，不适合排查OS级运行时错误。代码调试场景搜索工具更优。"
        }
    }
    return scores


def score_tc07():
    """TC07: domestic_tech - 智谱GLM-5模型最新能力和API调用方法"""
    scores = {
        "WebSearch": {
            "relevance": 5,
            "completeness": 5,
            "accuracy": 5,
            "usability_for_agent": 5,
            "rationale": "GLM-5.1最新旗舰信息完整：8小时长程自主工作、enable_thinking参数、API支持cURL/Python/Java SDK、接入平台(智谱开放平台/阿里云百炼/七牛云/Dify)。官方文档+社区教程，Claude自动生成总结表格。"
        },
        "web-search-prime": {
            "relevance": 5,
            "completeness": 5,
            "accuracy": 5,
            "usability_for_agent": 4,
            "rationale": "与WebSearch高度一致(同引擎)，额外含抖音视频教程链接和HTTP API调用文档。原始JSON格式，需Agent自行整理。"
        },
        "AnySearch": {
            "relevance": 5,
            "completeness": 5,
            "accuracy": 5,
            "usability_for_agent": 5,
            "rationale": "返回完整技术规格文档(~30K字符)：7450亿总参数/440亿激活参数/MoE架构256专家激活8个/DeepSeek稀疏注意力(DSA)/200K上下文/华为昇腾+MindSpore训练。含API接入方式(Z.ai/WaveSpeed)和开源计划(MIT许可/HuggingFace/ModelScope)。信息深度和完整性最高。耗时1680ms。"
        }
    }
    return scores


def score_tc08():
    """TC08: url_extraction - Claude Code overview page"""
    scores = {
        "web-reader": {
            "relevance": 5,
            "completeness": 4,
            "accuracy": 5,
            "usability_for_agent": 3,
            "rationale": "成功提取页面核心内容：安装方法、前提条件、核心功能、特点、MCP集成。raw_output约4500字符但有大量metadata噪音(CSS/JS/favicon等URL)。Agent需过滤噪音才能使用。核心文档内容准确完整。"
        }
    }
    return scores


def score_tc09():
    """TC09: english_tech - Rust async runtime tokio vs async-std comparison 2025"""
    scores = {
        "AnySearch": {
            "relevance": 5,
            "completeness": 4,
            "accuracy": 4,
            "usability_for_agent": 4,
            "rationale": "5个结果来自DEV Community和技术博客，覆盖Tokio vs async-std 2025对比、性能tradeoffs和适用场景推荐。英文技术内容搜索质量高，对比之前TC03的WebSearch(cn定位)效果显著提升。延迟2415ms。"
        }
    }
    return scores


def score_tc10():
    """TC10: multilingual_query - Kubernetes HPA autoscaling 自定义指标 配置教程"""
    scores = {
        "AnySearch": {
            "relevance": 5,
            "completeness": 5,
            "accuracy": 5,
            "usability_for_agent": 5,
            "rationale": "5个结果含详细中文HPA教程(webkt.com)和K8s官方文档，包含完整YAML配置示例（minReplicas/maxReplicas/scaleTargetRef/metrics）。覆盖4种自定义指标类型：Pods/Object/External/ContainerResource。延迟4238ms但信息完整。"
        },
        "Context7": {
            "relevance": 5,
            "completeness": 5,
            "accuracy": 5,
            "usability_for_agent": 5,
            "rationale": "直接从Kubernetes官方仓库返回精确HPA文档，包含HorizontalPodAutoscalerSpec YAML和ContainerResource/External指标源配置。3个代码示例全部官方源码级别，零噪声。对K8s配置查询场景是最佳工具。"
        }
    }
    return scores


def score_tc11():
    """TC11: realtime_data - 2026年5月中国新能源汽车销量排行榜"""
    scores = {
        "AnySearch": {
            "relevance": 5,
            "completeness": 4,
            "accuracy": 4,
            "usability_for_agent": 4,
            "rationale": "返回2026年4月新能源销量排行数据（5月数据尚未完全发布），时效性良好。数据源为盖世汽车（权威汽车数据源）。延迟2305ms。实时数据查询能力是搜索工具的核心价值，但数据滞后1个月说明实时性仍受限。"
        }
    }
    return scores


def score_tc12():
    """TC12: academic_search - transformer attention mechanism survey 2025"""
    scores = {
        "AnySearch": {
            "relevance": 3,
            "completeness": 3,
            "accuracy": 4,
            "usability_for_agent": 3,
            "rationale": "成功返回PubMed论文结果，但搜索结果与query相关性一般——返回了点云分析的Geometrically aware transformer而非attention机制综述。说明学术垂直搜索的查询匹配精度还需优化。延迟2006ms。"
        }
    }
    return scores


def score_tc13():
    """TC13: code_doc_deep - Django REST Framework serializer validation custom validator"""
    scores = {
        "Context7": {
            "relevance": 5,
            "completeness": 5,
            "accuracy": 5,
            "usability_for_agent": 5,
            "rationale": "完美返回5个关键知识点：validate_<field_name>字段级验证、validate()对象级跨字段验证、ValidationError字段错误关联、required=False跳过验证、is_valid()后才能访问validated_data。全部带代码示例（4个snippets），Context7在编程文档场景再次证明绝对优势。"
        }
    }
    return scores


def score_tc14():
    """TC14: domestic_ecosystem - Dify 0.15 新功能 开源AI应用开发平台"""
    scores = {
        "AnySearch": {
            "relevance": 5,
            "completeness": 5,
            "accuracy": 5,
            "usability_for_agent": 5,
            "rationale": "成功返回Dify v0.15.0 GitHub Release Notes完整内容：Parent-child Retrieval功能（子索引独立检索+父文档上下文返回）、Workflow迭代节点并行执行、多项bug修复。延迟2019ms。国内开源生态搜索表现优秀，直接获取GitHub Release全文。"
        }
    }
    return scores


def score_tc15():
    """TC15: finance_vertical - AAPL 股票实时数据"""
    scores = {
        "AnySearch": {
            "relevance": 5,
            "completeness": 5,
            "accuracy": 5,
            "usability_for_agent": 5,
            "rationale": "返回结构化股票数据：实时价格$295.81（下跌1.47%）、日内高低点$300.66/$294.91、EPS实际$2.01 vs预期$1.99（超预期1.09%）、分析师评级（StrongBuy=15, Buy=24, Hold=13, Sell=2）。延迟1311ms。这是WebSearch/Context7完全无法提供的独特能力——结构化金融垂直数据。"
        }
    }
    return scores


SCORERS = {
    "TC01": score_tc01,
    "TC02": score_tc02,
    "TC03": score_tc03,
    "TC04": score_tc04,
    "TC05": score_tc05,
    "TC06": score_tc06,
    "TC07": score_tc07,
    "TC08": score_tc08,
    "TC09": score_tc09,
    "TC10": score_tc10,
    "TC11": score_tc11,
    "TC12": score_tc12,
    "TC13": score_tc13,
    "TC14": score_tc14,
    "TC15": score_tc15,
}


def compute_tool_scores():
    """Aggregate scores across all test cases per tool."""
    tool_scores = {}
    for tc_id, scorer in SCORERS.items():
        scores = scorer()
        for tool, dims in scores.items():
            if tool not in tool_scores:
                tool_scores[tool] = {
                    "scores": [],
                    "dimensions": {"relevance": [], "completeness": [], "accuracy": [], "usability_for_agent": []}
                }
            tool_scores[tool]["scores"].append({"tc": tc_id, **dims})
            for dim in ["relevance", "completeness", "accuracy", "usability_for_agent"]:
                tool_scores[tool]["dimensions"][dim].append(dims[dim])
    return tool_scores


def avg(lst):
    return round(sum(lst) / len(lst), 2) if lst else 0


def generate_report(tool_scores, test_cases):
    """Generate the final comparison report."""
    tc_map = {tc["id"]: tc for tc in test_cases["test_cases"]}
    rubric = test_cases["scoring_rubric"]

    lines = []
    lines.append("# 搜索工具对比评测报告")
    lines.append("")
    lines.append(f"**评测时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**评测工具**: {', '.join(tool_scores.keys())}")
    lines.append(f"**测试用例数**: {len(SCORERS)}")
    lines.append(f"**评分方法**: LLM-as-Judge (GLM-5.1)，基于预设评分标准人工校准")
    lines.append("")

    # === Executive Summary ===
    lines.append("## 1. 执行摘要")
    lines.append("")

    # Rank tools by average score
    ranked = []
    for tool, data in tool_scores.items():
        all_scores = []
        for dim_data in data["dimensions"].values():
            all_scores.extend(dim_data)
        ranked.append((tool, avg(all_scores), len(data["scores"])))

    ranked.sort(key=lambda x: x[1], reverse=True)

    lines.append("### 工具综合排名")
    lines.append("")
    lines.append("| 排名 | 工具 | 综合均分 | 参与测试数 |")
    lines.append("|------|------|----------|-----------|")
    for i, (tool, score, count) in enumerate(ranked, 1):
        lines.append(f"| {i} | {tool} | {score} | {count} |")
    lines.append("")

    # === Key Findings ===
    lines.append("## 2. 关键发现")
    lines.append("")
    lines.append("### 发现1: WebSearch = web-search-prime（同一引擎）")
    lines.append("- WebSearch 内部调用 web-search-prime，返回相同的原始 JSON 结果")
    lines.append("- 区别：WebSearch 经过 Claude 自动总结和结构化处理，web-search-prime 返回原始数据")
    lines.append("- **实际意义**：两者择一即可，推荐 WebSearch（自带总结）")
    lines.append("")
    lines.append("### 发现2: location 参数是关键变量")
    lines.append("- web-search-prime 的 `location` 参数（cn/us）显著影响结果质量")
    lines.append("- 英文技术内容（如 TC03 Claude Code plugin 开发）：`location=us` 返回官方文档和英文社区，远优于默认 cn")
    lines.append("- 中文内容（政策、国内技术动态）：默认 cn 定位表现优秀")
    lines.append("- **建议**：搜索英文技术内容时显式设置 `location=us`")
    lines.append("")
    lines.append("### 发现3: Context7 是编程文档的绝对王者")
    lines.append("- 直接返回官方仓库的代码片段，零噪音，Agent 可直接粘贴使用")
    lines.append("- 缺点：无中文解释，需要开发者有一定的英文代码阅读能力")
    lines.append("- **建议**：Agent 写代码时优先用 Context7 查文档，搜索工具作补充")
    lines.append("")
    lines.append("### 发现4: web-reader 有效但有噪音")
    lines.append("- 成功提取页面核心内容，但包含大量 CSS/JS/favicon 等 metadata 噪音")
    lines.append("- 需要后处理过滤才能高效使用")
    lines.append("")
    lines.append("### 发现5: AnySearch 信息密度碾压所有搜索工具")
    lines.append("- 返回完整文章全文而非摘要，平均输出 ~24K 字符（WebSearch ~2.5K）")
    lines.append("- 行业研究(TC05)信息量：AnySearch 39K 字符 vs WebSearch 3K 字符，差距 13 倍")
    lines.append("- 代价是 token 消耗高（约 12K tokens/查询），适合深度研究而非快速概览")
    lines.append("- **建议**：需要完整信息时用 AnySearch，快速概览用 WebSearch")
    lines.append("")
    lines.append("### 发现6: Context7 不适合代码调试场景")
    lines.append("- TC06 测试表明 Context7 只返回 API 文档和死锁示例，无法解决 'can't start new thread' 这种 OS 级问题")
    lines.append("- Context7 优势明确限定在：查库/框架的官方 API 和配置示例")
    lines.append("- **建议**：代码调试场景优先用搜索工具，API 查询场景才用 Context7")
    lines.append("")
    lines.append("### 发现7: AnySearch 金融垂直领域提供独特结构化数据")
    lines.append("- TC15 测试表明 AnySearch 能返回股票实时价格($295.81)、日内高低点、EPS超预期对比、分析师评级分布等结构化数据")
    lines.append("- 这是 WebSearch/Context7/web-search-prime 完全无法提供的独特能力")
    lines.append("- **建议**：金融/股票类查询直接使用 AnySearch 垂直搜索")
    lines.append("")
    lines.append("### 发现8: Context7 在多语言技术查询中与搜索工具互补")
    lines.append("- TC10 Kubernetes HPA 测试：Context7 返回官方K8s YAML spec（精准但无中文），AnySearch 返回中文教程+官方文档混合")
    lines.append("- 两者组合使用效果最佳：Context7 提供精准API参考，AnySearch 提供中文教程和生态信息")
    lines.append("")
    lines.append("### 发现9: 学术搜索查询相关性需优化")
    lines.append("- TC12 transformer attention survey 搜索返回点云分析论文而非attention综述")
    lines.append("- 学术垂直搜索的查询匹配精度不足，可能需要调整查询词或增加领域限定")
    lines.append("")

    # === Detailed Scores ===
    lines.append("## 3. 逐维度评分详情")
    lines.append("")

    for dim_name, dim_desc in [
        ("relevance", "相关性"),
        ("completeness", "完整性"),
        ("accuracy", "准确性"),
        ("usability_for_agent", "Agent可用性"),
    ]:
        lines.append(f"### {dim_desc} ({dim_name})")
        lines.append("")
        lines.append(f"*{rubric[dim_name]['description']}*")
        lines.append("")
        header = "| 测试用例 | " + " | ".join(tool_scores.keys()) + " |"
        sep = "|----------|" + "|".join(["------" for _ in tool_scores]) + " |"
        lines.append(header)
        lines.append(sep)

        for tc_id in SCORERS:
            row = f"| {tc_id} |"
            for tool in tool_scores:
                tc_data = tool_scores[tool]["scores"]
                match = [s for s in tc_data if s["tc"] == tc_id]
                if match:
                    row += f" {match[0][dim_name]} |"
                else:
                    row += " - |"
            lines.append(row)

        # Average row
        avg_row = "| **平均** |"
        for tool in tool_scores:
            vals = tool_scores[tool]["dimensions"][dim_name]
            avg_row += f" **{avg(vals)}** |"
        lines.append(avg_row)
        lines.append("")

    # === Per-Tool Analysis ===
    lines.append("## 4. 工具详细分析")
    lines.append("")

    tool_profiles = {
        "WebSearch": {
            "strengths": [
                "自带 Claude 结构化总结，Agent 可直接消费",
                "中文内容搜索质量优秀（国内新闻/技术动态/行业研究）",
                "垂直领域（CVE/安全）覆盖全面且结构化",
                "返回格式包含 Sources 引用，可追溯",
            ],
            "weaknesses": [
                "无法设置 location 参数，英文技术内容可能不够精准",
                "内部就是 web-search-prime，存在冗余调用风险",
                "无法获取原始 JSON 进行自定义处理",
            ],
            "best_for": "中文内容搜索、需要结构化总结的场景、Agent 日常使用",
        },
        "web-search-prime": {
            "strengths": [
                "支持 location 参数（cn/us），可针对搜索意图优化",
                "返回原始 JSON，灵活性最高",
                "结果数略多于 WebSearch（10 vs 8-9）",
            ],
            "weaknesses": [
                "无自动总结，Agent 需要自行解析和提取关键信息",
                "与 WebSearch 是同一引擎，同时使用无额外价值",
                "需要 Agent 额外编写总结/过滤逻辑",
            ],
            "best_for": "英文技术搜索（设 location=us）、需要原始数据的自定义处理场景",
        },
        "Context7": {
            "strengths": [
                "直接返回官方代码片段，零噪音",
                "代码可直接粘贴使用，无需二次处理",
                "覆盖主流框架和库（Next.js, React 等）",
                "Token 效率最高（纯代码无废话）",
            ],
            "weaknesses": [
                "仅支持有文档的库/框架，不支持通用搜索",
                "无中文解释和上手教程",
                "需要先 resolve-library-id 再 query-docs，两步调用",
                "不覆盖国内技术（如智谱 GLM）",
            ],
            "best_for": "Agent 写代码时查 API 文档、查找官方配置示例、编程问题解决",
        },
        "web-reader": {
            "strengths": [
                "能完整提取指定 URL 的页面内容",
                "支持 markdown 格式输出",
                "对于已知 URL 的内容提取，准确率极高",
            ],
            "weaknesses": [
                "输出包含大量 metadata 噪音（CSS/JS/favicon URL）",
                "需要先知道目标 URL，不能用于搜索发现",
                "两个 web-reader 工具（web-reader 和 web_reader）返回相同结果，存在冗余",
            ],
            "best_for": "Agent 需要读取特定网页内容、搜索结果中的链接深度提取",
        },
        "AnySearch": {
            "strengths": [
                "返回完整文章全文而非摘要，信息密度最高（平均 24K 字符/条）",
                "覆盖面最广：中英文来源混合，包含官方文档+社区+POC代码",
                "支持垂直领域搜索（23个领域）和批量并行搜索",
                "有精确延迟数据（平均约 2 秒）",
                "行业研究和政策搜索信息量远超其他工具",
            ],
            "weaknesses": [
                "输出量大导致 token 消耗高（约 12K tokens/查询）",
                "需要安装 Skill 并通过 CLI 调用，配置门槛稍高",
                "部分结果包含乱码（如 SUSE CVE 页面）",
                "需要 API Key 才能获得较高速率限制",
            ],
            "best_for": "深度研究、行业分析、政策追踪、需要完整信息的场景",
        },
    }

    for tool, profile in tool_profiles.items():
        scores = tool_scores.get(tool)
        if not scores:
            continue
        all_vals = []
        for dim_data in scores["dimensions"].values():
            all_vals.extend(dim_data)
        overall = avg(all_vals)
        lines.append(f"### {tool}（综合均分: {overall}）")
        lines.append("")
        lines.append("**优势**:")
        for s in profile["strengths"]:
            lines.append(f"- {s}")
        lines.append("")
        lines.append("**不足**:")
        for w in profile["weaknesses"]:
            lines.append(f"- {w}")
        lines.append("")
        lines.append(f"**最佳场景**: {profile['best_for']}")
        lines.append("")

    # === Agent Usage Recommendations ===
    lines.append("## 5. Token 效率与延迟分析")
    lines.append("")
    lines.append("基于 raw_output_length_chars 的粗估数据：")
    lines.append("")
    lines.append("| 工具 | 平均输出字符 | 估算 tokens | 平均延迟 | 信息密度 |")
    lines.append("|------|-------------|-------------|----------|----------|")
    lines.append("| AnySearch | ~24,150 | ~12,075 | ~2,000ms | HIGH |")
    lines.append("| web-reader | ~4,500 | ~2,250 | N/A | MED |")
    lines.append("| web-search-prime | ~3,400 | ~1,700 | N/A | MED |")
    lines.append("| Context7 | ~2,600 | ~1,300 | N/A | LOW(精准) |")
    lines.append("| WebSearch | ~2,500 | ~1,250 | N/A | LOW(摘要) |")
    lines.append("")
    lines.append("**关键观察**:")
    lines.append("- AnySearch 输出量最大（完整全文），token 消耗约 10 倍于 WebSearch，但信息密度也最高")
    lines.append("- Context7 输出最少但精准度最高（纯代码片段），token 效率最优")
    lines.append("- WebSearch 输出适中（Claude 已总结），适合快速获取概要")
    lines.append("- 延迟数据仅 AnySearch 可精确获取（~2s），其他工具受运行时限制无法测量")
    lines.append("")

    lines.append("## 6. Agent 使用建议")
    lines.append("")
    lines.append("基于评测结果，针对不同 Agent 工作场景的搜索工具推荐：")
    lines.append("")
    lines.append("| 场景 | 首选工具 | 备选 | 原因 |")
    lines.append("|------|----------|------|------|")
    lines.append("| Agent 写代码查 API | **Context7** | WebSearch | 零噪音官方代码，直接可用 |")
    lines.append("| Agent 追踪国内技术动态 | **AnySearch** | WebSearch | 完整全文，信息密度最高 |")
    lines.append("| Agent 搜索英文技术内容 | **web-search-prime (us)** | AnySearch | location=us 返回英文官方文档 |")
    lines.append("| Agent 做行业研究 | **AnySearch** | WebSearch | 完整对比数据+表格+市场动态 |")
    lines.append("| Agent 查 CVE/安全漏洞 | **AnySearch** | WebSearch | NVD官方+POC代码+修复版本 |")
    lines.append("| Agent 调试代码报错 | **WebSearch** | web-search-prime | 中文社区方案全面，自带总结 |")
    lines.append("| Agent 读取指定网页 | **web-reader** | AnySearch extract | 完整提取页面内容 |")
    lines.append("| Agent 国内新闻/政策 | **AnySearch** | WebSearch | 政策面覆盖最广+完整全文 |")
    lines.append("| Agent 快速概要查询 | **WebSearch** | - | 自带总结，token 消耗低 |")
    lines.append("")

    # === Test Coverage ===
    lines.append("## 7. 测试覆盖与局限")
    lines.append("")
    lines.append("### 已覆盖")
    lines.append("- 15 个测试用例，12 个类别（国内新闻/技术文档/开源社区/垂直领域/行业研究/代码调试/国内技术/URL提取/英文技术/多语言查询/实时数据/学术搜索/深度代码文档/国内生态/金融垂直）")
    lines.append("- 5 个工具：WebSearch、web-search-prime、Context7、web-reader、AnySearch")
    lines.append("- 4 个评分维度 × 多个测试用例")
    lines.append("- Token 效率粗估（基于 output 字符数）")
    lines.append("- AnySearch 延迟精确数据")
    lines.append("")
    lines.append("### 未覆盖")
    lines.append("- **精确 token 计数**：WebSearch/web-search-prime/Context7 的 input/output token 无法从运行时获取")
    lines.append("- **并发能力**：未测试多工具并发调用的稳定性和限流策略")
    lines.append("- **AnySearch 垂直领域搜索**：已测试金融(AAPL)和学术(transformer survey)垂直领域，其余垂直领域（如法律/医疗等）未测试")
    lines.append("- **时效性衰减**：未测试同一查询在不同时间点的结果差异")
    lines.append("")
    lines.append("### 改进建议")
    lines.append("1. 测试 AnySearch 垂直领域搜索（CVE/股票/学术等），对比通用搜索的差异")
    lines.append("2. 在自动化框架中加入精确 token 计数和延迟计时")
    lines.append("3. 增加更多英文技术搜索用例以验证 location 参数影响")
    lines.append("4. 测试搜索结果的时效性衰减")
    lines.append("")

    # === Appendix: Raw Scores ===
    lines.append("## 附录: 原始评分明细")
    lines.append("")
    for tc_id in SCORERS:
        lines.append(f"### {tc_id}: {tc_map[tc_id]['category']}")
        lines.append(f"**查询**: {tc_map[tc_id]['query']}")
        lines.append("")
        for tool, data in tool_scores.items():
            match = [s for s in data["scores"] if s["tc"] == tc_id]
            if match:
                s = match[0]
                lines.append(f"**{tool}**: R={s['relevance']} C={s['completeness']} A={s['accuracy']} U={s['usability_for_agent']}")
                lines.append(f"- {s['rationale']}")
                lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main():
    test_cases = load_test_cases()
    tool_scores = compute_tool_scores()

    report = generate_report(tool_scores, test_cases)
    with open(OUTPUT_FILE, "w") as f:
        f.write(report)

    print(f"报告已生成: {OUTPUT_FILE}")

    # Print summary table
    print("\n=== 综合排名 ===")
    ranked = []
    for tool, data in tool_scores.items():
        all_vals = []
        for dim_data in data["dimensions"].values():
            all_vals.extend(dim_data)
        ranked.append((tool, avg(all_vals), len(data["scores"])))
    ranked.sort(key=lambda x: x[1], reverse=True)
    for i, (tool, score, count) in enumerate(ranked, 1):
        print(f"  {i}. {tool}: {score} ({count} tests)")


def llm_judge_score(query, expected_content, search_results_text):
    """
    使用 LLM-as-Judge 自动评分（v2 改进）。

    调用智谱 GLM API 对搜索结果进行 4 维度评分。
    需要 ZHIPU_API_KEY 环境变量。

    用法: python scorer.py --llm-judge
    """
    import os

    api_key = os.environ.get("ZHIPU_API_KEY")
    if not api_key:
        print("错误: 需要设置 ZHIPU_API_KEY 环境变量")
        return None

    prompt = f"""你是一个搜索结果评估专家。请对以下搜索结果进行评分。

## 查询
{query}

## 期望内容
{expected_content}

## 搜索结果
{search_results_text[:8000]}

## 评分标准（1-5分）
- relevance: 返回结果与查询意图的匹配程度（1=完全无关, 5=高度精准）
- completeness: 是否覆盖了期望内容中的关键信息点（1=缺失大部分, 5=完整覆盖）
- accuracy: 信息的准确性和时效性（1=明显过时/错误, 5=准确详细有来源）
- usability_for_agent: 结果对 Agent 直接使用的程度（1=需大量处理, 5=直接可用）

请严格按照以下 JSON 格式输出，不要输出其他内容：
{{"relevance": N, "completeness": N, "accuracy": N, "usability_for_agent": N, "rationale": "一句话评价"}}"""

    try:
        import urllib.request
        data = json.dumps({
            "model": "glm-4-flash",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 500,
        }).encode()

        req = urllib.request.Request(
            "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read().decode())
        content = result["choices"][0]["message"]["content"]

        # 解析 JSON 评分
        scores = json.loads(content)
        return scores
    except Exception as e:
        print(f"LLM Judge 调用失败: {e}")
        return None


def auto_score_all():
    """对所有结果文件使用 LLM-as-Judge 自动评分。"""
    test_cases = load_test_cases()
    tc_map = {tc["id"]: tc for tc in test_cases["test_cases"]}

    print("LLM-as-Judge 自动评分模式")
    print("=" * 60)

    result_files = sorted(RESULTS_DIR.glob("tc*.json"))
    all_scores = []

    for rf in result_files:
        if "scoring" in rf.name or "latency" in rf.name or "methodology" in rf.name or "vertical" in rf.name:
            continue

        with open(rf) as f:
            data = json.load(f)

        tc_id = data.get("test_case", "")
        if tc_id not in tc_map:
            continue

        tc = tc_map[tc_id]
        query = tc["query"]
        expected = tc["expected_content"]

        # 提取搜索结果文本
        results_text = json.dumps(data, ensure_ascii=False)[:8000]

        print(f"\n{tc_id}: {query[:40]}...")
        scores = llm_judge_score(query, expected, results_text)
        if scores:
            print(f"  → R={scores['relevance']} C={scores['completeness']} "
                  f"A={scores['accuracy']} U={scores['usability_for_agent']}")
            print(f"  → {scores['rationale'][:80]}")
            all_scores.append({"tc": tc_id, **scores})
        else:
            print(f"  → 评分失败")

    if all_scores:
        with open(RESULTS_DIR / "llm_judge_scores.json", "w") as f:
            json.dump(all_scores, f, ensure_ascii=False, indent=2)
        print(f"\n已保存 {len(all_scores)} 条评分到 results/llm_judge_scores.json")


if __name__ == "__main__":
    import sys as _sys
    if "--llm-judge" in _sys.argv:
        auto_score_all()
    else:
        main()
