#!/usr/bin/env python3
"""
搜索工具选择器 — 基于评测数据的查询→工具推荐引擎

输入查询特征，输出推荐工具、调用参数、备选方案和理由。
评测基础: 15 TC × 5 工具 × 52 组合，LLM-Judge 验证一致 (deviation 0.46)。

用法:
  from search_selector import recommend_tool
  result = recommend_tool(
      query="Next.js middleware 配置",
      language="zh",          # zh/en
      intent="code",          # code/search/extract/research/finance/academic
      depth="quick",          # quick/deep
  )
"""

# 查询意图 → (首选工具, 备选工具, 调用参数, 理由)
RULES = {
    # intent: (primary, fallback, params, reason)
    "code": {
        "primary": "Context7",
        "fallback": "WebSearch",
        "params": {"tool": "Context7", "steps": "resolve-library-id → query-docs"},
        "reason": "Context7 直接返回官方代码片段，零噪音，Agent 可直接粘贴使用。评测均分: 编程文档 5/5/5/5 (TC02/TC03/TC10/TC13)。",
        "constraints": [
            "仅限编程库/框架的 API 文档和配置示例",
            "不适合代码调试(OS 级错误)、版本追踪(release notes)、技术选型对比(只返回单库)",
            "国内技术(智谱 GLM 等)覆盖不到",
        ],
    },
    "extract": {
        "primary": "web-reader",
        "fallback": "AnySearch",
        "params": {"tool": "web-reader", "format": "markdown"},
        "reason": "web-reader 完整提取已知 URL 内容，准确率极高。评测: TC08 5/4/5/3。",
        "constraints": [
            "只能提取已知 URL，不能用于搜索发现",
            "输出含 CSS/JS/favicon metadata 噪音，需过滤",
        ],
    },
    "finance": {
        "primary": "AnySearch",
        "fallback": None,
        "params": {"tool": "AnySearch", "mode": "vertical", "domain": "finance"},
        "reason": "AnySearch 金融垂直是独有能力: 实时价格/分析师评级/EPS 超预期对比。其他工具无法提供结构化金融数据。TC15: 5/5/5/5。",
        "constraints": [
            "无替代工具，金融数据必须用 AnySearch",
            "token 消耗约 12K (WebSearch 的 10 倍)",
        ],
    },
    "research": {
        "primary": "AnySearch",
        "fallback": "WebSearch",
        "params": {"tool": "AnySearch", "mode": "general"},
        "reason": "AnySearch 返回完整文章全文(~24K 字符)，信息密度 10x WebSearch。行业分析/政策追踪场景碾压。TC05: 信息量 39K vs 3K 字符。",
        "constraints": [
            "token 消耗高(~12K/查询)，深度研究才值得",
            "快速概览用 WebSearch 更划算",
        ],
    },
    "academic": {
        "primary": "WebSearch",
        "fallback": None,
        "params": {"tool": "WebSearch"},
        "reason": "学术搜索 WebSearch 精准匹配 arXiv/OpenReview/Semantic Scholar。AnySearch 垂直学术匹配精度差。TC12: WebSearch 5/5/5/5 vs AnySearch 3/3/4/3。",
        "constraints": [
            "不要用 AnySearch 垂直学术搜索(匹配精度差)",
            "WebSearch 自带 Claude 总结，对论文综述特别有用",
        ],
    },
    "security": {
        "primary": "AnySearch",
        "fallback": "WebSearch",
        "params": {"tool": "AnySearch", "mode": "general"},
        "reason": "CVE 漏洞查询: AnySearch 返回 NVD 官方详情 + POC 代码 + 修复版本，信息深度最高。TC04: 5/5/5/5。WebSearch 同样优秀(5/5/5/5)，备选可用。",
        "constraints": [
            "不要用 Context7 查 CVE(只返回通用安全扫描工具，TC04: 1/1/2/1)",
        ],
    },
    "search": {
        "primary": "WebSearch",
        "fallback": "web-search-prime",
        "params": {"tool": "WebSearch"},
        "reason": "WebSearch 自带 Claude 结构化总结，usability 4.36 vs web-search-prime 3.36 (+1.0)。中文日常搜索/快速概览首选。",
        "constraints": [
            "不要同时调用 WebSearch 和 web-search-prime(同引擎，浪费 token)",
            "英文技术搜索用 web-search-prime location=us",
        ],
    },
}

# 语言覆盖规则
LANGUAGE_OVERRIDES = {
    "en": {
        "search": {
            "primary": "web-search-prime",
            "params": {"tool": "web-search-prime", "location": "us"},
            "reason": "英文技术搜索 location=us 返回官方文档+英文社区，远优于默认 cn。TC03: web-search-prime(us) 5/4/5/4 vs WebSearch(cn) 3/3/4/3。",
        },
        "code": {
            "extra_note": "Context7 无语言限制，英文代码文档直接可用。",
        },
    },
    "zh": {
        "search": {
            "reason": "WebSearch 中文内容搜索质量优秀(国内新闻/技术动态/行业研究)，自带 Claude 总结。TC01/TC07: 5/5/4/5。",
        },
    },
}


