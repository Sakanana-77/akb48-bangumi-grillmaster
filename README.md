# Bangumi GrillMaster 简体中文版

当前版本：v0.2.0  
更新日期：2026-06-12

## 更新记录

- 2026-06-03：v0.1.0，创建本简体中文 Fork，基于原项目调整为面向简体中文字幕制作的个人化版本。
- 2026-06-12：v0.2.0，新增读取本地视频文件的处理流程；优化最终字幕输出格式。

Bangumi GrillMaster 是一个面向日语综艺、番组和网络视频的自动字幕制作工具。它可以下载在线视频，自动抽取音频、进行语音识别、翻译成中文，并导出可播放的 SRT / ASS 字幕。

本仓库是在原项目基础上做的个人化改造版，重点优化了日语节目、偶像综艺、AKB48 相关内容、固定译名、中文排版和最终字幕格式。

## 功能特点

- 支持 Bilibili、TVer、ABEMA、YouTube 等 yt-dlp 可处理的视频来源。
- 本 Fork 新增：支持读取本地视频文件，适合无法用 yt-dlp 下载的视频站点。
- 使用 ElevenLabs 进行日语语音识别，生成源语言 SRT。
- 使用 Gemini 进行 pre-pass 分析和分块翻译。
- 可选使用 Codex 进行字幕润色、固定词表校对和封面生成。
- 支持固定译名、人物名、节目名、常用梗和专有名词的统一处理。
- 最终导出 ASS 字幕和清理后的 SRT 字幕。
- 支持断点续跑，失败后可以从已完成阶段继续。

## 字幕输出格式优化

v0.2.0 对最终字幕输出做了进一步清理，优化了长句换行、对话横线、单句前缀横线，以及英文词组前后多余空格等问题，让导出的 SRT / ASS 更适合直接观看。

## 工作流程

```text
视频 URL / 视频 ID / 本地视频文件
    ↓
下载视频或复制本地视频
    ↓
整理为项目内 video.mp4
    ↓
使用 FFmpeg 抽取音频
    ↓
ElevenLabs ASR 生成日语字幕
    ↓
Gemini pre-pass 分析人物、语境、译名和分段摘要
    ↓
Gemini 分块翻译字幕
    ↓
可选：Codex 润色字幕
    ↓
可选：Codex 固定词表校对
    ↓
最终清理并导出 ASS / SRT
    ↓
可选：归档和打包成品
```

## 环境要求

- Python 3.13+
- FFmpeg，并确保 `ffmpeg` / `ffprobe` 已加入 PATH
- ElevenLabs API Key
- Gemini API Key
- 可选：Codex CLI / Gemini CLI，用于额外润色或 pre-pass
- 可选：cookies.txt，用于需要登录状态的视频站点

## 安装

推荐使用 uv：

```bash
uv sync
```

如果不使用 uv，也可以安装到当前 Python 环境：

```bash
pip install -e .
```

## 使用方式

如果已经把 `scripts/` 加入 PATH，可以直接使用：

```bash
grill <视频来源> [翻译提示]
```

也可以直接运行：

```bash
python main.py <视频来源> [翻译提示]
```

`视频来源` 可以是：

- Bilibili BV 号
- TVer / ABEMA / YouTube URL
- YouTube 的 `v=xxxx` 格式
- 本地视频文件路径，例如 `.\episode.mp4`

`翻译提示` 是可选参数。建议填写节目名、集数、出演者、系列名或你希望翻译时参考的背景信息。

## 使用示例

使用视频 ID：

```bash
grill BV18KBJBeEmV
```

使用完整 URL：

```bash
grill "https://www.bilibili.com/video/BV18KBJBeEmV"
```

使用 YouTube：

```bash
grill "https://youtu.be/dQw4w9WgXcQ"
```

使用本地视频文件：

```bash
grill ".\episode.mp4" "节目名 / 集数 / 出演者 / 其他翻译提示"
```

使用断点：

```bash
python main.py ".\episode.mp4" "节目提示" --break-after is_asr_completed
```

