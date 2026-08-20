# 更新日志 / Changelog

本插件遵循 [语义化版本](https://semver.org/lang/zh-CN/)。每个版本的详细变更记录如下。

## [1.0.1] - 2026-08-20

### 修复

- **transformers 5.x 兼容性问题**：修复 `ImportError: cannot import name 'OffloadedCache' from 'transformers.cache_utils'`。
  环境中若安装了 transformers 5.x（例如被其他插件自动升级），节点将无法加载。
  现已在内置的 GPT 私有代码中添加向后兼容层：
  - `OffloadedCache` → 回退 `DynamicCache`
  - `isin_mps_friendly` → 回退 `torch.isin`
  - `ExtensionsTrie` → 本地最小前缀树实现
  - `find_pruneable_heads_and_indices` / `prune_conv1d_layer` / `prune_layer` → 本地重实现
- **BigVGAN 模块缺失**：补齐缺失的 `indextts/BigVGAN/env.py`（`AttrDict` / `build_env`），
  修复 `ModuleNotFoundError: No module named 'indextts.BigVGAN.env'`。

### 变更

- **依赖版本约束收紧**（`requirements.txt`），防止其他插件把共享环境拉到不兼容版本：
  - `transformers>=4.40.0,<5.0`（5.x 移除了大量本项目依赖的内部 API，明确禁止）
  - `huggingface-hub>=0.34.0,<1.0`
  - `tokenizers>=0.22.0,<=0.23.0`
  - 新增 `openai-whisper>=20231117`（多语言分词器依赖 `whisper.tokenizer`）

### 说明

- 离线环境（`HF_HUB_OFFLINE=1`）首次加载时，辅助模型（w2v-bert-2.0 / campplus / bigvgan / MaskGCT codec）
  会自动下载到 `ComfyUI/models/TTS/IndexTTS-2.5/hf_cache/`；该目录为运行必需，请勿删除（详见 README FAQ）。
- Release Notes 现在从本文件自动提取对应版本段落，不再使用硬编码模板。

## [1.0.0] - 2026-08-18

### 首次发布

- 基于官方 [index-tts/index-tts](https://github.com/index-tts/index-tts) 适配的 ComfyUI 自定义节点插件
- 零样本音色克隆（≥0.25 秒参考音频）
- 五国语言：ZH / EN / JA / ES / AR
- 四种情感控制：八维向量 / 情感参考音频 / 文本描述 / 跟随音色
- 4 个节点：模型加载器 / 语音生成 / 情感控制 / 采样设置
- 双语界面（中/英）
