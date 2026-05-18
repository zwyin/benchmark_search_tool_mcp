#!/usr/bin/env python3
"""
搜索工具对比评测 CLI - 一键运行测试 + 评分 + 生成报告

用法:
  python run_benchmark.py run      # 运行所有测试（调用搜索工具）
  python run_benchmark.py score    # 对已有结果评分并生成报告
  python run_benchmark.py full     # run + score

支持工具:
  - WebSearch (通过 web-search-prime 代理，同引擎)
  - web-search-prime (智谱 MCP)
  - Context7 (编程文档)
  - AnySearch (通用 + 垂直领域)
  - web-reader (URL 提取)
"""

import argparse
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"
TEST_CASES_FILE = BASE_DIR / "test_cases.json"
ANYSEARCH_CLI = Path.home() / ".claude/skills/anysearch/scripts/anysearch_cli.py"


def load_test_cases():
    with open(TEST_CASES_FILE) as f:
        return json.load(f)


# ── 工具调用器 ──────────────────────────────────────────────

def call_anysearch(query, max_results=10, domain=None, sub_domain=None, zone=None):
    """调用 AnySearch CLI，返回 (results_json, latency_ms, error)"""
    cmd = ["python3", str(ANYSEARCH_CLI), "search", query, "--max_results", str(max_results)]
    if domain:
        cmd += ["--domain", domain, "--sub_domain", sub_domain]
    if zone:
        cmd += ["--zone", zone]

    start = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        latency = int((time.time() - start) * 1000)
        if r.returncode != 0:
            return None, latency, r.stderr[:500]
        return r.stdout, latency, None
    except subprocess.TimeoutExpired:
        return None, 60000, "timeout"
    except Exception as e:
        return None, 0, str(e)


def call_context7(library_name, query):
    """调用 Context7（两步），返回 (result_text, latency_ms, error)"""
    start = time.time()
    try:
        # Step 1: resolve
        r1 = subprocess.run(
            ["python3", "-c", f"""
import json, urllib.request
req = urllib.request.Request(
    "https://context7.com/api/v1/tools/resolve_library_id",
    data=json.dumps({{"libraryName": "{library_name}", "query": "{query}"}}).encode(),
    headers={{"Content-Type": "application/json"}})
resp = urllib.request.urlopen(req, timeout=30)
data = json.loads(resp.read())
print(json.dumps(data))
"""],
            capture_output=True, text=True, timeout=30
        )
        if r1.returncode != 0:
            return None, int((time.time() - start) * 1000), f"resolve failed: {r1.stderr[:200]}"

        libs = json.loads(r1.stdout.strip())
        if not libs:
            return None, int((time.time() - start) * 1000), "no library found"

        lib_id = libs[0].get("id", "")

        # Step 2: query docs
        r2 = subprocess.run(
            ["python3", "-c", f"""
import json, urllib.request
req = urllib.request.Request(
    "https://context7.com/api/v1/tools/get_library_docs",
    data=json.dumps({{"libraryId": "{lib_id}", "query": "{query}", "tokens": 5000}}).encode(),
    headers={{"Content-Type": "application/json"}})
resp = urllib.request.urlopen(req, timeout=30)
print(resp.read().decode())
"""],
            capture_output=True, text=True, timeout=30
        )
        latency = int((time.time() - start) * 1000)
        if r2.returncode != 0:
            return None, latency, f"query failed: {r2.stderr[:200]}"
        return r2.stdout, latency, None

    except Exception as e:
        return None, int((time.time() - start) * 1000), str(e)


# ── 测试执行器 ──────────────────────────────────────────────

TOOL_RUNNERS = {
    "AnySearch": lambda tc: call_anysearch(
        tc["query"],
        domain=tc.get("_domain"),
        sub_domain=tc.get("_sub_domain"),
        zone=tc.get("_zone"),
    ),
    "Context7": lambda tc: call_context7(
        tc.get("_library_name", tc["query"].split()[0]),
        tc["query"],
    ),
}


def run_single_tc(tc):
    """执行单个测试用例，返回 {tool_name: result_dict}"""
    results = {}
    tc_id = tc["id"]
    tools = tc.get("applicable_tools", [])

    print(f"\n{'='*60}")
    print(f"  {tc_id}: {tc['category']} — {tc['query'][:50]}...")
    print(f"  适用工具: {', '.join(tools)}")
    print(f"{'='*60}")

    for tool in tools:
        if tool in TOOL_RUNNERS:
            print(f"  → {tool} ... ", end="", flush=True)
            output, latency, error = TOOL_RUNNERS[tool](tc)

            if error:
                print(f"ERROR ({latency}ms): {error[:80]}")
                results[tool] = {"error": error, "latency_ms": latency}
            else:
                chars = len(output) if output else 0
                est_tokens = chars // 2  # 粗估
                print(f"OK ({latency}ms, {chars} chars, ~{est_tokens} tokens)")
                results[tool] = {
                    "output_preview": output[:500] if output else "",
                    "output_chars": chars,
                    "est_tokens": est_tokens,
                    "latency_ms": latency,
                }
        else:
            print(f"  → {tool}: 跳过（需在 Claude Code 内部调用，CLI 不支持）")

    return results


def save_tc_result(tc_id, results):
    """保存测试结果到 JSON"""
    outfile = RESULTS_DIR / f"{tc_id.lower()}_rerun_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(outfile, "w") as f:
        json.dump({
            "test_case": tc_id,
            "timestamp": datetime.now().isoformat(),
            "results": results,
        }, f, ensure_ascii=False, indent=2)
    print(f"  已保存: {outfile.name}")


# ── 评分与报告（复用 scorer.py 的逻辑）──────────────────────

def run_score():
    """调用 scorer.py 生成报告"""
    scorer = BASE_DIR / "scorer.py"
    print("\n生成评分报告...")
    r = subprocess.run(
        ["python3", str(scorer)],
        capture_output=True, text=True, timeout=30
    )
    if r.returncode == 0:
        print(r.stdout)
    else:
        print(f"评分失败: {r.stderr}")


# ── 主入口 ──────────────────────────────────────────────────

def cmd_run(args):
    """运行测试"""
    RESULTS_DIR.mkdir(exist_ok=True)
    tc_data = load_test_cases()

    print(f"搜索工具评测 - 运行模式")
    print(f"测试用例: {len(tc_data['test_cases'])} 个")
    print(f"可执行工具: {list(TOOL_RUNNERS.keys())}")
    print(f"说明: WebSearch/web-search-prime/web-reader 需在 Claude Code 内调用，CLI 模式仅支持 AnySearch 和 Context7")

    for tc in tc_data["test_cases"]:
        results = run_single_tc(tc)
        if results:
            save_tc_result(tc["id"], results)

    print(f"\n所有可执行测试完成。")


def cmd_score(args):
    """评分并生成报告"""
    run_score()


def cmd_full(args):
    """运行 + 评分"""
    cmd_run(args)
    cmd_score(args)


def main():
    parser = argparse.ArgumentParser(
        description="搜索工具对比评测 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run_benchmark.py run       # 运行所有可执行的搜索测试
  python run_benchmark.py score     # 评分并生成报告
  python run_benchmark.py full      # 完整流程
        """
    )
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("run", help="运行搜索测试")
    sub.add_parser("score", help="评分并生成报告")
    sub.add_parser("full", help="运行 + 评分")

    args = parser.parse_args()
    if args.command == "run":
        cmd_run(args)
    elif args.command == "score":
        cmd_score(args)
    elif args.command == "full":
        cmd_full(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
