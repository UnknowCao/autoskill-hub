# Patent Forge Reference

> **工具分层说明**：本文件记录 3 个**专利检索专用 API**（Optional 增强层），叠加在主搜索工具之上（详见 `shared_workflow.md` § Phase 2 **搜索工具分层**）。
> 主搜索工具按以下优先级探测：① `anysearch` skill（首选）→ ② `tavily` skill（次选）→ ③ `fetch_webpage` 内置工具（兜底，仅抓已知 URL）。
>
> **专利专用 API 优先级**（配置了对应 key 才启用，可叠加在任一主搜索层上）：
> 1. **CNIPA.AI**（`CNIPA_API_KEY`）— **首选**，以中国专利为中心，中英双语自动翻译匹配，对中国专利覆盖最佳
> 2. SerpAPI（`SERPAPI_KEY`）— Google Patents 关键词检索，全球专利覆盖
> 3. Exa.ai（`EXA_API_KEY`）— 语义检索，适合概念模糊场景
>
> 未配置任何 key → 跳过本文件以下三节，仅用主搜索工具分层检索。

## CNIPA.AI API（中国专利专用检索 — 首选 Optional 增强层）

> **来源**：https://cnipa.ai/zh/api-docs（2026-07-23 抓取）。CNIPA.AI 是独立第三方工具，与中国国家知识产权局（CNIPA）无关联；专利数据来源于公开数据库。

### 身份验证

所有请求需在 `Authorization` 头以 Bearer 令牌形式携带 API 密钥。在 https://cnipa.ai/register 创建账户获取。

### 检索端点（本 skill 仅使用以下 2 个检索端点）

```
GET https://api.cnipa.ai/v1/patents/search?q=<keywords>
GET https://api.cnipa.ai/v1/patents/:id
```

### Search 参数（query string）

| 参数 | 说明 | 示例 |
|------|------|------|
| `q` | 关键词（中英双语，系统自动翻译匹配）| `q=solid-state battery cathode material` |
| 申请人 | 申请人过滤（文档未暴露 query 参数名，优先用 `q` 传公司名）| `q=Huawei` / `q=BYD` |
| IPC 分类号 | 用 `q` 传 IPC 码配合关键词 | `q=H01M battery` / `q=G06F` |
| 公开日范围 | UI 支持，API 参数名未公开 | 若需精确日期过滤，回退 SerpAPI |

### Search 示例

```bash
curl -X GET "https://api.cnipa.ai/v1/patents/search?q=(solid-state%20battery)%20cathode%20material" \
  -H "Authorization: Bearer ${CNIPA_API_KEY}" \
  -H "Content-Type: application/json"
```

### 检索技巧（来自官方 Patent Search Guide）

- **双语检索**：可输入英文，系统自动翻译并匹配中文专利（如 `electric vehicle battery` 自动匹配中文电动汽车电池专利）
- **精确关键词**：`solid-state battery cathode material` 比 `battery` 更精确
- **组合检索**：用空格分隔多个关键词
- **IPC + 关键词组合**：如 `H01M battery` 提升准确度
- 专利类型过滤：发明 / 实用新型 / 外观设计

### Detail 端点

`GET /patents/:id` 通过 ID 获取专利详情（权利要求、说明书、法律状态等），用于 Step 2.6 新颖性分析中深入对比最接近现有技术。

### 本 skill 不使用的端点（红线声明）

CNIPA.AI 另有 2 个**撰写端点**（`POST /patent-writing/analyze`、`POST /patent-writing/generate-claims`），本 skill **明确禁用**：
- 权利要求撰写受 **Checkpoint 3A-claims + Anti-Pattern 红线**管控，必须由本 skill 按中国专利法实施细则规范自行撰写并经用户确认
- 外部 AI 生成的权利要求存在不支持说明书、用语不规范（专利法 26.4）的风险
- 详见 `anti_patterns.md` Anti-Pattern #19

### 故障处理

- HTTP 401/403 → key 无效或额度耗尽，告知用户检查 `CNIPA_API_KEY`，回退到 SerpAPI/Exa.ai 或主搜索分层
- 0 结果 → 用同义词/IPC 码重试一次 → 仍 0 结果则回退 SerpAPI/Exa.ai + 主搜索分层
- 429 限流 → 跳过 CNIPA.AI，审计日志记录状态

---

## SerpAPI Google Patents (Structured Search — Optional Enhancement Layer)

### Endpoint

