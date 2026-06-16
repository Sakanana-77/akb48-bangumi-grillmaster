# Bangumi GrillMaster 简体中文版

当前版本：v0.3.0  
更新日期：2026-06-13

Bangumi GrillMaster 简体中文版是一个面向 AKB48 相关视频的日语字幕翻译工具。它可以处理在线视频或本地视频，生成日文源字幕，再翻译成简体中文，并导出 SRT / ASS 字幕。

本仓库基于原项目做了个人化改造，重点面向 AKB48 综艺、MC、直播切片和字幕制作场景。项目仍保留原作者针对日本综艺番组的润饰思路、固定译名转换和流程设计，因此也可用于 AKB48 以外的节目，但不作为首要推荐用途。如果有更广泛的日本综艺翻译需求，建议优先使用原作者项目。

## 快速开始

安装依赖：

```bash
uv sync
```

复制配置文件并填写 API Key：

```bash
copy .env.example .env
```

至少需要填写：

```env
ELEVENLABS_API_KEY=
GEMINI_API_KEY=
```

如果你已经有日文 SRT，只想翻译字幕，可以不使用 ElevenLabs ASR，直接看下面的“外部日文 SRT”用法。

## 最常用命令

可以使用 `grill`，也可以使用 `python main.py`。两种方式调用的是同一个入口，所有参数都可以互换。下面统一用 `grill` 举例。

处理在线视频：

```bash
grill "https://www.bilibili.com/video/BV18KBJBeEmV" "节目名 / 出演者 / 其他翻译提示"
```

处理本地视频：

```bash
grill ".\episode.mp4" "节目名 / 出演者 / 其他翻译提示"
```

处理本地视频，并导入外部日文 SRT：

```bash
grill ".\episode.mp4" "节目提示" --source-srt ".\ocr.ja.srt"
```

直接运行 Python 入口也可以：

```bash
python main.py ".\episode.mp4" "节目提示" --source-srt ".\ocr.ja.srt"
```

`视频来源` 可以是 Bilibili BV 号、TVer / ABEMA / YouTube URL、YouTube 的 `v=xxxx` 格式，或本地视频文件路径。

`节目提示` 建议填写节目名、集数、出演者、企划内容等信息。提示越清楚，人物名和语境通常越容易翻对。

## 版本更新

- 2026-06-03：v0.1.0，创建本简体中文 Fork，基于原项目调整为面向简体中文字幕制作的个人化版本。
- 2026-06-12：v0.2.0，新增读取本地视频文件的处理流程；优化最终字幕输出格式。
- 2026-06-13：v0.3.0，新增 `--source-srt`，支持导入外部日文 SRT 作为源字幕继续翻译。

## 主要功能

- 支持 yt-dlp 可处理的视频来源，例如 Bilibili、TVer、ABEMA、YouTube。
- 支持本地视频文件，适合无法直接下载的视频站点。
- 支持导入外部日文 SRT，适合配合硬字幕 OCR 使用。
- 默认使用 ElevenLabs ASR 识别日语音频，生成源语言字幕。
- 使用 Gemini 进行视频分析、上下文整理和分块翻译。
- 可选使用 Codex CLI 进行字幕润色、固定译名校对和封面生成。
- 支持固定译名表，方便维护 AKB48 成员名、昵称、节目名和专有名词。
- 最终导出 ASS 字幕和清理后的 SRT 字幕。
- 支持断点续跑，中途失败后可以从已完成阶段继续。

## 常用功能

### 本地视频

本地视频是本 Fork 在 v0.2.0 新增的功能。适合处理无法用 yt-dlp 下载、但你已经保存到本地的视频。

```bash
grill ".\episode.mp4" "节目名 / 出演者 / 其他翻译提示"
```

程序会把本地视频复制到项目目录中的 `video.mp4`，然后继续抽取音频、生成字幕、翻译和导出。

### 外部日文 SRT

