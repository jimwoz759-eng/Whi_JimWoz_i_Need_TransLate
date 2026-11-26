# Whi_JimWoz_i_Need_TransLate

> 把音频文件扔进来，GitHub Actions 自动用 OpenAI Whisper Large 转写成文字，并发布到 Release。

---

## 工作原理

```
audio/ 里放入音频文件
        ↓
git push 触发 GitHub Actions（transcribe-release.yml）
        ↓
CI 安装 ffmpeg + CPU 版 PyTorch + openai-whisper（large 模型）
        ↓
转写完成，生成 transcripts/*.txt 与 *.srt
        ↓
每个音频（音频 + txt + srt）打成一个 zip，发布到 Releases
        ↓
从仓库中删除已发布的音频（保留 .gitkeep）
```

---

## 仓库结构

```
├── .github/workflows/
│   ├── transcribe-release.yml   # 默认工作流：push 触发，结果发布到 Release
│   └── transcribe.yml           # 备用工作流：仅手动触发，结果提交回仓库
├── audio/                       # 把音频放这里 ← 你只需要管这里
├── transcripts/                 # 转写结果（CI 生成）
├── transcribe.py                # 转写脚本
└── requirements.txt             # 依赖：openai-whisper（已锁定版本）
```

两个工作流**不要同时开启 push 触发**，否则同一批音频会被转写两次。

---

## 使用方法

### 1. 把音频文件放入 `audio/`

支持格式：`.mp3` `.wav` `.m4a` `.flac` `.ogg` `.opus` `.aac` `.mp4` `.webm`

支持子目录。**同一目录下主文件名相同的文件（如 `a.mp3` 与 `a.wav`）会互相覆盖输出，请避免。**

```bash
git add audio/
git commit -m "add audio"
git push
```

### 2. 等待 CI 完成

前往 Actions 页面查看进度，转写时会逐句打印时间戳。

### 3. 获取结果

在仓库的 **Releases** 页面下载：

- `transcripts-run-<编号>-<次数>-001.zip` ……（每个音频一个 zip，内含音频、`.txt`、`.srt`）
- `MANIFEST.txt`（zip 文件名与原始文件名的对应关系）

也可以在 Actions 页面下载 **Artifact**（即使 CI 失败，已完成的部分也会保存）。

---

## 手动触发 / 指定参数

在 Actions 页面选择工作流，点击 **Run workflow**：

| 参数 | 说明 | 默认值 |
|---|---|---|
| `model` | Whisper 模型 | `large` |
| `language` | 语言代码，如 `zh`、`en`、`ja` | 留空自动检测 |

指定语言（如 `zh`）可以提高准确率，同时省去自动检测的时间。

---

## 模型说明

| 模型 | 参数量 | 适用场景 |
|---|---|---|
| `tiny` | 39M | 测试流程 |
| `base` | 74M | 清晰英文 |
| `small` | 244M | 日常使用 |
| `medium` | 769M | 较高准确率 |
| **`large`** | **1550M** | **最高准确率（默认，large-v3）** |
| `turbo` | 809M | large 的加速裁剪版，速度快很多 |

> ⚠️ `large` 在 GitHub 免费 CPU runner 上非常慢。建议首次部署先用一小段音频 + `tiny` 模型测试整条流程。

---

## 限制与注意事项

| 事项 | 说明 |
|---|---|
| **单任务时长** | GitHub 托管 runner 单个任务上限 6 小时（本仓库设为 360 分钟，转写步骤 335 分钟）。单个音频若在此时间内转不完，无法完成 |
| **文件大小（推送）** | 普通 push 单文件不超过 100MB；更大的音频请使用 Git LFS（工作流已启用 `lfs: true`） |
| **文件大小（Release）** | 每个音频的 zip 须小于 2 GiB，超过会被跳过并保留在仓库中 |
| **模型缓存** | 第一次运行需下载约 3GB 模型；之后命中缓存自动跳过 |
| **断点续传** | 超时或部分失败时，已发布的音频会被删除，剩余的下次 push 继续转写 |
| **仓库可见性** | 公开仓库中，Release、Artifact 和 Git 历史任何人可见；清理只是从最新提交中删除音频，历史中仍可找回 |
| **并发保护** | 多次连续 push 时，CI 任务自动排队 |
| **转写结果** | 默认不保存在仓库中，请及时从 Release 下载 |

---

## 依赖

- [openai-whisper](https://github.com/openai/whisper)
- [ffmpeg](https://ffmpeg.org/)（CI 自动安装）
- [PyTorch](https://pytorch.org/)（CPU 版）

---

## License

MIT
