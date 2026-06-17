# Chinese Conversion Exclusions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split Chinese conversion exclusions into directional character sets derived from repository subtitle fixtures.

**Architecture:** Keep the public conversion API unchanged. Replace the reversible exclusion mapping with two private sets selected by conversion direction, while preserving the existing character-position replacement behavior.

**Tech Stack:** Python 3.13, OpenCC, pytest, ruff, ty, uv.

---

## File Structure

- Modify `scinoephile/lang/zho/script/conversion.py`: define the two private directional exclusion sets with inline annotations, remove the old mapping, and update exclusion selection.
- Modify `test/lang/zho/script/test_conversion.py`: update focused conversion tests for directional exclusions and inactive artifact candidates.
- No new runtime modules are needed. The fixture discovery command is read-only and stays outside the package.

### Task 1: Confirm Fixture-Derived Candidates

**Files:**
- Read: `docs/STYLE.md`
- Read: `docs/superpowers/specs/2026-06-17-zho-conversion-exclusions-design.md`
- Read: `test/data/*/output/*/fuse_clean_validate.srt`
- Read: `test/data/*/input/*.srt`

- [ ] **Step 1: Re-read style and design requirements**

Run:

```powershell
Get-Content -Raw docs/STYLE.md
Get-Content -Raw docs/superpowers/specs/2026-06-17-zho-conversion-exclusions-design.md
```

Expected: confirm Python modules keep the copyright header, module docstring,
`from __future__ import annotations`, documented exports, and that fixture scope
includes OCR output SRTs plus original input SRTs.

- [ ] **Step 2: Run the read-only fixture discovery command**

Run:

```powershell
$env:UV_CACHE_DIR='/tmp/uv-cache'
$env:PYTHONIOENCODING='utf-8'
@'
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

from opencc import OpenCC

languages = {"yue-Hans", "yue-Hant", "zho-Hans", "zho-Hant"}
output_paths = [
    path
    for path in Path("test/data").glob("*/output/*/fuse_clean_validate.srt")
    if path.parent.name.split("_")[0] in languages
]
input_paths = [
    path for path in Path("test/data").glob("*/input/*.srt") if path.stem in languages
]
paths = sorted(output_paths + input_paths)
converters = {"Hans": OpenCC("t2s"), "Hant": OpenCC("s2t")}
pair_counters = {"Hans": Counter(), "Hant": Counter()}
examples = {}
length_changes = []


def language_of(path: Path) -> str:
    if path.parent.name == "input":
        return path.stem
    return path.parent.name.split("_")[0]


def script_of(path: Path) -> str:
    language = language_of(path)
    if language.endswith("Hans"):
        return "Hans"
    if language.endswith("Hant"):
        return "Hant"
    raise ValueError(language)


for path in paths:
    script = script_of(path)
    converter = converters[script]
    rel_path = path.as_posix()
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        converted = converter.convert(line)
        if line == converted:
            continue
        if len(line) == len(converted):
            for source, target in zip(line, converted, strict=True):
                if source == target:
                    continue
                pair_counters[script][(source, target)] += 1
                examples.setdefault(
                    (script, source, target), (rel_path, line_no, line, converted)
                )
        else:
            length_changes.append((rel_path, line_no, line, converted))
            matcher = SequenceMatcher(a=line, b=converted, autojunk=False)
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == "equal":
                    continue
                source = line[i1:i2]
                target = converted[j1:j2]
                pair_counters[script][(source, target)] += 1
                examples.setdefault(
                    (script, source, target), (rel_path, line_no, line, converted)
                )

print(f"paths={len(paths)} output={len(output_paths)} input={len(input_paths)}")
print(
    "paths_by_script=",
    {script: sum(1 for path in paths if script_of(path) == script) for script in ("Hans", "Hant")},
)
for script in ("Hant", "Hans"):
    print(f"\n[{script}]")
    for (source, target), count in pair_counters[script].most_common():
        rel_path, line_no, line, converted = examples[(script, source, target)]
        print(f"{source}\t{target}\t{count}\t{rel_path}:{line_no}\t{line}\t{converted}")
print(f"\nlength_changes={len(length_changes)}")
for rel_path, line_no, line, converted in length_changes:
    print(f"{rel_path}:{line_no}\t{line}\t{converted}")
'@ | uv run python -
```