外部日文 SRT 是本 Fork 在 v0.3.0 新增的功能。适合你先用硬字幕 OCR 工具提取日文 SRT，再交给本项目翻译。

```bash
grill ".\episode.mp4" "节目提示" --source-srt ".\ocr.ja.srt"
```

使用 `--source-srt` 时会跳过 ElevenLabs ASR，把外部 SRT 作为 `video.ja.srt` 继续翻译。视频和音频仍会正常处理，供 Gemini 分析画面和上下文。

这个功能不只限于本地视频，也可以配合在线视频使用，只要视频内容和外部 SRT 对得上即可。

### 断点续跑

如果只想跑到某一步就停，可以使用断点：

```bash
grill ".\episode.mp4" "节目提示" --break-after is_asr_completed
```

```bash
grill ".\episode.mp4" "节目提示" --break-after is_srt_completed
```

重新运行同一个视频来源时，已经完成的阶段会自动跳过。

### 可选后处理

启用 Codex 润色、固定译名校对和封面生成：

```bash
grill BV18KBJBeEmV "节目提示" --refine --glossary-check --cover
```

也可以在 `.env` 中开启：

```env
ENABLE_SRT_REFINE=true
ENABLE_GLOSSARY_CHECK=true
ENABLE_COVER_GENERATION=true
```

这些功能需要本地安装并登录 Codex CLI，可能消耗 Codex CLI 额度。

## 配置说明

完整配置请看 `.env.example`。常用配置包括：

```env
ELEVENLABS_API_KEY=                 # ElevenLabs API 密钥，用于 ASR
GEMINI_API_KEY=                     # Gemini API 密钥，用于分析和翻译
DEEPSEEK_API_KEY=                   # 可选，用于修正 chunk 输出结构
COOKIES_TXT_PATH=cookies.txt        # 可选，供 yt-dlp 下载登录内容
ARCHIVED_PATH=                      # 可选，留空则不自动归档
PACKAGE_PATH=                       # 可选，留空则不执行烧录/打包步骤
```

默认情况下，`PACKAGE_PATH` 留空就不会执行最后的烧录/打包步骤，只会生成字幕文件。

## 输出文件

每个视频会生成一个独立项目目录：

```text
projects/{project_id}/
├── video.mp4
├── video.ja.srt
├── video.cht.finalized.srt
├── video.cht.ass
├── poster.jpg
└── project.json
```

最常用的成品是：

- `video.cht.ass`：带样式的最终 ASS 字幕。
- `video.cht.finalized.srt`：清理后的最终 SRT 字幕。
- `video.mp4`：项目内整理后的视频文件。

## 固定译名表

固定译名表位于：

```text
services/fixed_glossary/
```

这里可以维护 AKB48 成员名、昵称、组合名、节目名和专有名词的译法。后续如果有翻译错误，建议优先维护固定译名表，让之后的视频也能复用。

## 成本说明

默认 ASR 和翻译都会产生 API 费用，请先用短视频或断点测试流程。

根据是否启用 CLI、润色、词表校对、重试和模型配置，实际成本会略有差异。仅使用 ElevenLabs ASR `scribe_v2` 与 `gemini-3-flash-preview` 时，粗略成本约为 0.2 人民币元/分钟。

使用 `--source-srt` 时会跳过 ElevenLabs ASR，因此不会产生 ElevenLabs ASR 费用。

## 免责声明

本项目仅建议用于个人学习、研究和字幕制作。使用者应自行遵守视频平台服务条款、版权规定以及所在地相关法律法规。使用 ElevenLabs、Gemini、DeepSeek、Codex CLI 等服务产生的 API 或订阅费用由使用者自行承担。请不要将 `.env`、`cookies.txt`、API Key、登录凭据或任何私人配置提交到公开仓库。

## Credits

Original Project:

https://github.com/elishahung/bangumi-grillmaster

感谢原作者提供优秀的项目基础