启用可选润色、词表校对和封面生成：

```bash
python main.py BV18KBJBeEmV "节目提示" --refine --glossary-check --cover
```

## 常用环境变量

在项目根目录创建 `.env`：

```env
# ElevenLabs 语音识别
ELEVENLABS_API_KEY=xxx
ELEVENLABS_STT_MODEL=scribe_v2
ELEVENLABS_STT_LANGUAGE_CODE=jpn

# Gemini 翻译
GEMINI_API_KEY=xxx
GEMINI_MODEL=gemini-3-flash-preview
GEMINI_THINKING_LEVEL=HIGH

# 分块翻译
GEMINI_CHUNK_CHAR_LIMIT=6000
GEMINI_CONCURRENCY=10
GEMINI_CHUNK_MAX_RETRIES=3
GEMINI_CHUNK_MISSING_BLOCK_TOLERANCE=2

# pre-pass 和分块时的视频截图采样
GEMINI_PRE_PASS_FRAME_INTERVAL_SECONDS=120
GEMINI_PRE_PASS_FRAME_MAX_SIDE=768
GEMINI_CHUNK_FRAME_INTERVAL_SECONDS=30
GEMINI_CHUNK_FRAME_MAX_SIDE=768

# 可选功能
ENABLE_SRT_REFINE=false
ENABLE_GLOSSARY_CHECK=false
ENABLE_COVER_GENERATION=false
ENABLE_GEMINI_CLI_PREPASS=false
ENABLE_FULL_FIXED_GLOSSARY=false

# yt-dlp cookies
COOKIES_TXT_PATH=cookies.txt

# 可选归档和打包路径
ARCHIVED_PATH=
PACKAGE_PATH=
```

实际可用配置以 [settings.py](settings.py) 为准。

## 项目输出结构

每个视频会生成一个独立项目目录：

```text
projects/{project_id}/
├── project.json
├── video.mp4
├── video.ja.srt
├── video.cht.srt
├── video.cht.refined.srt
├── video.cht.glossary_checked.srt
├── video.cht.finalized.srt
├── video.cht.ass
├── poster.jpg
├── poster.cover.png
├── .asr/
│   ├── audio.opus
│   └── asr.json
├── .pre_pass/
│   └── pre_pass.json
├── .chunks/
├── .refine/
└── .glossary_check/
```

其中最常用的成品是：

- `video.cht.ass`：带样式的最终 ASS 字幕。
- `video.cht.finalized.srt`：清理后的最终 SRT 字幕。
- `video.mp4`：项目内整理后的视频文件。

## 本地视频说明

读取本地视频是本 Fork 在 v0.2.0（2026-06-12）新增的功能，用来处理无法通过 yt-dlp 下载的视频来源。

当传入本地文件路径时，程序会：

1. 根据文件路径创建稳定的 `local_...` 项目 ID。
2. 把本地视频复制到项目目录中的 `video.mp4`。
3. 跳过 yt-dlp 元数据和下载流程。
4. 继续执行抽音频、ASR、翻译、润色和最终导出。

本地视频路径建议配合翻译提示使用，因为本地文件没有站点标题、简介和演员信息可供自动读取。

## 固定词表

固定词表位于：

```text
services/fixed_glossary/
```

这里可以维护常见人物、组合、节目名和专有名词的译法。翻译和最终清理会尽量利用这些信息保持用词一致。

## 注意事项

- 语音识别和翻译都会产生 API 费用，请先用短视频或 `--break-after` 测试流程。
- 如果视频网站需要登录，请准备 `cookies.txt` 并在 `.env` 中设置 `COOKIES_TXT_PATH`。
- 如果中途失败，可以重新运行同一个视频来源，已完成阶段会跳过。
- 本地视频如果已经创建项目，后续也可以直接用对应的 `local_...` 项目 ID 续跑。

## Credits

Original Project:

https://github.com/elishahung/bangumi-grillmaster

感谢原作者提供优秀的项目基础
