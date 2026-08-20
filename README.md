<div align="center">
  <img src="assets/index2.5_video_cover.png" width="600" alt="IndexTTS 2.5 ComfyUI Plugin">
  <h1>🎙️ ComfyUI IndexTTS 2.5 插件</h1>
  <p>
    <a href="https://github.com/xiaozhuguang/Comfyui-indextts25-xzg/releases">
      <img src="https://img.shields.io/github/v/release/xiaozhuguang/Comfyui-indextts25-xzg?label=Release&logo=github">
    </a>
    <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-blue?logo=linux">
    <img src="https://img.shields.io/badge/VRAM-8GB%2B-yellow?logo=nvidia">
  </p>
  <p><b>零样本音色克隆 · 五国语言 · 情感控制</b></p>
</div>

---

## 📌 简介

本项目是基于官方 [index-tts/index-tts](https://github.com/index-tts/index-tts) 适配的 **ComfyUI 自定义节点插件**，将 IndexTTS-2.5 的零样本 TTS 能力接入 ComfyUI 工作流。

- 零样本音色克隆（≥0.25 秒参考音频）
- 五国语言：ZH / EN / JA / ES / AR
- 四种情感控制：八维向量 / 情感参考音频 / 文本描述 / 跟随音色
- 4 个 ComfyUI 节点：模型加载器 / 语音生成 / 情感控制 / 采样设置
- 双语界面（中/英）

---

## 📦 安装

### 方式一：ComfyUI Manager（推荐）
1. ComfyUI → **Manager** → **Install via Git URL**
2. 填入：`https://github.com/xiaozhuguang/Comfyui-indextts25-xzg`
3. 安装完成后重启 ComfyUI

### 方式二：手动 Clone
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/xiaozhuguang/Comfyui-indextts25-xzg.git
```

### 安装依赖
```bash
# Windows（ComfyUI 自带 Python）
python_embeded/python.exe -m pip install -r ComfyUI/custom_nodes/Comfyui-indextts25-xzg/requirements.txt

# Linux / macOS
python -m pip install -r custom_nodes/Comfyui-indextts25-xzg/requirements.txt
```

---

## 📥 模型下载（约 5GB+）

下载后放到 `ComfyUI/models/TTS/IndexTTS-2.5/`。

| 渠道 | 地址 |
| :--- | :--- |
| **夸克网盘**（国内推荐） | <https://pan.quark.cn/s/f933f6037874> |
| 自动脚本（ModelScope） | `python scripts/download_models.py --source modelscope --accept-license` |
| 自动脚本（HuggingFace） | `python scripts/download_models.py --source huggingface --accept-license` |
| HuggingFace 手动 | <https://huggingface.co/IndexTeam/IndexTTS-2.5> |
| ModelScope 手动 | <https://www.modelscope.cn/models/IndexTeam/IndexTTS-2.5> |

下载完成后**重启 ComfyUI**。

---

## ⚠️ 常见问题

<details>
<summary><b>hf_cache 目录是什么？能删吗？</b></summary>

`ComfyUI/models/TTS/IndexTTS-2.5/hf_cache/` 存放 4 个第三方辅助模型（w2v-bert-2.0 / campplus / bigvgan / MaskGCT codec，约 2.8GB），由 Meta / NVIDIA / 阿里 / Amphion 提供，不在 IndexTTS 官方模型包内，但推理管线必需。**不能删除**，否则离线环境下节点会报 `LocalEntryNotFoundError` 并重新下载。
</details>

<details>
<summary><b>报 ImportError: cannot import name 'OffloadedCache'</b></summary>

环境中 transformers 被其他插件升级到 5.x 导致。v1.0.1 已内置兼容层并锁定 `transformers<5.0`。若仍出现，请执行：

```bash
python -m pip install "transformers>=4.40.0,<5.0" "huggingface-hub>=0.34.0,<1.0"
```
</details>

---

## 📋 更新日志

| 版本 | 日期 | 变更 |
| :--- | :--- | :--- |
| **v1.0.1** | 2026-08-20 | 修复 transformers 5.x 兼容性；补齐 BigVGAN env 模块；收紧依赖版本约束 |
| v1.0.0 | 2026-08-18 | 首次发布 |

完整变更记录见 [CHANGELOG.md](./CHANGELOG.md)。

---

> 本插件是对 [index-tts/index-tts](https://github.com/index-tts/index-tts) 官方项目的 ComfyUI 适配封装，完整文档与许可证请参考源仓库。
