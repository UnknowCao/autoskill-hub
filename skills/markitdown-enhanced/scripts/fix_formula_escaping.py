r"""markitdown output post-processor - fix formula escaping errors.

Problem: markitdown 0.1.6 escapes * _ ^ inside $...$ math formulas as
markdown escape sequences (\* \\_ \^), breaking KaTeX rendering.

Fix: scan $...$ and $$...$$ regions, revert incorrect escapes.
Only touches formula regions; body text is untouched.

Usage (shared module):
    from fix_formula_escaping import fix_formulas_in_text
    fixed_text, fix_count = fix_formulas_in_text(md_text)
"""
from __future__ import annotations
import re


# 错误转义模式（在公式内部）
# 匹配「一个反斜杠 + 特殊字符」。repl 用函数返回纯字符（避免 backref 混淆）。
# 顺序：先匹配双反斜杠转义（\\_、\\\^），再匹配单反斜杠转义（\_、\^）。
_BAD_ESCAPES = [
    # 双反斜杠情形：文本里是两个反斜杠 + 字符 → 还原成一个下标/上标符号
    (re.compile(r"\\\\_"), lambda m: r"_"),   # \\_ → _
    (re.compile(r"\\\\\^"), lambda m: r"^"),  # \\^ → ^
    # 单反斜杠情形：文本里是一个反斜杠 + 字符
    (re.compile(r"\\\*"), lambda m: r"*"),     # \*  → *
    (re.compile(r"\\_"), lambda m: r"_"),       # \_  → _
    (re.compile(r"\\\^"), lambda m: r"^"),     # \^  → ^
]


def fix_formulas_in_text(text: str) -> tuple[str, int]:
    """修复文本中所有 $...$ / $$...$$ 公式内的错误转义。

    返回 (修复后文本, 修复点数)。
    """
    fixes = 0
    out_parts: list[str] = []

    # 用分割捕获 $...$ 段（含块级 $$）
    # 模式：匹配 $$...$$ 或 $...$，非贪婪
    # 标志：DOTALL 让 . 匹配换行（块公式跨行）
    pattern = re.compile(r"(\$\$[\s\S]+?\$\$|\$[^\$\n]+?\$)")

    last_end = 0
    for m in pattern.finditer(text):
        # 段前的正文（不动）
        out_parts.append(text[last_end:m.start()])
        formula = m.group(1)
        # 修复公式内部
        fixed = formula
        for rx, repl in _BAD_ESCAPES:
            new, n = rx.subn(repl, fixed)
            if n:
                fixes += n
                fixed = new
        out_parts.append(fixed)
        last_end = m.end()
    out_parts.append(text[last_end:])

    return "".join(out_parts), fixes
