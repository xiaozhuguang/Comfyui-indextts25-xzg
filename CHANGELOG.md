# 更新日志 / Changelog

本插件遵循 [语义化版本](https://semver.org/lang/zh-CN/)。每个版本的详细变更记录如下。

## [2.0.1] - 2026-08-21

### 优化

- **响度测量升级为 BS.1770 双阶段门控**（[`audio_normalizer.py`](./runtime/audio_normalizer.py)）：
  原单阶段 `-60 dBFS` 静音门限改为「绝对门 `-70 dBFS` + 相对门 `-10 dB` 低于活跃帧均值」，
  呼吸声、房间底噪、淡出尾音不会再拉低测量值，`match reference` 对齐精度显著提升。
- **输出端新增 soft-knee 软峰值限制器**（`_soft_limit` + `normalize_rms_limited`）：
  峰值超出天花板时，`match reference` / `rms -16 dB` 模式不再直接裁剪，
  而是用 2dB soft-knee + tanh 渐进压缩吸收温和过冲，实际输出响度更贴近目标。
  若软压缩导致响度损失超过 1.5 dB（目标不可及），会自动回退到保守峰值增益，音质优先。
- **状态栏提示细化**：当实际 RMS 低于目标 1 dB 以上时，会追加说明
  「低于目标 X dB，已受峰值保护限制」，便于判断是否需要降低参考响度或换用 `peak -1 dB`。

### 修复

- **参考缓存版本标签升级**（[`reference_cache.py`](./runtime/reference_cache.py)）：
  hash salt 从 `refnorm-rms20-dc` → `refnorm-v2-gate`，
  门控算法升级后旧缓存自动失效，避免历史缓存影响归一化结果。
- **GPT 模型显式继承 GenerationMixin**（`indextts/gpt/model.py` / `model_v2.py` / `model_v2_5.py`）：
  与本地私有 `transformers_generation_utils.GenerationMixin` 绑定，
  进一步加固 transformers 4.x / 5.x 混合环境下的 MRO 解析。

## [2.0.0] - 2026-08-20

### 新增

- **音频归一化（gated-RMS）**：新建 `runtime/audio_normalizer.py`，实现带静音门限的 gated-RMS 响度测量
  （借鉴 ITU-R BS.1770 gating 思想，50ms 分帧 + -60 dBFS 静音阈值，首尾静音不拉低测量值），
  以及去直流偏置、峰值天花板、非对称增益限幅（放大限幅、衰减放宽）等全套处理。

### 变更

- **参考音频响度标准化**（输入侧，[`reference_cache.py`](./runtime/reference_cache.py)）：
  说话人 / 情感参考音频在重采样后统一经去 DC → gated-RMS 归到 **-20 dBFS** → 峰值限 **-3 dBFS**；
  实测增益会出现在状态栏（例如「speaker 已响度归一化到 -20 dBFS（增益 +9.1 dB）」）；
  缓存 hash 纳入归一化标签，版本变化不会命中旧缓存。
- **生成音频响度控制**（输出侧，[`audio_normalizer.py`](./runtime/audio_normalizer.py) / [`inference_adapter.py`](./runtime/inference_adapter.py)）：
  「XZG_IndexTTS25_Speech_Generate」节点新增 advanced 参数 **Output Normalization**：
  - `match reference`（默认）：输出按参考音频原始响度缩放，**输入多大输出就多大**，
    同时用 -1 dBFS 峰值天花板兜底，避免对齐到很响的参考时削波；
  - `rms -16 dB`：按播客标准（-16 dBFS RMS / -1 dBFS peak）统一响度，多段拼接响度一致；
  - `peak -1 dB`：峰值归一化；
  - `off`：模型原始输出（仅 clamp）。
- **`node_list.json` 版本号**升至 `2.0.0`，Generate 节点 `inputs` 追加 `output_normalization`。

### 说明

- 实现全程使用 PyTorch 原生算子，无第三方依赖（如 `pyloudnorm`），离线环境不受影响。
- 参考音频的原始响度在归一化前测量并一路传出，`match reference` 用它缩放结果；
  而**进模型**的参考仍是归一化到 -20 dBFS 的稳定版本，保证音色克隆和情感抽取稳定。

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