```
GET https://serpapi.com/search.json?engine=google_patents
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `engine` | Yes | Must be `google_patents` |
| `api_key` | Yes | Your SerpAPI key |
| `q` | Yes | URL-encoded Boolean query |
| `num` | No | Results per page (10-100) |
| `sort` | No | `new` or `old` |
| `language` | No | `ENGLISH`, `CHINESE`, etc. |
| `status` | No | `GRANT` or `APPLICATION` |

### Query Syntax

```
(machine learning) AND (recommendation)
(AI) OR (artificial intelligence)
assignee:(Google)
inventor:(Smith)
```

### Response Structure

```json
{
  "organic_results": [
    {
      "publication_number": "US12345678B2",
      "title": "Patent Title",
      "snippet": "Description...",
      "priority_date": "2020-01-15",
      "assignee": "Tech Corp",
      "inventor": "John Smith"
    }
  ]
}
```

### Example

```bash
curl -s "https://serpapi.com/search.json?engine=google_patents&q=(machine%20learning)%20AND%20(recommendation)&api_key=KEY&num=20"
```

---

## Exa.ai Search API (Semantic Search)

### Endpoint

```
POST https://api.exa.ai/search
```

### Headers

| Header | Required | Value |
|--------|----------|-------|
| `x-api-key` | Yes | Your Exa.ai API key |
| `Content-Type` | Yes | `application/json` |

### Request Body

```json
{
  "query": "semantic description of the invention",
  "type": "neural",
  "numResults": 20,
  "includeDomains": ["patents.google.com", "patentscope.wipo.int", "espacenet.com"],
  "contents": {
    "text": true,
    "summary": true
  }
}
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Natural language search query |
| `type` | enum | `neural` (semantic), `fast`, `auto`, `deep` |
| `numResults` | int | Results to return (max 100) |
| `includeDomains` | array | Restrict to specific domains |
| `excludeDomains` | array | Exclude domains |
| `category` | enum | `research paper`, `pdf`, `news`, etc. |
| `startPublishedDate` | string | ISO 8601 date filter |
| `contents.text` | bool | Include full text |
| `contents.summary` | bool | Include AI summary |

### Response Structure

```json
{
  "results": [
    {
      "title": "Patent Title",
      "url": "https://patents.google.com/patent/US12345678B2",
      "publishedDate": "2023-01-15",
      "summary": "AI-generated summary of the patent...",
      "text": "Full patent text content..."
    }
  ]
}
```

### Patent Domains

Use these in `includeDomains` for patent search:
- `patents.google.com` - Google Patents
- `patentscope.wipo.int` - WIPO PatentScope
- `espacenet.com` - European Patent Office
- `patents.justia.com` - Justia Patents

### Example Request

```bash
curl -X POST 'https://api.exa.ai/search' \
  -H 'x-api-key: YOUR_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "machine learning calendar scheduling focus time recommendation",
    "type": "neural",
    "numResults": 10,
    "includeDomains": ["patents.google.com"],
    "contents": {"summary": true}
  }'
```

---

## Application Form Format

完整的结构模板与 8 节顺序定义在 [`../assets/templates/standard_application.md`](../assets/templates/standard_application.md)（单一事实源）。撰写 `--doc-type application` 时直接加载该模板，此处不再重复以避免漂移。

> 注：摘要 / 权利要求书 / 说明书附图 为中国专利法实施细则第 23 条及审查指南的强制要求，不可省略。

---

## Language Conventions

### 避免使用

| 类型 | 示例 |
|------|------|
| 产品名称 | iPhone, MacBook, Galaxy |
| UI 术语 | 按钮, 页面, 弹窗, 下拉框 |
| 品牌名称 | Google, Apple, Microsoft |
| 口语化 | 然后, 接着, 之后 |

### 应该使用

| 类型 | 示例 |
|------|------|
| 设备 | 移动终端设备, 便携式计算设备, 显示装置 |
| UI 元素 | 用户交互元素, 显示界面, 输入组件, 选择控件 |
| 通用术语 | 处理单元, 存储模块, 通信接口 |
| 专利表述 | 响应于, 根据, 基于, 用于 |

### Standard Phrases

- `一种...` - 发明名称开头
- `包括/包含` - 描述组成部分
- `用于...` - 描述功能目的
- `其特征在于` - 引出创新点
- `所述...` - 指代前文元素
- `根据...确定...` - 逻辑关系
- `响应于...` - 触发条件
- `配置为...` - 模块功能