def classify_intent(query: str) -> str:
    """从查询内容推断意图类型。"""
    q = query.lower()

    # 金融/股票
    stock_keywords = ["stock", "股价", "股票", "aapl", "tsla", "市值", "pe", "eps", "评级", "analyst", "price target", "基金", "fund"]
    if any(k in q for k in stock_keywords):
        return "finance"

    # CVE/安全
    security_keywords = ["cve-", "漏洞", "vulnerability", "exploit", "poc", "0day", "安全"]
    if any(k in q for k in security_keywords):
        return "security"

    # 学术论文
    academic_keywords = ["paper", "survey", "arxiv", "论文", "综述", "review", "注意力机制", "transformer", "mechanism"]
    if any(k in q for k in academic_keywords):
        return "academic"

    # URL 提取
    if q.startswith("http://") or q.startswith("https://"):
        return "extract"

    # 技术选型（vs/comparison 优先于 code，因为 Context7 不适合对比场景）
    comparison_keywords = [" vs ", "对比", "比较", "comparison", "versus", "选型"]
    if any(k in q for k in comparison_keywords):
        return "research"

    # 编程文档
    code_keywords = ["api", "sdk", "配置", "config", "middleware", "validator", "serializer", "如何写", "怎么用", "example", "tutorial", "文档"]
    code_frameworks = ["react", "next.js", "django", "kubernetes", "k8s", "tokio", "rust", "python", "fastapi", "flask", "vue", "angular"]
    if any(k in q for k in code_keywords) or any(f in q for f in code_frameworks):
        return "code"

    # 深度研究
    research_keywords = ["行业", "市场", "分析", "趋势", "政策", "报告", "ranking", "market", "industry", "report"]
    if any(k in q for k in research_keywords):
        return "research"

    return "search"


def recommend_tool(query: str, language: str | None = None, intent: str | None = None, depth: str | None = None) -> dict:
    """
    根据查询特征推荐搜索工具。

    Args:
        query: 搜索查询文本
        language: zh/en (自动检测时传 None)
        intent: code/search/extract/research/finance/academic/security (自动推断时传 None)
        depth: quick/deep (影响是否推荐 token 消耗高的工具)

    Returns:
        {
            "query": str,
            "intent": str,
            "language": str,
            "primary": {"tool": str, "params": dict},
            "fallback": {"tool": str, "params": dict} | None,
            "reason": str,
            "constraints": list[str],
        }
    """
    # 自动推断
    if intent is None:
        intent = classify_intent(query)
    if language is None:
        language = "zh" if any("一" <= c <= "鿿" for c in query) else "en"

    # 基础规则
    rule = RULES.get(intent, RULES["search"])

    # 语言覆盖
    lang_override = LANGUAGE_OVERRIDES.get(language, {}).get(intent, {})

    primary_tool = lang_override.get("primary", rule["primary"])
    primary_params = lang_override.get("params", rule["params"])
    primary_reason = lang_override.get("reason", rule["reason"])

    extra_note = LANGUAGE_OVERRIDES.get(language, {}).get(intent, {}).get("extra_note", "")

    fallback_tool = rule.get("fallback")
    fallback_params = None
    if fallback_tool:
        fallback_rule = RULES.get(_intent_for_tool(fallback_tool), RULES["search"])
        fallback_params = fallback_rule["params"]

    # depth 调整: quick 时避免高 token 工具
    if depth == "quick" and primary_tool == "AnySearch" and intent in ("research", "security"):
        if fallback_tool:
            primary_tool, fallback_tool = fallback_tool, primary_tool
            primary_params = {"tool": fallback_tool}
            primary_reason = f"[快速模式] {primary_reason.replace('AnySearch', 'WebSearch(fallback)')}。深度研究用 AnySearch。"

    result = {
        "query": query,
        "intent": intent,
        "language": language,
        "primary": {
            "tool": primary_tool,
            "params": primary_params,
        },
        "fallback": {
            "tool": fallback_tool,
            "params": fallback_params,
        } if fallback_tool else None,
        "reason": primary_reason,
        "constraints": rule.get("constraints", []),
    }

    if extra_note:
        result["extra_note"] = extra_note

    return result


def _intent_for_tool(tool: str) -> str:
    """反查工具对应的默认 intent。"""
    for intent, rule in RULES.items():
        if rule["primary"] == tool:
            return intent
    return "search"


def format_recommendation(rec: dict) -> str:
    """格式化推荐结果为可读文本。"""
    lines = []
    lines.append(f"查询: {rec['query']}")
    lines.append(f"意图: {rec['intent']} | 语言: {rec['language']}")
    lines.append("")
    lines.append(f"→ 首选: {rec['primary']['tool']}")
    if rec['primary'].get('params'):
        lines.append(f"  参数: {rec['primary']['params']}")
    lines.append(f"  理由: {rec['reason']}")
    if rec.get('fallback'):
        lines.append(f"  备选: {rec['fallback']['tool']}")
    if rec.get('constraints'):
        lines.append(f"  约束:")
        for c in rec['constraints']:
            lines.append(f"    - {c}")
    return "\n".join(lines)


if __name__ == "__main__":
    # 示例
    examples = [
        "Next.js App Router middleware 配置",
        "CVE-2024-9264 漏洞详情",
        "AAPL stock price analyst rating",
        "transformer attention mechanism survey 2025",
        "2026年5月中国AI大模型政策",
        "Rust tokio vs async-std comparison",
        "https://docs.anthropic.com/en/docs/claude-code/overview",
        "Dify 0.15 新功能",
        "Kubernetes HPA custom metrics 配置",
    ]

    for q in examples:
        rec = recommend_tool(q)
        print(format_recommendation(rec))
        print("-" * 60)
