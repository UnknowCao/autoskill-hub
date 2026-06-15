---
name: tavily
description: Tavily web search, content extraction, and research tools.
---

# Tavily Tools

## When to use which tool

| Need                         | Tool             | When                                                          |
| ---------------------------- | ---------------- | ------------------------------------------------------------- |
| Quick web search             | `web_search`     | Basic queries, no special options needed                      |
| Search with advanced options | `tavily_search`  | Need depth, topic, domain filters, time ranges, or AI answers |
| Extract content from URLs    | `tavily_extract` | Have specific URLs, need their content                        |

## web_search

Tavily powers this automatically when selected as the search provider. Use for
straightforward queries where you don't need Tavily-specific options.

| Parameter | Description              |
| --------- | ------------------------ |
| `query`   | Search query string      |
| `count`   | Number of results (1-20) |

## tavily_search

Use when you need fine-grained control over search behavior.

| Parameter         | Description                                                           |
| ----------------- | --------------------------------------------------------------------- |
| `query`           | Search query string (keep under 400 characters)                       |
| `search_depth`    | `basic` (default, balanced) or `advanced` (highest relevance, slower) |
| `topic`           | `general` (default), `news` (real-time updates), or `finance`         |
| `max_results`     | Number of results, 1-20 (default: 5)                                  |
| `include_answer`  | Include an AI-generated answer summary (default: false)               |
| `time_range`      | Filter by recency: `day`, `week`, `month`, or `year`                  |
| `include_domains` | Array of domains to restrict results to                               |
| `exclude_domains` | Array of domains to exclude from results                              |

### Search depth

| Depth      | Speed  | Relevance | Best for                                     |
| ---------- | ------ | --------- | -------------------------------------------- |
| `basic`    | Faster | High      | General-purpose queries (default)            |
| `advanced` | Slower | Highest   | Precision, specific facts, detailed research |

### Tips

- **Keep queries under 400 characters** — think search query, not prompt.
- **Break complex queries into sub-queries** for better results.
- **Use `include_domains`** to focus on trusted sources.
- **Use `time_range`** for recent information (news, current events).
- **Use `include_answer`** when you need a quick synthesized answer.

## tavily_extract

Use when you have specific URLs and need their content. Handles JavaScript-rendered
pages and returns clean markdown. Supports query-focused chunking for targeted
extraction.

| Parameter           | Description                                                        |
| ------------------- | ------------------------------------------------------------------ |
| `urls`              | Array of URLs to extract (1-20 per request)                        |
| `query`             | Rerank extracted chunks by relevance to this query                 |
| `extract_depth`     | `basic` (default, fast) or `advanced` (for JS-heavy pages, tables) |
| `chunks_per_source` | Chunks per URL, 1-5 (requires `query`)                             |
| `include_images`    | Include image URLs in results (default: false)                     |

### Extract depth

| Depth      | When to use                                                 |
| ---------- | ----------------------------------------------------------- |
| `basic`    | Simple pages — try this first                               |
| `advanced` | JS-rendered SPAs, dynamic content, tables, embedded content |

### Tips

- **Max 20 URLs per request** — batch larger lists into multiple calls.
- **Use `query` + `chunks_per_source`** to get only relevant content instead of full pages.
- **Try `basic` first**, fall back to `advanced` if content is missing or incomplete.
- If `tavily_search` results already contain the snippets you need, skip the extract step.

## Choosing the right workflow

Follow this escalation pattern — start simple, escalate only when needed:

1. **`web_search`** — Quick lookup, no special options needed.
2. **`tavily_search`** — Need depth control, topic filtering, domain filters, time ranges, or AI answers.
3. **`tavily_extract`** — Have specific URLs, need their full content or targeted chunks.

Combine search + extract when you need to find pages first, then get their full content.

### 🔴 CHECKPOINT: Escalation gates

Stop and confirm before crossing each gate. Do NOT auto-escalate without user confirmation.

| Gate | Trigger | Confirm |
|------|---------|---------|
| 🔴 Gate 1 | `web_search` → `tavily_search` | Basic results insufficient? Confirm the specific advanced options needed before upgrading. |
| 🔴 Gate 2 | Search → `tavily_extract` | Do you have specific URLs to extract? Do NOT extract all search results blindly — confirm which URLs to extract. |
| 🔴 Gate 3 | `extract_depth=basic` → `advanced` | `basic` returned incomplete/missing content? Confirm `advanced` is needed (slower, higher cost). |
| ⚠️ Gate 4 | Batch > 20 URLs | Max 20 URLs per request. Split into batches; confirm batch plan before each `tavily_extract` call. |

## 🚫 Anti-patterns: What NOT to do

These are common mistakes that waste resources or produce poor results. Avoid them.

### Tool selection mistakes

| # | ❌ Don't | ✅ Do instead | Why |
|---|---------|-------------|-----|
| 1 | Use `tavily_search` for a one-word lookup | Use `web_search` for simple queries | `tavily_search` costs more; escalate only when you need filters |
| 2 | Use `web_search` when you need domain/time filtering | Use `tavily_search` with `include_domains` / `time_range` | `web_search` lacks fine-grained controls |
| 3 | Extract every URL from a search result page | Confirm Gate 2: pick only the 2-3 most relevant URLs | Blind extraction wastes requests and clutters output |

### Parameter mistakes

| # | ❌ Don't | ✅ Do instead | Why |
|---|---------|-------------|-----|
| 4 | Send a full prompt (>400 chars) as a search query | Trim to keywords; split complex topics into sub-queries | Search engines work on keywords, not natural language prompts |
| 5 | Default to `search_depth=advanced` for every query | Start with `basic`; escalate via Gate 3 only if needed | `advanced` is slower and costs more; `basic` suffices for most queries |
| 6 | Use `extract_depth=advanced` without trying `basic` first | Always try `basic` first; retry with `advanced` only if content is missing | `advanced` is for JS-heavy SPAs and tables — overkill for static pages |
| 7 | Omit `time_range` when the user asks for "latest" / "recent" | Always set `time_range` when recency matters | Without it, results may include outdated content |

### Workflow mistakes

| # | ❌ Don't | ✅ Do instead | Why |
|---|---------|-------------|-----|
| 8 | Skip `web_search` and jump straight to `tavily_extract` | Follow escalation: search → confirm URLs → extract | You need URLs to extract; searching finds them first |
| 9 | Use `include_answer=true` when the user needs raw sources | Use `include_answer=false` (default) for source-backed research | AI summaries can hallucinate; raw results are verifiable |
| 10 | Send 25 URLs in one `tavily_extract` call | Batch: max 20 per call; split into 20 + 5 | API rejects >20 URLs per request |
