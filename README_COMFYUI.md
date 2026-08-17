<div align="center">
  <img src="assets/index2.5_video_cover.png" width="600" alt="IndexTTS 2.5 Banner">
  <h1>🎙️ ComfyUI IndexTTS 2.5 插件</h1>
  <p>
    <a href="https://github.com/xiaozhuguang/Comfyui-indextts25-xzg/releases">
      <img src="https://img.shields.io/github/v/release/xiaozhuguang/Comfyui-indextts25-xzg?label=Release&logo=github">
    </a>
    <a href="https://github.com/xiaozhuguang/Comfyui-indextts25-xzg/actions">
      <img src="https://img.shields.io/github/actions/workflow/status/xiaozhuguang/Comfyui-indextts25-xzg/.github%2Fworkflows%2Frelease.yml?label=Publish&logo=githubactions">
    </a>
    <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-blue?logo=linux">
    <img src="https://img.shields.io/badge/VRAM-8GB%2B-yellow?logo=nvidia">
  </p>
  <p><b>零样本音色克隆 · 五国语言 · 情感控制 · 语速可调</b></p>
</div>

---

## 📌 项目简介

基于官方 [Bilibili IndexTTS Team / index-tts](https://github.com/index-tts/index-tts) 代码库集成的 **ComfyUI 自定义节点**，将 IndexTTS-2.5 零样本 TTS 能力无缝接入 ComfyUI 工作流。

> 本插件将官方 `indextts` 代码库直接内置（vendored），**无需单独安装 IndexTTS 项目**，在 ComfyUI 中开箱即用。

### ✨ 主要特性

| 特性 | 说明 |
| :--- | :--- |
| 🎯 **零样本克隆** | 只需 ≥0.25 秒的参考音频即可克隆任意音色 |
| 🌏 **五国语言** | 中文（ZH）、英文（EN）、日文（JA）、西班牙文（ES）、阿拉伯文（AR） |
| 🎭 **四种情感模式** | 八维向量 / 情感参考音频 / 文本描述 / 跟随音色 |
| ⚡ **采样自由配置** | 确定性束搜索 / 随机采样 / 长文本分段 / 停顿控制 |
| 🏷️ **双语界面** | 节点名、参数、Tooltip 完全中/英双语，随 ComfyUI 语言切换 |
| 🔤 **自定义发音** | 文本内支持 `<字\|读音>` 发音标注（拼音/音素/假名） |
| 📋 **动态提示词** | 待合成文本支持 ComfyUI 动态提示词语法 |

---

## 🖥️ 节点一览

```
┌─────────────────────────┐    ┌────────────────────────────┐
│  IndexTTS 2.5 模型加载器 │───▶│   IndexTTS 2.5 语音生成    │───▶  AUDIO 输出
└─────────────────────────┘    └────────────────────────────┘
                                      ▲   ▲   ▲
                                      │   │   │
                   [参考音频节点] ────┘   │   └──── [采样设置] 节点（可选）
                                          │
                            [情感控制] 节点 ───────────┘ （可选）
```

| 节点名 | 中/英 | 作用 |
| :--- | :--- | :--- |
| **XZG_IndexTTS25_ModelLoader** | IndexTTS 2.5 模型加载器 | 发现并校验模型，配置设备与精度 |
| **XZG_IndexTTS25_Generate** | IndexTTS 2.5 语音生成 | 音色参考音频 + 文本 → 合成音频 |
| **XZG_IndexTTS25_EmotionControl** | IndexTTS 2.5 情感控制 | 4 种方式控制输出情感 |
| **XZG_IndexTTS25_SamplingConfig** | IndexTTS 2.5 采样设置 | 采样/束搜索/分段/停顿参数集中配置 |

---

## ⚙️ 环境要求

| 项目 | 要求 |
| :--- | :--- |
| **ComfyUI 版本** | 较新版本（支持 `comfy_api.latest` 节点 API） |
| **显存** | 最低 **8GB**（推荐 **12GB+**，使用 bfloat16 可省约一半） |
| **系统** | Windows 10/11 · Linux · macOS |
| **Python** | 3.10 ~ 3.11（3.12 已内置补丁兼容） |
| **PyTorch** | 使用 ComfyUI 自带版本即可，**无需单独重装** |

---

## 📦 安装方法

### 方式一：ComfyUI Manager 安装（推荐，最简单）

1. 打开 ComfyUI → 点击右侧 **Manager**
2. 选择 **Install via Git URL**（或者 **Search and Install** 搜索 `indextts25`）
3. 填入本仓库地址：
   ```
   https://github.com/xiaozhuguang/Comfyui-indextts25-xzg
   ```
4. 安装完成后，**重启 ComfyUI**

### 方式二：手动 Clone（开发者）

进入 ComfyUI 的 `custom_nodes` 目录，克隆仓库：

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/xiaozhuguang/Comfyui-indextts25-xzg.git
cd Comfyui-indextts25-xzg
```

### 方式三：离线安装（下载 Release 压缩包）

1. 打开 [Releases 页面](https://github.com/xiaozhuguang/Comfyui-indextts25-xzg/releases) 下载最新版本的 `Source code (zip)`
2. 解压到 `ComfyUI/custom_nodes/Comfyui-indextts25-xzg/`
3. 重启 ComfyUI

---

### 🧪 安装 Python 依赖

上述任意方式安装完成后，使用 ComfyUI 自带的 Python 安装依赖：

```bash
# Windows（ComfyUI 自带 Python）
python_embeded/python.exe -m pip install -r ComfyUI/custom_nodes/Comfyui-indextts25-xzg/requirements.txt

# Linux / macOS / 手动环境
python -m pip install -r custom_nodes/Comfyui-indextts25-xzg/requirements.txt
```

> **注意**：不要单独重装或降级 `torch` / `torchaudio`，保持 ComfyUI 自带版本即可，避免环境冲突。
>
> 主要依赖：`librosa`、`omegaconf`、`transformers`、`sentencepiece`、`fugashi`、`unidic-lite`、`cn2an`、`wetext`、`jieba` 等。

---

## 📥 模型下载（约 5GB+）

IndexTTS-2.5 模型需要下载到 `ComfyUI/models/TTS/IndexTTS-2.5/` 目录下。共提供 **4 种下载渠道**，任选其一即可：

---

### 🔵 方式 A：夸克网盘（国内推荐，速度最快）

> 提取码如过期，请在 [Issues](https://github.com/xiaozhuguang/Comfyui-indextts25-xzg/issues) 反馈。

**下载地址**：<https://pan.quark.cn/s/f933f6037874>

下载后手动解压到以下目录结构：

```
ComfyUI/
└── models/
    └── TTS/
        └── IndexTTS-2.5/
            ├── config.yaml
            ├── gpt.pth                 (~3.3GB，主模型)
            ├── codec.pth               (~607MB，声码器)
            ├── s2mel.pth               (~415MB，声学模型)
            ├── feat1.pt
            ├── feat2.pt
            ├── wav2vec2bert_stats.pt
            ├── multilingual_zh_ja_yue_char_del.tiktoken
            └── qwen0.6bemo4-merge/     (可选，文本情感模式)
                ├── model.safetensors
                ├── config.json
                ├── tokenizer.json
                ├── vocab.json
                ├── merges.txt
                └── ...
```

---

### 🟢 方式 B：运行自动下载脚本（ModelScope / HuggingFace）

使用 ComfyUI 的 Python 执行：

```bash
# 进入插件目录
cd ComfyUI/custom_nodes/Comfyui-indextts25-xzg

# 方式 B-1：从 ModelScope 下载（国内速度推荐）
python scripts/download_models.py --source modelscope --accept-license

# 方式 B-2：从 HuggingFace 下载
python scripts/download_models.py --source huggingface --accept-license
```

> 脚本会自动把模型下载到 `ComfyUI/models/TTS/IndexTTS-2.5/`，并内置 SHA-256 校验。

---

### 🟠 方式 C：HuggingFace 手动下载

- 仓库地址：<https://huggingface.co/IndexTeam/IndexTTS-2.5>
- 下载所有文件到 `ComfyUI/models/TTS/IndexTTS-2.5/`

### 🟡 方式 D：ModelScope 手动下载

- 仓库地址：<https://www.modelscope.cn/models/IndexTeam/IndexTTS-2.5>
- 适合国内无 HuggingFace 访问条件的用户

---

> 📝 **关于 `qwen0.6bemo4-merge` 子目录**：
> - 这是**文本情感模式**专用的 Qwen 情感模型
> - **不使用文本情感模式可以跳过**该文件夹下载，节省约 1.2GB 空间
> - 如要用该模式：在模型加载器节点勾选「启用文本情感分析」（`use_qwen_emo`）

下载完成后**重启 ComfyUI**，在 **IndexTTS 2.5 模型加载器**节点的下拉列表中即可看到已识别的模型。

---

## 📖 节点参数详解

### 🔧 1. 模型加载器（Model Loader）

发现并校验模型，配置推理环境。权重采用**懒加载**（首次生成时才读入显存）。

| 参数 | 中文名 | 含义 & 可选值 | 默认 |
| :--- | :--- | :--- | :--- |
| `model_name` | IndexTTS 2.5 模型 | `ComfyUI/models/TTS/` 下检测到的模型名 | 自动检测 |
| `device` | 设备 | `auto`（推荐）/ `cuda:0`~`cuda:N` / `cpu` | `auto` |
| `precision` | 精度 | `auto`（CUDA 有 bf16 支持时自动用 bf16 省显存）/ `bfloat16` / `float32` | `auto` |
| `use_qwen_emo` | 启用文本情感分析 | 加载 Qwen 情感模型（+显存），启用后情感节点的「文本描述」模式才能用 | `false` |
| `use_cuda_kernel` | BigVGAN CUDA 融合核 | 首次会编译扩展；速度更快但可能失败 | `false` |
| `release_after_run` | 生成后释放模型 | 适合低显存环境；连续生成时会变慢 | `false` |
| `verify_hashes` | 完整 SHA-256 校验 | 加载前对约 5GB 模型做逐文件哈希校验（较慢） | `false` |
| `custom_model_path` | 自定义模型绝对路径 | 留空则用上方列表；填绝对路径则跳过自动搜索 | 空 |

**输出**：`model`（模型句柄，连接到语音生成节点）

---

### 🎤 2. 语音生成（Speech Generation）

核心合成节点。输入「模型 + 音色参考音频 + 文本」输出标准 ComfyUI AUDIO。

| 参数 | 中文名 | 含义 & 可选值 | 默认 |
| :--- | :--- | :--- | :--- |
| `model` | 模型 | 来自模型加载器的 MODEL 句柄 | *必填* |
| `speaker_audio` | 音色参考音频 | ≥0.25 秒，自动截取前 15 秒；采样率自动重采样为 22050Hz 单声道 | *必填* |
| `text` | 待合成文本 | 支持换行、动态提示词、以及 `<字\|读音>` 发音标注 | *必填* |
| `language` | 语言 | `ZH`(中文) / `EN`(英文) / `JA`(日文) / `ES`(西语) / `AR`(阿语) | `ZH` |
| `duration_factor` | 时长系数 | 控制语速：**越小越快，越大越慢** | `1.0`（0.5~2.0） |
| `seed` | 随机种子 | 相同 seed + 相同输入 → 完全可复现 | `0`（自动随机） |
| `emotion` | 情感控制 | 来自情感控制节点（可选，不接则跟随音色） | — |
| `sampling` | 采样设置 | 来自采样设置节点（可选，不接用默认值） | — |

**输出**：`audio`（标准 ComfyUI `AUDIO`，22050Hz 单声道，可接预览/保存节点）

---

### 🎭 3. 情感控制（Emotion Control）

四种模式控制输出情感。官方模型内置 **8 个情感维度**：

| 维度 | Happy | Angry | Sad | Afraid | Disgusted | Melancholic | Surprised | Calm |
| :--- | :---: | :---: | :-: | :----: | :-------: | :---------: | :-------: | :--: |
| **中文** | 高兴 | 愤怒 | 悲伤 | 恐惧 | 厌恶 | 低落 | 惊讶 | 平静 |

#### 模式一：八维向量（`vector`）🎛️
- 分别滑动 8 个维度（0~1.2）任意组合
- `strength`：情感整体强度 0~1
- `use_random`：开 → seed 决定每种情感原型；关 → 匹配音色参考

#### 模式二：情感参考音频（`reference_audio`）🔊
- 提供一段带目标情感的音频作为「情感模板」
- `emotion_audio`：情感参考音频
- `strength`：整体强度 0~1

#### 模式三：文本描述（`text`）📝
- **需先在模型加载器勾选「启用文本情感分析」**（加载 Qwen 情感模型）
- `emotion_text`：一句话描述，例如：
  > 「强忍着泪水却又带着一丝微笑的温柔语气」  
  > 「语带愤怒，音量偏高但在克制」  
  > 留空则分析待合成文本本身
- `strength`：整体强度 0~1

#### 模式四：跟随音色（`speaker`）🎯
- 不额外控制情感，完全跟随音色参考音频
- 最省显存/最快

**输出**：`emotion`（情感配置，连到语音生成节点）

---

### ⚙️ 4. 采样设置（Sampling Config）

集中控制生成过程的采样与分段策略。

| 参数 | 中文名 | 含义 | 默认 |
| :--- | :--- | :--- | :--- |
| `do_sample` | 启用随机采样 | 关 → 确定性/束搜索（稳定可复现）；开 → `temperature/top_p/top_k` 生效 | `false` |
| `temperature` | — | 采样温度：越高越随机/多变，越低越保守 | `0.8` |
| `top_p` | — | 核采样累积概率阈值 | `0.8` |
| `top_k` | — | 只考虑概率最高的前 k 个 token | `30` |
| `num_beams` | — | 束搜索宽度（越大越优但越慢） | `3` |
| `repetition_penalty` | — | 重复惩罚，越高越不重复 | `10.0` |
| `length_penalty` | — | 长度惩罚：>0 偏长，<0 偏短 | `0.0` |
| `max_mel_tokens` | 最大语音 token | 生成音频的最大 mel 长度（长文本可增大） | `1500` |
| `max_text_tokens_per_segment` | 每段最大文本 token | 长文本按标点切分后单段最大 token 数 | `120` |
| `segment_silence_ms` | 段间静音 | 分句之间的停顿时长 | `200` |
| `text_normalization` | 文本归一化 | 自动把 `25%`→`百分之二十五`、日期、单位等展开成可朗读文本 | `true` |

**输出**：
- `sampling`：采样配置（连接到语音生成节点）
- `sampling_info`：配置摘要文本（可接显示节点调试）

---

## 🔤 自定义发音标注

直接写在**待合成文本**中，精确控制字/词读音：

### 中文（拼音 + 声调 1~5）
```
受不<了|liao3>你了
长<行|xíng>和银<行|háng>的读法不一样
<苹果|píng guǒ>很好吃
```
> 声调：`1` 阴平、`2` 阳平、`3` 上声、`4` 去声、`5` 轻声

### 英文（CMU 音素）
```
I <live|l-ay-v> in Shanghai.      # 动词：居住
<live|l-ih-v> music is great.     # 形容词：现场的
```

### 日文（假名）
```
<今日|きょう>は<天気|てんき>がいいです。
<明日|あした>また<会|あ>いましょう。
```

---

## 🎬 示例工作流

仓库内已预置 **4 个可直接导入的工作流 JSON**，位于 `example_workflows/` 目录：

| 文件 | 说明 |
| :--- | :--- |
| `indextts25-basic.json` | 最简基础工作流：模型加载器 + 参考音频 + 文本 → 合成 |
| `indextts25-emotion-vector.json` | 八维情感向量模式（高兴/悲伤等组合） |
| `indextts25-multilingual.json` | 中/英/日/西/阿 多语言混合示例 |
| `indextts25-save-audio.json` | 完整流水线：含音频保存节点 |

使用方式：在 ComfyUI 菜单选择 **Load** → 选择对应 JSON 文件即可。

---

## ❓ 常见问题 FAQ

| 现象 | 解决方案 |
| :--- | :--- |
| 模型加载器显示「未找到」 | ① 模型路径：确认位于 `ComfyUI/models/TTS/IndexTTS-2.5/` ② 放入模型后**重启 ComfyUI** |
| 输出为空 / 没声音 | 检查：文本是否为空、参考音频是否 ≥0.25s、`max_mel_tokens` 是否过小 |
| 显存不足 OOM | ① 精度改为 `bfloat16` ② 开启「生成后释放模型」③ 关闭 `use_qwen_emo` ④ 改用 CPU（慢） |
| 中文数字/符号读错 | 确认 `text_normalization` 已开启（默认开）；或用 `<字\|读音>` 手工标注 |
| 某字读错音 | 直接在文本内用拼音标注，例如：`<银行|yín háng>` |
| 情感没变化 | ① 确认情感节点已连接 ② `strength` 调大到 0.8~1.0 ③ 向量模式可单维加到 1.0~1.2 |
| 相同 seed 结果不同 | 关闭 `do_sample`（切到确定性束搜索），并固定 seed |
| 首次生成特别慢 | 首次加载需读 5GB 模型；之后会缓存，速度正常 |
| 日文假名分词不准 | 在文本里写 `<汉字\|假名>` 标注即可 |

---

## 🙏 致谢 & 引用

### 源项目（核心代码与模型）
- **[index-tts / index-tts](https://github.com/index-tts/index-tts)** — Bilibili IndexTTS Team 官方项目，IndexTTS 2.5 的作者
  - Paper: [IndexTTS 2.5](https://github.com/index-tts/index-tts)
  - HuggingFace: [IndexTeam/IndexTTS-2.5](https://huggingface.co/IndexTeam/IndexTTS-2.5)
  - ModelScope: [IndexTeam/IndexTTS-2.5](https://www.modelscope.cn/models/IndexTeam/IndexTTS-2.5)

### 社区与依赖
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) — 强大的节点式 Stable Diffusion / AI 工作流平台
- [BigVGAN](https://github.com/NVIDIA/BigVGAN) · [Amphion Codec](https://github.com/open-mmlab/Amphion) · [DAC](https://github.com/descriptinc/descript-audio-codec) · [Vocos](https://github.com/gemelo-ai/vocos) — 声码器与编解码器
- [ECAPA-TDNN](https://github.com/TaoRuijie/ECAPA-TDNN) / [CAM++](https://github.com/modelscope/3D-Speaker) — 说话人编码器
- [wav2vec 2.0 BERT](https://huggingface.co/facebook/wav2vec2-bert-CV16-base) · [Qwen 0.6B Emotion](https://huggingface.co/) — 语义/情感模型

---

## 📜 许可证 & 免责声明

- 插件代码（ComfyUI 节点封装部分）：MIT License
- 内置 IndexTTS 官方代码：见仓库内 `LICENSE`、`LICENSE_ZH.txt`
- 模型权重：遵循 IndexTTS 官方模型许可证（Bilibili IndexTTS Team 授权）
- 免责声明：见 `DISCLAIMER` 文件

> **注意**：请确保使用该插件合成音频时遵循当地法律法规，并获得音色参考音频权利人的授权，不得用于欺诈、冒充、违法等用途。

---

## 📮 反馈 & 支持

- 🐛 Bug 反馈：[GitHub Issues](https://github.com/xiaozhuguang/Comfyui-indextts25-xzg/issues)
- 💬 讨论区：[GitHub Discussions](https://github.com/xiaozhuguang/Comfyui-indextts25-xzg/discussions)
- ⭐ 如果本插件对你有帮助，欢迎点个 Star！

---

<div align="center">
  <a href="https://github.com/xiaozhuguang/Comfyui-indextts25-xzg/stargazers">
    <img src="https://img.shields.io/github/stars/xiaozhuguang/Comfyui-indextts25-xzg?style=social" alt="GitHub Stars">
  </a>
  <a href="https://github.com/xiaozhuguang/Comfyui-indextts25-xzg/forks">
    <img src="https://img.shields.io/github/forks/xiaozhuguang/Comfyui-indextts25-xzg?style=social" alt="GitHub Forks">
  </a>
  <a href="https://github.com/xiaozhuguang/Comfyui-indextts25-xzg/watchers">
    <img src="https://img.shields.io/github/watchers/xiaozhuguang/Comfyui-indextts25-xzg?style=social" alt="GitHub Watchers">
  </a>
</div>