Expected: `paths=28 output=19 input=9`, `paths_by_script= {'Hans': 13, 'Hant': 15}`,
and `length_changes=0`. The candidate list should include the same source characters
that are named in Tasks 3 and 4.

### Task 2: Update Directional Conversion Tests

**Files:**
- Modify: `test/lang/zho/script/test_conversion.py`

- [ ] **Step 1: Replace the exclusion parametrization**

Replace the existing parametrized cases in
`test_get_zho_text_converted_applies_exclusions_by_character_position` with:

```python
@pytest.mark.parametrize(
    ("text", "config", "expected"),
    [
        ("台臺", OpenCCConfig.s2t, "台臺"),
        ("台臺", OpenCCConfig.t2s, "台台"),
        ("你吃吓晒啦", OpenCCConfig.s2t, "你吃吓晒啦"),
        ("一群牛虱", OpenCCConfig.s2t, "一群牛虱"),
        ("这家伙", OpenCCConfig.s2t, "這傢伙"),
        ("呢個嗰度喎", OpenCCConfig.t2s, "呢个嗰度喎"),
        ("希望藉此答覆", OpenCCConfig.t2s, "希望藉此答覆"),
        ("丑大了", OpenCCConfig.s2t, "醜大了"),
        ("移形換影", OpenCCConfig.t2s, "移形换影"),
        ("黃大富", OpenCCConfig.t2s, "黄大富"),
    ],
)
```

Expected: the first seven cases assert active directional preservation. The last
three cases assert that commented-out artifact candidates are not active exclusions.

- [ ] **Step 2: Run the focused test and confirm it fails before implementation**

Run:

```powershell
$env:UV_CACHE_DIR='/tmp/uv-cache'
uv run pytest test/lang/zho/script/test_conversion.py::test_get_zho_text_converted_applies_exclusions_by_character_position -q
```

Expected: FAIL. The old mapping still preserves `臺` during `t2s`, does not preserve
new Cantonese `t2s` characters such as `喎`, and does not apply the new inactive
artifact distinction.

### Task 3: Split the Runtime Exclusion Data

**Files:**
- Modify: `scinoephile/lang/zho/script/conversion.py`

- [ ] **Step 1: Replace the old mapping with the `s2t` exclusion set**

Delete `_conversion_exclusions` and its docstring. Add this set in the same location:

```python
_S2T_EXCLUDED_CHARS = {
    "吃",  # Modern subtitles prefer 吃 over the literary traditional variant 喫.
    "吓",  # Cantonese particle/verb is distinct from 嚇 "frighten".
    "晒",  # Cantonese result particle uses 晒 rather than 曬 "sun-dry".
    "才",  # Common modern form is preferred over the older adverbial 纔.
    "托",  # 拜托 and Cantonese uses keep 托 rather than 託.
    "蒙",  # Cantonese/colloquial 蒙 is not the weather adjective 濛.
    "准",  # 准 remains valid in permission contexts such as 不准.
    "群",  # Modern subtitles use 群 instead of the older variant 羣.
    "郁",  # Cantonese 郁 "move" is not 鬱 "depressed/dense".
    "床",  # Modern subtitles prefer 床 over the older variant 牀.
    "台",  # 台 is kept for platform/stage/address forms instead of 臺.
    "痴",  # 白痴 commonly keeps 痴 rather than 癡.
    "升",  # 升仙 keeps the modern form rather than 昇.
    "仆",  # Cantonese 仆街 is not 僕 "servant".
    "秘",  # Modern subtitles prefer 秘 over the older variant 祕.
    "克",  # 克制 uses 克, not 剋.
    "借",  # 借助 is accepted in the fixture style instead of 藉助.
    "了",  # 了解 keeps 了 rather than 瞭.
    "里",  # 萬里 uses the distance character 里, not 裏 "inside".
    "咸",  # Cantonese food terms such as 咸煎餅 keep 咸.
    "虱",  # Modern/Hong Kong subtitles use 虱 instead of 蝨.
    "响",  # Cantonese locative/verb use is kept instead of 響.
    "峰",  # Modern subtitles prefer 峰 over the older variant 峯.
    "扑",  # Cantonese 扑 "hit" is kept rather than 撲.
    "伙",  # 伙記 and 家伙 keep 伙 rather than 夥.
    "干",  # 干 has valid traditional uses such as 干擾.
    "粽",  # Modern/Hong Kong subtitles use 粽 instead of 糉.
    "洒",  # 瀟洒 keeps the fixture's variant rather than 灑.
    "卺",  # 合卺 keeps 卺 rather than the rare variant 巹.
    "皂",  # 青紅皂白 uses 皂 rather than 皁.
    "娘",  # Profanity/kinship contexts use 娘 rather than 孃.
    "灶",  # Modern subtitles prefer 灶 over 竈.
    "唇",  # Modern subtitles prefer 唇 over 脣.
    "刮",  # Shaving/scraping uses 刮, not 颳 "wind blows".
    "幸",  # 薄幸 uses 幸, not 倖.
    "岩",  # 金剛岩 and Cantonese 岩 are not 巖 "cliff".
    "杰",  # Cantonese 杰 is not 傑 "outstanding".
    "厘",  # 無厘頭 keeps the Hong Kong form 厘.
    "注",  # 注定 uses 注, not 註 "annotation".
    "制",  # 制定 uses 制, not 製 "manufacture".
    "喂",  # Interjection 喂 is not 餵 "feed".
}
"""Characters to preserve when converting simplified Chinese toward traditional."""

# Likely fixture artifacts seen during s2t no-op discovery:
# "丑",  # test/data/tmm/output/zho-Hant_ocr/fuse_clean_validate.srt:35 uses 丑
#        # where standard traditional 醜 is expected for "ugly".
# "边",  # test/data/acopopb/output/yue-Hant_ocr/fuse_clean_validate.srt:5071
#        # contains simplified 边 in a Hant OCR output.
# "嘘",  # test/data/acoptc/output/yue-Hant_ocr/fuse_clean_validate.srt:3899
#        # contains simplified 嘘 where Hant 噓 is expected.
# "只",  # test/data/tmm/output/zho-Hant_ocr/fuse_clean_validate.srt:2376 uses
#        # 只 as a classifier where traditional 隻 is expected.
# "面",  # test/data/acopopb/output/yue-Hant_ocr/fuse_clean_validate.srt:679
#        # likely has simplified 面 for noodle 麵.
# "云",  # test/data/acopopb/output/yue-Hant_ocr/fuse_clean_validate.srt:1787
#        # appears in Cantonese "呢云", likely an OCR/review artifact.
# "羡",  # test/data/tmm/output/yue-Hant_ocr/fuse_clean_validate.srt:2611
#        # uses simplified 羡 where traditional 羨 is expected.
# "家",  # test/data/tmm/output/yue-Hant_ocr/fuse_clean_validate.srt:4695
#        # appears in 家伙, where the existing test expects 傢伙.
```

Expected: the old reverse mapping no longer exists, and the active `s2t` set contains
only characters that should be preserved when converting toward traditional.

- [ ] **Step 2: Add the `t2s` exclusion set below the `s2t` set**

Add:

