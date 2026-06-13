# Bangumi GrillMaster 简体中文版

当前版本：v0.3.0  
更新日期：2026-06-13

## 更新记录

- 2026-06-03：v0.1.0，创建本简体中文 Fork，基于原项目调整为面向简体中文字幕制作的个人化版本。
- 2026-06-12：v0.2.0，新增读取本地视频文件的处理流程；优化最终字幕输出格式。
- 2026-06-13：v0.3.0，新增 `--source-srt`，支持导入外部日文 SRT 作为源字幕继续翻译。

Bangumi GrillMaster 是一个面向日语综艺、番组和网络视频的自动字幕制作工具。它可以下载在线视频，自动抽取音频、进行语音识别、翻译成中文，并导出可播放的 SRT / ASS 字幕。

本仓库是在原项目基础上做的个人化改造版，主要面向 AKB48 相关综艺、MC、直播切片和字幕制作场景。项目仍保留了原作者针对日本综艺番组的润饰思路、固定译名转换和流程设计，因此也可以用于 AKB48 以外的节目，但并不作为首要推荐用途。如果有更广泛的日本综艺翻译需求，建议优先使用原作者项目。

## 免责声明

本项目仅建议用于个人学习、研究和字幕制作。使用者应自行遵守视频平台服务条款、版权规定以及所在地相关法律法规。使用 ElevenLabs、Gemini、DeepSeek、Codex CLI 等服务产生的 API 或订阅费用由使用者自行承担。请不要将 `.env`、`cookies.txt`、API Key、登录凭据或任何私人配置提交到公开仓库。

## 功能特点

- 支持 Bilibili、TVer、ABEMA、YouTube 等 yt-dlp 可处理的视频来源。
- v0.2.0 新增：支持读取本地视频文件，适合无法用 yt-dlp 下载的视频站点。
- v0.3.0 新增：支持导入外部日文 SRT 作为源字幕，跳过 ElevenLabs ASR。
- 默认使用 ElevenLabs 进行日语语音识别，生成源语言 SRT。
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
生成源日文字幕：
- 默认：ElevenLabs ASR
- 可选：--source-srt 导入外部日文 SRT
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

可以使用 `grill` 命令，也可以直接运行 `python main.py`。两种方式调用的是同一个入口，所有参数都可以互换；下面的示例统一使用 `grill`。

如果已经把 `scripts/` 加入 PATH，或已经通过 `pip install -e .` / `uv sync` 安装了项目，可以直接使用：

```bash
grill <视频来源> [翻译提示]
```

不使用 `grill` 时，也可以直接运行：

```bash
python main.py <视频来源> [翻译提示]
```

`视频来源` 可以是：

- Bilibili BV 号
- TVer / ABEMA / YouTube URL
- YouTube 的 `v=xxxx` 格式
- 本地视频文件路径，例如 `.\episode.mp4`

`翻译提示` 是可选参数。建议填写节目名、集数、出演者、系列名或你希望翻译时参考的背景信息。

如果已经用 OCR 工具从视频硬字幕提取出日文 SRT，可以用 `--source-srt` 导入：

```bash
grill ".\episode.mp4" "节目提示" --source-srt ".\ocr.ja.srt"
```

这种模式会跳过 ElevenLabs ASR，把外部 SRT 作为 `video.ja.srt` 继续翻译；视频和音频仍会正常处理，供 Gemini pre-pass 和分块翻译参考。

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

使用本地视频和外部日文 SRT：

```bash
grill ".\episode.mp4" "节目提示" --source-srt ".\ocr.ja.srt"
```

使用断点：

```bash
grill ".\episode.mp4" "节目提示" --break-after is_asr_completed
```

启用可选润色、词表校对和封面生成：

```bash
grill BV18KBJBeEmV "节目提示" --refine --glossary-check --cover
```

## 常用环境变量

在项目根目录创建 `.env`：

