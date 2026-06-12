# Bangumi Grillmaster Simplified Chinese Edition

基于 elishahung/bangumi-grillmaster 修改的简体中文版本，针对 AKB48、坂道系及日系偶像综艺进行了专项优化。

## 项目特色

### 简体中文字幕输出

* 默认输出中国大陆简体中文字幕
* 去除繁体中文专用规则
* 优化大陆用户阅读习惯
* 支持繁体内容自动转换为简体

### 偶像综艺专项优化

* AKB48 固定译名表
* 坂道系成员译名优化
* 偶像综艺常用术语优化
* 成员昵称识别与统一
* 针对 SHOWROOM、综艺节目、直播切片优化翻译风格

### 智能翻译流程

结合音频、视频画面与上下文进行多模态翻译，而不仅仅依赖字幕文本。

* ElevenLabs Scribe v2 日语语音识别
* Gemini 多模态翻译
* DeepSeek 自动修复字幕结构错误
* 支持断点续跑（Resume）

---

## 与原版的主要区别

| 项目   | 原版     | 本 Fork             |
| ---- | ------ | ------------------ |
| 输出语言 | 繁体中文   | 简体中文               |
| 主要对象 | 日本综艺   | AKB48 / 坂道系 / 偶像综艺 |
| 译名规则 | 台湾习惯   | 中国大陆习惯             |
| 字幕风格 | 繁中综艺风格 | 简中字幕组风格            |
| 标点规则 | 原版规则   | 自定义大陆字幕规则          |

---

## 技术栈

### ASR（语音识别）

使用 ElevenLabs Scribe v2。

对于多人同时说话、吐槽与插话频繁的综艺节目识别效果优秀，能够较好区分不同发言内容。

### 翻译

经过测试，目前 Gemini Flash 系列对于日本综艺、偶像节目及直播内容的语气把握最自然。

为保证字幕结构稳定性，项目采用两阶段翻译流程：

1. Pre-pass 全片分析
2. Chunk 并发翻译
3. DeepSeek 自动修复结构错误
4. 最终组装输出

除了音频内容外，还会分析视频截图，辅助识别：

* 人物身份
* 场景变化
* 道具信息
* 画面文字

从而提升翻译准确率。

---

## Credits

Original Project:

https://github.com/elishahung/bangumi-grillmaster

感谢原作者提供优秀的项目基础。

-----------------------------------------------------------------

## 流程

```
Video ID
    ↓
下載影片 (yt-dlp)
    ↓
合併影片 (FFmpeg)
    ↓
提取音檔 (FFmpeg, mono 16kHz opus)
    ↓
語音辨識 (ElevenLabs Scribe v2)
    ↓
產生 SRT 字幕
    ↓
Pre-pass 分析 (Gemini: 全片簡報，定調人物/專名/語氣/分段摘要)
    ↓
併發 chunk 翻譯 (Gemini: 分塊平行翻譯 → 組裝驗證修正)
    ↓
潤飾字幕 (Codex, 可選)
    ↓
固定詞彙校對 (Codex)
    ↓
Finalize：格式清理，輸出 ASS (套樣式) + SRT
    ↓
歸檔 (可選)
    ↓
封裝交付 (可選：字幕燒錄進影片)
```

## 安裝

### 前置需求

- Python 3.13+
- FFmpeg (自行安裝並加入 PATH)
- uv (推薦) 或 pip

### 安裝步驟

```bash
# 使用 uv
uv sync

# 或使用 pip
pip install -e .
```

## 使用方式

### 方式一：加入 PATH

將 `scripts/` 資料夾加到系統 PATH，然後執行：

```bash
grill <SOURCE> [TRANSLATION_HINT]
```

### 方式二：直接執行

```bash
python main.py <SOURCE> [TRANSLATION_HINT]
```

- `SOURCE`: 影片 ID 或完整 URL
- `TRANSLATION_HINT`: 可選，提供給翻譯用的提示，通常是 bilibili 只有隱晦標題的需要

### 範例

```bash
# 使用影片標題作為翻譯提示
grill BV18KBJBeEmV

# 自訂翻譯提示
grill BV1CakEBaEJp "華大千鳥 - 全力100萬 - 間諜 1/7"

# 使用完整 URL
grill "https://www.bilibili.com/video/BV18KBJBeEmV"
```