```python
_T2S_EXCLUDED_CHARS = {
    "喎",  # Cantonese sentence particle should not be replaced by 㖞.
    "嗰",  # Cantonese demonstrative should not be replaced by 𠮶.
    "搵",  # Cantonese 搵 "look for" is preferred over OpenCC's 揾.
    "痾",  # Cantonese 痾 "defecate" is preferred over 疴.
    "藉",  # 藉此 is accepted in simplified text and should not collapse to 借.
    "劏",  # Cantonese 劏 "slaughter" is preferred over 㓥.
    "捱",  # 捱 in the fixtures is lexical, not a generic replacement with 挨.
    "噚",  # Cantonese 噚 should not be replaced by 㖊.
    "燶",  # Cantonese 燶 "burnt" should not be replaced by 㶶.
    "餸",  # Cantonese 餸 "dish" should not be replaced by 𩠌.
    "剎",  # 一剎那 keeps 剎 as an accepted variant.
    "覆",  # 答覆 keeps the lexical form distinct from 复.
    "唓",  # Cantonese interjection 唓 should not be replaced by 𪠳.
}
"""Characters to preserve when converting traditional Chinese toward simplified."""

# Likely fixture artifacts seen during t2s no-op discovery:
# "擺",  # test/data/acoptc/output/yue-Hans_ocr/fuse_clean_validate.srt:811
#        # contains traditional 擺 in a Hans OCR output.
# "換",  # test/data/acoptc/output/yue-Hans_ocr/fuse_clean_validate.srt:3003
#        # contains traditional 換 in a Hans OCR output.
# "決",  # test/data/acopopb/output/yue-Hans_ocr/fuse_clean_validate.srt:63
#        # contains traditional 決 in a Hans OCR output.
# "綁",  # test/data/acopopb/output/yue-Hans_ocr/fuse_clean_validate.srt:1639
#        # contains traditional 綁 in a Hans OCR output.
# "帶",  # test/data/acoptc/output/yue-Hans_ocr/fuse_clean_validate.srt:2675
#        # contains traditional 帶 in a Hans OCR output.
# "豬",  # test/data/acoptc/output/yue-Hans_ocr/fuse_clean_validate.srt:5603
#        # contains traditional 豬 in a Hans OCR output.
# "潚",  # test/data/acopopb/input/zho-Hans.srt:2067 is likely an OCR artifact
#        # for 瀟/潇 in 瀟洒.
# "涼",  # test/data/acopopb/output/yue-Hans_ocr/fuse_clean_validate.srt:775
#        # contains traditional 涼 in a Hans OCR output.
# "幫",  # test/data/acopopb/output/yue-Hans_ocr/fuse_clean_validate.srt:1043
#        # contains traditional 幫 in a Hans OCR output.
# "蹤",  # test/data/acopopb/output/yue-Hans_ocr/fuse_clean_validate.srt:2123
#        # contains traditional 蹤 in a Hans OCR output.
# "內",  # test/data/acopopb/output/yue-Hans_ocr/fuse_clean_validate.srt:3195
#        # contains traditional 內 in a Hans OCR output.
# "瀟",  # test/data/acopopb/output/zho-Hans_ocr/fuse_clean_validate.srt:2083
#        # contains traditional 瀟 in a Hans OCR output.
# "靚",  # test/data/acoptc/output/yue-Hans_ocr/fuse_clean_validate.srt:3
#        # contains traditional 靚 where simplified 靓 is expected.
# "鑼",  # test/data/acoptc/output/yue-Hans_ocr/fuse_clean_validate.srt:3983
#        # is likely OCR for 攞 rather than simplified 锣.
# "齋",  # test/data/acoptc/output/yue-Hans_ocr/fuse_clean_validate.srt:5243
#        # contains traditional 齋 in a Hans OCR output.
# "慘",  # test/data/tmm/output/zho-Hans_ocr/fuse_clean_validate.srt:339
#        # contains traditional 慘 in a Hans OCR output.
# "黃",  # test/data/tmm/output/zho-Hans_ocr/fuse_clean_validate.srt:1751
#        # contains traditional 黃 in a Hans OCR output.
# "噓",  # test/data/tmm/output/zho-Hans_ocr/fuse_clean_validate.srt:6107
#        # contains traditional 噓 in a Hans OCR output.
# "癲",  # test/data/tmm/output/zho-Hans_ocr/fuse_clean_validate.srt:6147
#        # contains traditional 癲 in a Hans OCR output.
```

