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

> 本插件是对 [index-tts/index-tts](https://github.com/index-tts/index-tts) 官方项目的 ComfyUI 适配封装，完整文档与许可证请参考源仓库。
