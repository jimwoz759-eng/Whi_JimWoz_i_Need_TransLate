# Whi_JimWoz_i_Need_TransLate

> 把音频文件扔进来，GitHub Actions 自动用 OpenAI Whisper Large 转写成文字。

---

## 工作原理

```
audio/ 里放入音频文件
        ↓
git push 触发 GitHub Actions
        ↓
CI 自动安装 openai-whisper（large 模型）
        ↓
转写完成，结果写入 transcripts/
        ↓
自动 commit 回仓库
```

---

## 仓库结构

```
├── .github/workflows/transcribe.yml   # CI 配置
├── audio/                             # 把音频放这里 ← 你只需要管这里
├── transcripts/                       # 自动生成的转写结果（不需要手动创建）
├── transcribe.py                      # 转写脚本
└── requirements.txt                   # 依赖：openai-whisper
```

---

## 使用方法

### 1. 把音频文件放入 `audio/`

支持格式：`.mp3` `.wav` `.m4a` `.flac` `.ogg` `.aac` `.mp4` `.webm`

```bash
git clone https://github.com/jimwoz759-eng/Whi_JimWoz_i_Need_TransLate.git
cd Whi_JimWoz_i_Need_TransLate

# 把你的音频文件复制到 audio/ 文件夹
cp /path/to/your/audio.mp3 audio/

git add audio/
git commit -m "add audio"
git push
```

### 2. 等待 CI 完成

前往 [Actions 页面](../../actions) 查看进度。

转写时会逐句打印时间戳，例如：

```
[00:00.000 --> 00:04.320]  大家好，今天我们来讲...
[00:04.320 --> 00:09.100]  首先第一个问题是...
```

### 3. 获取结果

CI 结束后，结果自动提交回仓库：

```
transcripts/
├── audio.txt    # 纯文字
└── audio.srt    # 带时间戳字幕
```

也可以在 Actions 页面下载 **Artifact**（即使 CI 失败，已完成的部分也会保存）。

---

## 手动触发 / 指定参数

在 [Actions 页面](../../actions) 点击 **Run workflow**，可以手动指定：

| 参数 | 说明 | 默认值 |
|---|---|---|
| `model` | Whisper 模型 | `large` |
| `language` | 语言代码，如 `zh`、`en`、`ja` | 留空自动检测 |

指定语言（如 `zh`）可以提高准确率，同时省去自动检测的时间。

---

## 模型说明

本仓库默认使用 **Whisper Large（large-v3）**，是 Whisper 系列中参数量最大、准确率最高的版本。

| 模型 | 参数量 | 相对速度 | 适用场景 |
|---|---|---|---|
| `tiny` | 39M | 最快 | 测试 |
| `base` | 74M | 快 | 清晰英文 |
| `small` | 244M | 较快 | 日常使用 |
| `medium` | 769M | 一般 | 较高准确率 |
| **`large`** | **1550M** | **最慢** | **最高准确率（默认）** |
| `turbo` | 809M | 快 8 倍 | large 的加速裁剪版 |

> ⚠️ `large` 在 GitHub Actions 免费 CPU runner 上速度较慢，1 小时音频大约需要 3～6 小时转写时间。

---

## 注意事项

| 事项 | 说明 |
|---|---|
| **文件大小** | 单个音频文件不超过 100MB（Git 限制）；更大的文件请使用 Git LFS |
| **模型缓存** | 第一次运行需下载约 3GB 模型；之后命中缓存自动跳过 |
| **超时接续** | 若 CI 超时，脚本会自动跳过已完成的文件，再次 push 即可继续 |
| **仓库可见性** | 本仓库为公开仓库，音频和转写内容任何人可见 |
| **并发保护** | 多次连续 push 时，CI 任务自动排队，不会重复转写同一批文件 |

---

## 依赖

- [openai-whisper](https://github.com/openai/whisper) — OpenAI 官方 Whisper 实现
- [ffmpeg](https://ffmpeg.org/) — 音频解码（CI 自动安装）
- [PyTorch](https://pytorch.org/)（CPU 版）— 模型推理后端

---

## License

MIT