Expected: the `t2s` set is independent from the `s2t` set and includes only characters
that should be preserved when converting toward simplified.

- [ ] **Step 3: Update `get_zho_text_converted` exclusion selection**

Replace:

```python
    excluded_chars: set[str] = set()
    if apply_exclusions:
        if config in SIMPLIFIED_CONFIGS:
            excluded_chars = set(_conversion_exclusions)
        if config in TRADITIONAL_CONFIGS:
            excluded_chars = set(_conversion_exclusions.values())
```

with:

```python
    excluded_chars: set[str] = set()
    if apply_exclusions:
        if config in SIMPLIFIED_CONFIGS:
            excluded_chars = _T2S_EXCLUDED_CHARS
        if config in TRADITIONAL_CONFIGS:
            excluded_chars = _S2T_EXCLUDED_CHARS
```

Expected: the function still applies exclusions by original character position only
when `len(converted_text) == len(text)`, but the chosen set is now directional.

- [ ] **Step 4: Run the focused exclusion test**

Run:

```powershell
$env:UV_CACHE_DIR='/tmp/uv-cache'
uv run pytest test/lang/zho/script/test_conversion.py::test_get_zho_text_converted_applies_exclusions_by_character_position -q
```

Expected: PASS.

### Task 4: Verify Conversion Tests and Formatting

**Files:**
- Modify: `scinoephile/lang/zho/script/conversion.py`
- Modify: `test/lang/zho/script/test_conversion.py`

- [ ] **Step 1: Check changed Python files against the style guide**

Inspect the changed files:

```powershell
git diff -- scinoephile/lang/zho/script/conversion.py test/lang/zho/script/test_conversion.py
```

Expected: the conversion module keeps its copyright header, module docstring,
`from __future__ import annotations`, and `__all__`. New comments are short,
specific, and placed next to the exclusion data they explain.

- [ ] **Step 2: Run format and lint on only changed Python files**

Run:

```powershell
$env:UV_CACHE_DIR='/tmp/uv-cache'
uv run ruff format scinoephile/lang/zho/script/conversion.py test/lang/zho/script/test_conversion.py
uv run ruff check --fix scinoephile/lang/zho/script/conversion.py test/lang/zho/script/test_conversion.py
uv run ty check scinoephile/lang/zho/script/conversion.py test/lang/zho/script/test_conversion.py
```

Expected: all three commands exit successfully. If `ruff` or `ty` reports a change
that would require restructuring beyond these two files, stop and ask the user.

- [ ] **Step 3: Run focused conversion tests**

Run:

```powershell
$env:UV_CACHE_DIR='/tmp/uv-cache'
uv run pytest test/lang/zho/script/test_conversion.py -q
```

Expected: all tests in `test/lang/zho/script/test_conversion.py` pass.

- [ ] **Step 4: Run the repository test command**

Run:

```powershell
Push-Location test
$env:UV_CACHE_DIR='/tmp/uv-cache'
uv run pytest -n auto
Pop-Location
```

Expected: the full test suite passes. If it fails, capture the failing test names and
the first relevant traceback before changing code.

- [ ] **Step 5: Commit implementation changes**

Run:

```powershell
git status --short
git add scinoephile/lang/zho/script/conversion.py test/lang/zho/script/test_conversion.py
git commit -m "Split Chinese conversion exclusions by direction"
```

Expected: the commit includes only the conversion module and focused conversion tests.

## Self-Review

Spec coverage:

- Data scope is covered by Task 1, including OCR outputs and original input SRTs.
- Directional runtime data is covered by Task 3.
- Artifact handling is covered by commented-out entries in Task 3.
- Public API preservation is covered by keeping `get_zho_text_converted` unchanged
  except for exclusion selection.
- Verification is covered by Task 4.

Placeholder scan: no deferred implementation markers are present.

Type consistency: both exclusion constants are `set[str]` literals, and
`excluded_chars` remains typed as `set[str]`.
