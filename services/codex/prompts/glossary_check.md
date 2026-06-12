Glossary-check the refined subtitles for this video project.

Target language is highest priority: all subtitle text, report text, and Chinese term renderings must be Mainland China Simplified Chinese. Never convert output to Traditional Chinese. Treat `cht` in file names as a legacy path name only; it does not describe the target script.

Goal: a narrow, surgical pass. A short list of subtitle blocks still carry English letters or Japanese kana. For each one, decide whether that token is a correctly-kept proper noun or a missed fixed-glossary localization, and fix only the missed ones. This is a term swap, not a re-translation or a re-refine.

Files in the current working directory:

- `video.cht.refined.srt` — the refined Simplified Chinese subtitles; the baseline you copy from.
- `.glossary_check/fixed_glossary.json` — the authoritative curated jp→zh fixed glossary.
- `.glossary_check/fixed_glossary.md` — the fixed-glossary translation philosophy, for terms not present in the json. This file may contain legacy Taiwan Traditional Chinese wording; adapt its naming philosophy to Mainland China Simplified Chinese and never copy its Traditional characters into output.
- `.pre_pass/pre_pass.json` — summary, cast, proper_nouns, glossary, catchphrases, tone notes.

`video.ja.srt` is **not** a routine reference for this task. Consult it only if a flagged token is genuinely ambiguous and you need to recover what its Japanese source term was; otherwise do not read it.

Procedure:

- First copy `video.cht.refined.srt` to `video.cht.glossary_checked.srt` verbatim (a plain file copy, not a re-emit).
- Then edit only the flagged blocks in that copy, in place.
- Do not re-output, reformat, or re-wrap the whole file or any untouched content. Editing only the flagged spans keeps this cheap.

Write scope (strict): you may only create or modify `video.cht.glossary_checked.srt` and `.glossary_check/report.md`. Do **not** touch any other file, in particular:

- `project.json` — do not edit, do not flip progress flags, do not touch its contents in any way. The outer Python workflow owns this file and will mark progress after validating your output.
- `video.cht.refined.srt`, `video.ja.srt` — read-only sources.
- `.glossary_check/fixed_glossary.json`, `.glossary_check/fixed_glossary.md` — read-only inputs. Do not copy or delete them; the workflow manages their lifecycle.
- `.pre_pass/`, `.chunks/`, `.asr/`, `.refine/` — read-only caches.
- `video.mp4`, `audio.opus`, `poster.jpg`, etc. — unrelated to this step.

Do not run scripts that mutate `project.json` (e.g. don't run the project's own Python entrypoints, validators that write back, or any tool that re-saves state).

Rules:

- Do not change SRT indexes or timecodes. Do not merge or split blocks. Keep the block count identical to `video.cht.refined.srt`.
- Do not edit any block that is not in the flagged list. Leave it byte-identical to the copied file.
- Within a flagged block, change only the offending English/kana token. Do not retranslate, rephrase, re-punctuate, re-wrap, or otherwise touch the surrounding Chinese text. Every other character in the block must stay byte-identical to the copied file.
- Decide by context whether the flagged token actually corresponds to a glossary entry. Matching is by meaning in context, not exact source-string equality: the json aliases are Japanese source spellings while the flagged text is already Chinese, so a token only "matches" when the surrounding line is genuinely about that person/group/program/term.
- If it maps to a `fixed_glossary.json` entry, render only the span the flagged token actually covers, using that entry's script/romanization choice for that component, but convert any Traditional Chinese characters in the glossary target to Simplified Chinese before writing the subtitle. Do not expand a partial token to the entry's full target, and do not add components the token did not say (same-span rule, as upstream: source 「徳井」 → 德井, never 德井义实). E.g. flagged `Hollywood Zakoshisyoh` (the full ハリウッドザコシショウ) → `好莱坞杂鱼师匠`, but flagged `Zakoshisyoh` alone → `杂鱼师匠`, never `好莱坞杂鱼师匠`; flagged `Saraba` alone (only the さらば of さらば青春の光 → 再见吧青春之光) → only its own span `再见吧`, never the full `再见吧青春之光`. If there is no json entry, consult `fixed_glossary.md` for the right naming approach, then `pre_pass.json` `proper_nouns`/`characters`.
- An intentional proper noun, title, service name, or quoted term may legitimately stay non-Chinese. Do not force-localize a token that is already correct; leaving it unchanged is the right outcome for those.
- Preserve tone, address register, and honorific suffixes already present; this step never adjusts them.

After writing the SRT, if and only if you changed at least one block, also write a concise summary to `.glossary_check/report.md`. The report must be a Markdown table with these exact columns:

| 字幕编号 | 原译 | 修改后 | 修改原因 |
| --- | --- | --- | --- |

Pick at most 10 representative rows. If your edits exceed 10 rows, append a short paragraph after the table describing in general what other changes were made. Write the table headers and rows in Simplified Chinese. If you changed nothing, do not create the report.

Final state:

- `video.cht.glossary_checked.srt` exists in the current working directory. Block count, indexes, and timecodes match `video.cht.refined.srt` exactly. Every block's text is non-empty Simplified Chinese.
- Only the swapped English/kana spans differ from `video.cht.refined.srt`; all surrounding Chinese and every non-flagged block are byte-identical.
- `.glossary_check/report.md` exists only if at least one block changed.

Reply with just the single word `done`. Do not include explanations, summaries, edit lists, file paths, or any other commentary — the report file already covers the substantive changes, the calling workflow ignores your final message, and any extra tokens are wasted.
