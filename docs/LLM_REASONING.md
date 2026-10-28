# LLM reasoning effort

All commands exposing the shared LLM arguments accept
`--llm-reasoning-effort {none,minimal,low,medium,high,xhigh,max}` alongside
`--llm-provider` and `--llm-model`. This includes review, translation,
transcription postprocessing, OCR processing, and OCR fusion. The audit report
and browser do not run LLM judgments and do not acquire LLM options through this
change.

For example:

```text
scinoephile review original.srt --outfile reviewed.srt --json review.json \
  --llm-provider openai --llm-model gpt-6-luna --llm-reasoning-effort xhigh
```

Python callers use `OpenAIProvider(model="gpt-6-luna", reasoning_effort="xhigh")`
or `DeepSeekProvider(reasoning_effort="high")`. `ReasoningEffort` is also exported
from `scinoephile.core.llms` for typed configuration.

Omitting the option preserves existing API defaults and cache identities.
OpenAI forwards explicit levels as `reasoning_effort`; the selected model's API
validates level and tool compatibility. DeepSeek enables thinking for explicit
levels and maps minimal to low, medium and xhigh to high, and preserves low,
high, and max. Mappings are logged. Explicit none disables DeepSeek thinking
without sending an unsupported none effort value. Unknown level names are
rejected before a request. New OpenAI-compatible provider subclasses must
explicitly implement reasoning configuration rather than silently ignoring it.

Effective request configuration enters both response-cache identity and explicit
prompt-cache routing, separating runs at different effective reasoning levels.
Equivalent DeepSeek mappings share a cache identity. Existing authored JSON
answers are durable decisions, not response-cache entries; changing reasoning
settings does not discard or rerun them automatically. Use a separate decisions
JSON when comparing configurations while preserving prior review work.

The setting does not change the default model or start requests by itself.
Provider behavior follows [OpenAI model documentation](https://developers.openai.com/api/docs/models/gpt-6-luna)
and [DeepSeek thinking-mode documentation](https://api-docs.deepseek.com/guides/thinking_mode/).