## 環境變數

建立 `.env` 檔案：

```env
# ElevenLabs Speech to Text
ELEVENLABS_API_KEY=xxx
ELEVENLABS_STT_MODEL=scribe_v2
ELEVENLABS_STT_LANGUAGE_CODE=jpn

# Google Gemini (翻譯)
GEMINI_API_KEY=xxx
GEMINI_MODEL=gemini-3-flash-preview

# DeepSeek (chunk 結構修正)
DEEPSEEK_API_KEY=xxx
LLM_CHUNK_FIX_MAX_RETRIES=3            # 修正失敗重試次數

# 可選：Gemini 翻譯調校
GEMINI_THINKING_LEVEL=HIGH             # 翻譯 thinking level: LOW/MEDIUM/HIGH
GEMINI_PRE_PASS_FRAME_INTERVAL_SECONDS=120 # pre-pass 全片圖片抽樣頻率（每幾秒一張，另外固定包含影片首尾幀）
GEMINI_PRE_PASS_FRAME_MAX_SIDE=768     # pre-pass 圖片最長邊尺寸
GEMINI_CHUNK_CHAR_LIMIT=6000           # 每塊目標字元數 (約 5 分鐘字幕)
GEMINI_CONCURRENCY=10                  # chunk 併發上限
GEMINI_CHUNK_MAX_RETRIES=3             # chunk 失敗重試次數
GEMINI_CHUNK_FRAME_INTERVAL_SECONDS=30 # chunk 圖片抽樣頻率（每幾秒一張，另外固定包含每段首尾幀）
GEMINI_CHUNK_FRAME_MAX_SIDE=768        # chunk 圖片最長邊尺寸
GEMINI_CHUNK_MISSING_BLOCK_TOLERANCE=2 # 每塊允許未對齊/缺漏字幕區塊數上限
ENABLE_FULL_FIXED_GLOSSARY=false       # 固定譯名表整份帶入 pre-pass（false=只帶比對到的）

# 可選：Gemini CLI pre-pass（訂閱制省 API 費用；需安裝 Gemini CLI）
ENABLE_GEMINI_CLI_PREPASS=false         # 改用 Gemini CLI 跑 pre-pass

# 可選：Codex 後處理（需安裝 Codex CLI）
ENABLE_SRT_REFINE=true             # 翻譯後再用 Codex 潤飾繁中字幕
ENABLE_GLOSSARY_CHECK=true         # 潤飾後再用 Codex 校對殘留的英文/假名專名
ENABLE_COVER_GENERATION=true       # 下載後並行 Codex 風格化封面圖

# 可選：下載/歸檔/封裝
COOKIES_TXT_PATH=cookies.txt       # 影片來源網站 cookies (供 yt-dlp 使用)
ARCHIVED_PATH=NAS:\bangumi\ai\     # 歸檔路徑 - 處理完直接移至指定資料夾並將資料夾名稱改為影片名稱
PACKAGE_PATH=NAS:\bangumi\package\ # 封裝路徑 - 將 ASS 字幕燒錄進影片並複製封面到 <package_path>/<id>_<name>/
```

## 專案結構

```
projects/{video_id}/
├── project.json              # 專案狀態
├── video.mp4                 # 合併後的影片
├── video.ja.srt              # 日文原文字幕
├── .asr/                     # ASR 音檔與 ElevenLabs 原始結果
│   ├── audio.opus
│   └── asr.json
├── .pre_pass/                # Gemini pre-pass 簡報與圖片快取
│   └── pre_pass.json
├── .chunks/                  # chunk 音檔 / 圖片 / 翻譯回應快取（供 resume）
├── .refine/                  # Codex 潤飾報告（可選）
├── .glossary_check/          # Codex 固定詞彙校對報告（可選）
├── poster.jpg                # yt-dlp 取得的原始封面
├── poster.cover.png          # Codex 風格化封面（可選）
├── video.cht.srt             # 繁體中文翻譯字幕
├── video.cht.refined.srt     # Codex 潤飾後字幕（可選）
├── video.cht.glossary_checked.srt  # Codex 固定詞彙校對後字幕（可選）
├── video.cht.finalized.srt   # 最終 SRT（標點清理，給不支援 ASS 的裝置）
└── video.cht.ass             # 最終 ASS（套樣式 + 標點清理）
```