```env
# 复制本文件为 .env，然后填写你自己的密钥和路径。
# 不要提交 .env、cookies.txt、视频文件、音频文件或项目生成结果。

# ElevenLabs Speech to Text
ELEVENLABS_API_KEY=                 # ElevenLabs API 密钥，用于 ASR 语音识别
ELEVENLABS_STT_MODEL=scribe_v2      # ElevenLabs ASR 模型，建议保持 scribe_v2
ELEVENLABS_STT_LANGUAGE_CODE=jpn    # 语音识别语言提示，jpn 表示日语

# Google Gemini 翻译
GEMINI_API_KEY=                     # Gemini API 密钥，用于 pre-pass 和分块翻译
GEMINI_MODEL=gemini-3-flash-preview # Gemini 翻译模型

# DeepSeek 结构修正
DEEPSEEK_API_KEY=                   # DeepSeek API 密钥，用于修正 chunk 输出结构
LLM_CHUNK_FIX_MAX_RETRIES=3         # 结构修正失败重试次数

# 可选：Gemini 翻译调校
GEMINI_THINKING_LEVEL=HIGH                  # thinking level：LOW / MEDIUM / HIGH
GEMINI_PRE_PASS_FRAME_INTERVAL_SECONDS=120  # pre-pass 全片截图采样间隔，单位秒
GEMINI_PRE_PASS_FRAME_MAX_SIDE=768          # pre-pass 截图最长边尺寸
GEMINI_CHUNK_CHAR_LIMIT=6000                # 每个翻译 chunk 的目标字符数
GEMINI_CONCURRENCY=10                       # chunk 并发翻译上限
GEMINI_CHUNK_MAX_RETRIES=3                  # chunk 翻译失败重试次数
GEMINI_CHUNK_FRAME_INTERVAL_SECONDS=30      # chunk 局部截图采样间隔，单位秒
GEMINI_CHUNK_FRAME_MAX_SIDE=768             # chunk 截图最长边尺寸
GEMINI_CHUNK_MISSING_BLOCK_TOLERANCE=2      # 每块允许未对齐/缺漏字幕块数量上限
GEMINI_INTRO_SKIP_SECONDS=3.0               # 截图采样时跳过片头秒数
ENABLE_FULL_FIXED_GLOSSARY=false            # 是否把完整固定译名表带入 pre-pass（false=只带比对到的）

# 可选：Gemini CLI pre-pass（订阅制可节省 API 费用；需安装并登录 Gemini CLI）
ENABLE_GEMINI_CLI_PREPASS=false             # 是否改用 Gemini CLI 跑 pre-pass
GEMINI_CLI_EXECUTABLE=gemini                # Gemini CLI 可执行文件名或绝对路径
GEMINI_CLI_MODEL=gemini-3.1-pro-preview     # Gemini CLI pre-pass 使用模型
GEMINI_CLI_TIMEOUT_SECS=900                 # Gemini CLI 单次调用超时时间，单位秒
GEMINI_CLI_MAX_RETRIES=3                    # Gemini CLI schema 修复重试次数

# 可选：Codex 后处理（需安装 Codex CLI）
ENABLE_SRT_REFINE=false             # 翻译后是否用 Codex 润色简体中文字幕
ENABLE_GLOSSARY_CHECK=false         # 润色后是否用 Codex 校对固定译名残留
ENABLE_COVER_GENERATION=false       # 下载后是否并行生成/风格化封面图
CODEX_EXECUTABLE=codex              # Codex CLI 可执行文件名或绝对路径
CODEX_DEFAULT_TIMEOUT_SECS=900      # Codex 单次调用默认超时时间，单位秒

# 可选：下载、归档和封装
COOKIES_TXT_PATH=cookies.txt        # 视频网站 cookies，供 yt-dlp 下载登录内容
ARCHIVED_PATH=                      # 归档路径；留空则不自动归档
PACKAGE_PATH=                       # 打包路径；留空则不执行烧录/打包步骤
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

使用 `--source-srt` 时，`.asr/audio.opus` 仍会生成供 Gemini 参考，但 `.asr/asr.json` 不会生成。

## 本地视频说明

读取本地视频是本 Fork 在 v0.2.0（2026-06-12）新增的功能，用来处理无法通过 yt-dlp 下载的视频来源。

当传入本地文件路径时，程序会：

1. 根据文件路径创建稳定的 `local_...` 项目 ID。
2. 把本地视频复制到项目目录中的 `video.mp4`。
3. 跳过 yt-dlp 元数据和下载流程。
4. 继续执行抽音频、ASR、翻译、润色和最终导出。

本地视频路径建议配合翻译提示使用，因为本地文件没有站点标题、简介和演员信息可供自动读取。

## 外部 SRT 说明

`--source-srt` 是本 Fork 在 v0.3.0（2026-06-13）新增的功能，适合配合 OCR 工具从硬字幕视频中提取出的日文 SRT 使用。

当传入 `--source-srt` 时，程序会：

1. 正常导入或下载视频。
2. 正常抽取音频，供 Gemini 参考上下文。
3. 跳过 ElevenLabs ASR。
4. 校验并重新编号外部 SRT。
5. 把外部 SRT 写入项目的 `video.ja.srt`。
6. 继续执行 pre-pass、翻译、润色和最终导出。

这个功能不只限于本地视频，也可以配合在线视频使用；只要视频内容和外部 SRT 对得上即可。

## 固定词表

固定词表位于：

```text
services/fixed_glossary/
```

这里可以维护常见人物、组合、节目名和专有名词的译法。翻译和最终清理会尽量利用这些信息保持用词一致。

## 注意事项

- 默认 ASR 和翻译都会产生 API 费用，请先用短视频或 `--break-after` 测试流程；使用 `--source-srt` 时会跳过 ElevenLabs ASR。
- 根据是否启用 CLI、润色、词表校对、重试和模型配置，实际成本会略有差异。仅使用 ElevenLabs ASR `scribe_v2` 与 `gemini-3-flash-preview` 时，粗略成本约为 0.2 人民币元/分钟。
- 如果视频网站需要登录，请准备 `cookies.txt` 并在 `.env` 中设置 `COOKIES_TXT_PATH`。
- 如果中途失败，可以重新运行同一个视频来源，已完成阶段会跳过。
- 本地视频如果已经创建项目，后续也可以直接用对应的 `local_...` 项目 ID 续跑。
- 如果使用 `--source-srt`，外部 SRT 的时间轴质量会直接影响翻译分块和最终字幕效果。
- `PACKAGE_PATH` 留空时不会执行最后的烧录/打包步骤。

## Credits

Original Project:

https://github.com/elishahung/bangumi-grillmaster

感谢原作者提供优秀的项目基础
