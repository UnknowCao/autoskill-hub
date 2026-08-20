#!/usr/bin/env python3
"""推敲（tuiqiao）benchmark 回归校验脚本。

对 examples/benchmark/cases.md 做全量静态回归：
  1. 每个 case 结构完整（输入/改写/评分/ban 齐全）
  2. 改写文本不含该 case 的 ban 禁用痕迹
  3. 改写文本不含长破折号、表情符号
  4. 改写文本不混用 "" 与 「」 两种引号样式
  5. 5 维评分各在 1–10，总分与标注一致，且 ≥35（<35 应打回重写）

用法：python scripts/backtest.py examples/benchmark/cases.md
退出码：0 = 全部通过；1 = 存在失败项。
仅用标准库，无第三方依赖。
"""

import re
import sys
from pathlib import Path

EMOJI_RE = re.compile(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F]")
CASE_SPLIT_RE = re.compile(r"^## Case\s+(\d+)", re.MULTILINE)
DIM_RE = re.compile(r"^\|\s*(\S+?)\s*\|\s*(\d+)\s*\|\s*(.+?)\s*\|", re.MULTILINE)
TOTAL_RE = re.compile(r"\*\*总分\*\*：\s*(\d+)")
BAN_RE = re.compile(r"\*\*ban\*\*:\s*`([^`]+)`")


def extract_block(text, start_marker, end_marker):
    """提取两个加粗小节标记之间的正文，去掉引用前缀 '> '。"""
    m = re.search(re.escape(start_marker) + r"\s*\n", text)
    if not m:
        return None
    tail = text[m.end():]
    e = re.search(re.escape(end_marker), tail)
    block = tail if e is None else tail[:e.start()]
    lines = []
    for line in block.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            line = line[1:].strip()
        lines.append(line)
    return "".join(lines)


def check_quote_mix(text):
    """引号样式混用检测："" 与 「」 不得同时出现。"""
    has_curly = "“" in text or "”" in text
    has_corner = "「" in text or "」" in text
    return has_curly and has_corner


def main(path):
    raw = Path(path).read_text(encoding="utf-8")
    cases = {}
    for m in CASE_SPLIT_RE.finditer(raw):
        cases[m.group(1)] = m.start()
    if not cases:
        print("FAIL: 未解析到任何 case")
        return 1

    order = sorted(cases, key=lambda k: cases[k])
    keys = list(cases.keys())
    boundaries = [cases[k] for k in keys] + [len(raw)]
    results = []
    for i, cid in enumerate(order):
        block = raw[boundaries[i]:boundaries[i + 1]]
        problems = []

        rewrite = extract_block(block, "**改写**", "**评分**")
        input_text = extract_block(block, "**输入**", "**问题点**")
        if input_text is None or not input_text.strip():
            problems.append("缺「输入」块")
        if rewrite is None or not rewrite.strip():
            problems.append("缺「改写」块")
        else:
            ban_m = BAN_RE.search(block)
            if not ban_m:
                problems.append("缺 ban 行")
            else:
                for token in ban_m.group(1).split("|"):
                    if token.strip() and token in rewrite:
                        problems.append(f"改写含禁用痕迹: {token}")
            if "——" in rewrite:
                problems.append("改写含长破折号 ——")
            if EMOJI_RE.search(rewrite):
                problems.append("改写含表情符号")
            if check_quote_mix(rewrite):
                problems.append("改写混用 “” 与 「」 引号样式")

        dims = DIM_RE.findall(block)
        total_m = TOTAL_RE.search(block)
        if total_m:
            total = int(total_m.group(1))
            if len(dims) != 5:
                problems.append(f"评分维度数 {len(dims)} != 5")
            else:
                dim_sum = 0
                for name, score, evidence in dims:
                    score = int(score)
                    if not 1 <= score <= 10:
                        problems.append(f"维度 {name} 得分 {score} 超出 1–10")
                    if not evidence.strip():
                        problems.append(f"维度 {name} 缺证据")
                    dim_sum += score
                if dim_sum != total:
                    problems.append(f"维度加总 {dim_sum} != 总分 {total}")
                if total < 35:
                    problems.append(f"总分 {total} < 35，应打回重写")
        else:
            problems.append("缺总分行")

        results.append((cid, problems))

    print(f"{'Case':>5}  {'结果':<6}  问题")
    failed = 0
    for cid, problems in results:
        if problems:
            failed += 1
            print(f"{cid:>5}  FAIL     {problems[0]}")
            for p in problems[1:]:
                print(f"{'':>5}          {p}")
        else:
            print(f"{cid:>5}  PASS")
    print("-" * 60)
    print(f"总计 {len(results)} 例，PASS {len(results) - failed}，FAIL {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
