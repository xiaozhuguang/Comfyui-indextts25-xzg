# ComfyUI IndexTTS 2.5 插件

基于官方 [index-tts/index-tts](https://github.com/index-tts/index-tts) 仓库集成的 **ComfyUI 自定义节点**，提供零样本音色克隆（Text-to-Speech）能力，支持中/英/日/西/阿拉伯语、情感控制、语速控制等。

> 本插件将官方 `indextts` 代码库直接内置（vendored），无需单独下载代码库即可在 ComfyUI 中使用。

---

## 节点一览

| 节点 | 说明 |
| :--- | :--- |
| **IndexTTS 2.5 模型加载器** | 发现并校验 `ComfyUI/models/TTS` 下的 IndexTTS-2.5 模型，配置推理设备与精度。 |
| **IndexTTS 2.5 语音生成** | 输入音色参考音频 + 文本，输出标准 ComfyUI AUDIO。 |
| **IndexTTS 2.5 情感控制** | 在「八维向量 / 情感参考音频 / 文本描述 / 跟随音色」四种情感控制方式间切换。 |
| **IndexTTS 2.5 采样设置** | 配置确定性/随机采样、长文本分段、停顿与文本归一化等参数。 |

---

## 多语言支持（i18n）

本插件界面遵循 ComfyUI 的国际化（i18n）规范，提供 **中 / 英文双模式**：

- 界面基准语言为英文，位于 `locales/en/nodeDefs.json`。
- 中文翻译位于 `locales/zh/nodeDefs.json`。
- 切换方式：在 ComfyUI 前端「Settings → Locale（语言）」中选择语言即可自动生效（无需重启），节点名称、输入/输出端口与 tooltip 会随之切换。

> 说明：
> - 运行时生成的结果信息（如生成时长、seed 等状态文本）属于节点输出数据，不在上述界面翻译范围内。
> - 情感控制节点中「情感模式」的动态下拉选项（`vector` / `reference_audio` / `text` / `speaker`）受 ComfyUI 前端机制限制**暂不随语言切换**（保持英文标识），但选项上方的模式名称与各参数的提示均已翻译。

---

## 环境要求

- ComfyUI（本插件基于 `comfy_api.latest` 节点 API，需较新版本）
- 至少 8GB 显存（推荐 12GB+，使用 bfloat16 可降低显存占用）
- 操作系统：Windows / Linux / macOS

---

## 一、安装依赖

使用 ComfyUI 自带的 Python 安装插件所需依赖（**不要**重装或降级 torch/torchaudio，使用 ComfyUI 自带版本即可）：

```bash
python -m pip install -r requirements.txt
```

常用依赖（`wetext`、`librosa`、`omegaconf`、`transformers`、`sentencepiece`、`fugashi` 等）多数已随 ComfyUI 附带；`requirements.txt` 已覆盖其余缺失项。

> 若需通过 ModelScope 下载模型，还需：`python -m pip install modelscope`

---

## 二、下载模型

IndexTTS-2.5 模型约 **5GB+**，需下载到 `ComfyUI/models/TTS/IndexTTS-2.5`。

### 方式 A：使用脚本（推荐）

```bash
# 从 ModelScope（国内更快）
python scripts/download_models.py --source modelscope --accept-license

# 从 HuggingFace
python scripts/download_models.py --source huggingface --accept-license
```

### 方式 B：手动放置

将官方 `IndexTeam/IndexTTS-2.5` 模型文件放入：

```
ComfyUI/models/TTS/IndexTTS-2.5/
├── config.yaml
├── gpt.pth
├── codec.pth
├── s2mel.pth
├── feat1.pt / feat2.pt / wav2vec2bert_stats.pt
├── multilingual_zh_ja_yue_char_del.tiktoken
└── qwen0.6bemo4-merge/  (文本情感模式所需，可选)
```

> 说明：`qwen0.6bemo4-merge/` 是情感控制「文本描述」模式所需的 Qwen 情感模型。只有当你需要该模式时，才需在模型加载器节点勾选「启用文本情感分析」并确保此文件夹存在；否则可忽略。

下载完成后**重启 ComfyUI**（或在模型加载器中刷新）以识别新模型。

---

## 三、详细使用说明（各节点参数含义）

以下逐节点说明每个输入/输出参数的含义。

### 节点 1：IndexTTS 2.5 模型加载器

**作用**：发现并校验模型目录，决定用哪块设备、以什么精度加载权重。模型权重在**第一次生成时**才真正载入内存（懒加载）。

| 参数 | 含义 | 可选值/默认值 |
| :--- | :--- | :--- |
| **IndexTTS 2.5 模型** `model_name` | 选择要使用的模型。自动扫描 `ComfyUI/models/TTS/` 下的 IndexTTS-2.5 目录。 | 默认自动检测到的模型 |
| **推理设备** `device` | 运行推理的硬件。`auto` 自动选 GPU。 | `auto` / `cuda:0`…`cuda:N` / `cpu` |
| **精度** `precision` | 权重精度。`auto` 在支持 bfloat16 的 GPU 上用 bf16（省显存），否则用 float32（更准）。 | `auto` / `bfloat16` / `float32` |
| **启用文本情感分析** `use_qwen_emo` | 加载 Qwen 情感模型（增加显存），以启用情感控制节点的「文本描述」模式。不使用该模式时可保持关闭以省显存。 | `false` / `true` |
| **BigVGAN CUDA 融合核** `use_cuda_kernel` | 是否启用 BigVGAN 声码器的自定义 CUDA 内核（速度更快）。首次使用会编译扩展，可能较慢。 | `false` / `true` |
| **生成后释放本模型** `release_after_run` | 每次生成后释放该模型的显存。适合显存紧张环境，但会降低连续生成速度。 | `false` / `true` |
| **完整 SHA-256 校验** `verify_hashes` | 加载前对全部模型文件做 SHA-256 哈希校验（约读取 5GB，较慢）。平时只做文件大小校验即可。 | `false` / `true` |
| **自定义模型绝对路径** `custom_model_path` | 手动指定模型目录绝对路径。留空则用上方模型列表。 | 默认空 |

**输出**：
- `model`：模型句柄（惰性），供语音生成节点使用。

---

### 节点 2：IndexTTS 2.5 语音生成

**作用**：核心节点，用音色参考音频 + 文本生成语音。

| 参数 | 含义 | 可选值/默认值 |
| :--- | :--- | :--- |
| **model** `model`（输入） | 来自模型加载器的模型句柄。 | 必填 |
| **音色参考音频** `speaker_audio` | 要克隆的声音样本。≥0.25 秒，自动截取前 15 秒，自动重采样到 22.05kHz 并转为单声道。 | 必填 |
| **待合成文本** `text` | 要朗读的文字。支持换行、动态提示词、以及 `<字|读音>` 发音标注。 | 必填 |
| **语言** `language` | 文本语言。 | `ZH` / `EN` / `JA` / `ES` / `AR` |
| **时长系数** `duration_factor` | 控制语速/时长。**越小越快**。 | 0.5（最快）~ 2.0（最慢），默认 1.0 |
| **seed** | 随机数种子。相同 seed + 相同输入 → 可复现结果。`control_after_generate` 支持「每次固定 / 递增 / 随机」。 | 0 ~ 2^64 |
| **情感控制** `emotion`（可选） | 来自情感控制节点的输出。不连接时跟随音色参考。 | 可选 |
| **采样设置** `sampling`（可选） | 来自采样设置节点的输出。不连接时用稳定默认值。 | 可选 |

**输出**：
- `audio`：标准的 ComfyUI `AUDIO`（`{waveform, sample_rate}`，22.05kHz 单声道），可接入预览/保存/其他音频节点。

---

### 节点 3：IndexTTS 2.5 情感控制

**作用**：以 4 种方式控制情感。官方模型内置 **8 种情感维度**：

| 维度 | 中文 | 含义 |
| :--- | :--- | :--- |
| `happy` | 高兴 | 愉悦、兴奋 |
| `angry` | 愤怒 | 生气、激动 |
| `sad` | 悲伤 | 难过、伤心 |
| `afraid` | 恐惧 | 害怕、紧张 |
| `disgusted` | 反感/厌恶 | 讨厌、嫌弃 |
| `melancholic` | 低落 | 忧郁、消沉 |
| `surprised` | 惊讶 | 意外、惊奇 |
| `calm` | 自然 | 平静、中性 |

**模式（mode）**：

**① 八维向量 `vector`** —— 手动设置 8 个维度的强度（0~1.2）。可用于表达任意组合情感。
- **注意：官方模型没有单独的「痛苦」维度**；要表达痛苦，可用「悲伤 + 恐惧」组合，或改用文本描述模式。
- `use_random`：开启后由 seed 决定每种情感采用的原型，关闭则匹配音色参考。

**② 情感参考音频 `reference_audio`** —— 用一段带情感的声音作参考。
- `emotion_audio`：情感参考音频。
- `情感强度 strength`：0~1。

**③ 文本描述 `text`** —— 用一句话描述情感，由 Qwen 情感模型自动转成 8 维向量。
- **需先在「模型加载器」节点勾选「启用文本情感分析」`use_qwen_emo`**（会额外加载 Qwen 情感模型，增加显存占用）。
- `emotion_text`：如「克制但难掩喜悦，语气温柔」。留空则分析待合成文本。
- `情感强度 strength`：0~1。

**④ 跟随音色 `speaker`** —— 不额外控制情感，跟随音色参考，最省显存。

**输出**：`emotion`（情感配置）。

---

### 节点 4：IndexTTS 2.5 采样设置

**作用**：控制生成过程的采样与分段参数。

| 参数 | 含义 | 可选值/默认值 |
| :--- | :--- | :--- |
| **启用随机采样** `do_sample` | 关闭时用确定性/束搜索（结果稳定、可复现）；开启后 `temperature/top_p/top_k` 生效（更多样）。 | `false` / `true` |
| `temperature` | 采样温度。越高越随机/多变，越低越保守。 | 0.1 ~ 2.0，默认 0.8 |
| `top_p` | 核采样。只保留累积概率前 top_p 的 token。 | 0.05 ~ 1.0，默认 0.8 |
| `top_k` | 只考虑概率最高的前 k 个 token。 | 0 ~ 200，默认 30 |
| `num_beams` | 束搜索宽度。越大越优但越慢。 | 1 ~ 10，默认 3 |
| `repetition_penalty` | 重复惩罚。越高越避免重复词。 | 0.1 ~ 20，默认 10 |
| `length_penalty` | 长度惩罚。>0 倾向于更长输出，<0 倾向更短。 | -2 ~ 2，默认 0 |
| **最大语音 token** `max_mel_tokens` | 生成音频的最大 mel token 数。长文本可增大。 | 256 ~ 4096，默认 1500 |
| **每段最大文本 token** `max_text_tokens_per_segment` | 长文本按标点切分时，每段的最大 token 数。 | 20 ~ 300，默认 120 |
| **段间静音（毫秒）** `segment_silence_ms` | 分句之间的停顿时长。 | 0 ~ 3000ms，默认 200 |
| **文本归一化** `text_normalization` | 是否把数字/符号/日期展开成可朗读文本（如 `25%` → `百分之二十五`）。 | `true` / `false` |

**输出**：`sampling`（采样配置）、`sampling_info`。

---

### 简易工作流

```
[IndexTTS 2.5 模型加载器] ──model──▶ [IndexTTS 2.5 语音生成] ──audio──▶ [预览/保存音频]
                                        ▲
                              speaker_audio（参考音频节点）+ text
```

> 参考音频可用「上传音频 / 加载音频」等 ComfyUI 音频输入节点提供，输出为标准的 `AUDIO`。

---

## 三-1、自定义发音

原项目支持文本内发音标注，本插件已开放：

### 1. 文本内发音标注（无需额外节点）

直接在待合成文本里用 `<字|读音>` 标注，可**精确控制某个字/词的读音**。按语言支持三种标注法：

**中文（拼音 + 声调数字 1~5）**
```
受不<了|liao3>你了
<苹果|píng guǒ>很好吃
长<行|xíng>和银行<行|háng>读法不同
```
- 拼音后跟声调：`1` 阴平、`2` 阳平、`3` 上声、`4` 去声、`5` 轻声。

**英文（CMU 音素）**
```
I <live|l-ay-v> in the city.        // 读作动词 live
<live|l-ih-v> music is great.       // 读作形容词 live
```

**日文（假名）**
```
<今日|きょう>は<天気|てんき>がいいです。
```

---

### 2. 原项目支持的全部「自定义」对照

| 原项目能力 | 在插件中的实现 | 是否需要额外节点 |
| :--- | :--- | :--- |
| G2P 发音标注 `<字\|读音>` | 直接写在待合成文本里 | 不需要 |
| 八维情感向量 | 情感控制节点 `vector` 模式 | 需要 |
| 情感文本 → 向量 | 情感控制节点 `text` 模式（Qwen） | 需要 |
| 情感参考音频 | 情感控制节点 `reference_audio` 模式 | 需要 |
| 随机情感种子 | 情感控制节点 `use_random` + 生成节点 `seed` | 需要 |
| 语速控制 | 生成节点 `duration_factor` | 不需要 |

---

## 四、注意事项与常见问题

### 运行提示
- **Python 版本**：官方代码面向 Python 3.10~3.11；在 3.12 下需对本插件内置代码做少量兼容补丁，本插件已内置这些补丁（针对新版 `transformers` 的 API 变更做了兼容处理）。
- **首次生成较慢**：模型首次加载需读入约 5GB 权重，之后会缓存在内存中加速。
- **显存不足**：可开启「生成后释放本模型」，或用 `bfloat16` 精度（省约一半显存）。
- **许可证**：使用模型前请阅读仓库内 `LICENSE`、`LICENSE_ZH.txt` 与 `DISCLAIMER`。

### 常见问题排查

| 现象 | 原因与解决办法 |
| :--- | :--- |
| 模型加载器显示「[未找到]」 | 模型未放在 `models/TTS/IndexTTS-2.5`，或刚放入未刷新。确认路径后**重启 ComfyUI**。 |
| 生成后没有声音 / 输出为空 | 文本为空、参考音频过短（<0.25 秒），或 `max_mel_tokens` 太小。增大 `max_mel_tokens`、缩短文本、换更长的参考音频。 |
| 显存不足 OOM | 用 `bfloat16`、开启「生成后释放本模型」，或改到 CPU（很慢）。 |
| 中文数字/符号读错 | 确认「文本归一化」开启（默认开启），它会自动展开 `25%`→`百分之二十五`、日期、单位等。 |
| 某字读音不对 | 用文本发音标注 `<字\|拼音>` 精确指定。 |
| 情感无效果 | 确认情感控制节点已连接；`strength` 过小会削弱效果，向量模式可加到 1.0~1.2。 |
| 结果不可复现 | 确认 `do_sample` 关闭（确定性束搜索）且 seed 固定。 |

---

## 相关链接

- 官方仓库：[index-tts/index-tts](https://github.com/index-tts/index-tts)
- 模型：HuggingFace `IndexTeam/IndexTTS-2.5` / ModelScope `IndexTeam/IndexTTS-2.5`
