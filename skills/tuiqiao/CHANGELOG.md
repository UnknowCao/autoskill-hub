# CHANGELOG

## 2026-08-20

### 新增

- **benchmark 评测集**：`examples/benchmark/cases.md` 15 条对抗样例，覆盖 patterns.md 全部 22 类模式 + 反例 N4/N5 + 失败模式 F3/F4，每条带改写前后与 5 维评分。为什么：skill 此前只有 3 条 test-prompts，没有任何可展示的改写产物，也无法回归。
- **回归脚本**：`scripts/backtest.py`（纯标准库），全量校验 benchmark 的禁用痕迹、破折号、表情符号、引号混用、评分加总。已做反向验证（植入违例必报 FAIL）。为什么：让"改得行不行"从手感变成可跑命令。
- **README / LICENSE**：按公开仓库标准补齐出生证（MIT，署名 unknowCao）。

### 修改

- SKILL.md：修正 description 中 skill 名拼写（tuikiao→tuiqiao）；补负触发词（不用于英文文本、代码、配置文件）。
- voice-adoption.md：新增「素材来源与使用边界」声明；`references/voices/` 声明为本地扩展，不随公开仓库分发。
- 清理 references/ 下两个 .bak 遗留备份（基线已另存）。

### 为什么改

- 负触发词初版含「不要用于公告重写」，与内部工作流（公告保守处理）矛盾，改为只排除英文/代码/配置。
- 声线档案不随仓库公开（作者权利考量），相关文件全部改为条件加载，公开版本缺失 voices/ 时自动走中立路径。
