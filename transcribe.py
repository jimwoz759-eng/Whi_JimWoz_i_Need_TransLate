import os
import sys
from pathlib import Path

import torch
import whisper
from whisper.utils import get_writer

# 管道输出时也逐行刷新，CI 日志才能实时看到进度
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

torch.set_num_threads(os.cpu_count() or 4)

AUDIO_DIR  = Path("audio")
OUT_DIR    = Path("transcripts")
MODEL_NAME = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else "large"
LANGUAGE   = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else None
EXTS = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".opus", ".aac", ".mp4", ".webm"}

OUT_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(exist_ok=True)


def out_dir_of(f: Path) -> Path:
    return OUT_DIR / f.relative_to(AUDIO_DIR).parent


def is_done(f: Path) -> bool:
    d = out_dir_of(f)
    return (d / f"{f.stem}.txt").exists() and (d / f"{f.stem}.srt").exists()


def is_lfs_pointer(f: Path) -> bool:
    """checkout 没开 lfs 时，大文件只是一个几百字节的指针文本。"""
    try:
        return f.stat().st_size < 1024 and f.read_bytes().startswith(b"version https://git-lfs")
    except OSError:
        return False


# 加 is_file()：避免名为 "xxx.mp3" 的目录被当成音频
files = [p for p in sorted(AUDIO_DIR.rglob("*")) if p.is_file() and p.suffix.lower() in EXTS]

# 同目录同主文件名（a.mp3 与 a.wav）会写成同一个 a.txt/a.srt，互相覆盖
_seen = {}
for p in files:
    _seen.setdefault((p.parent, p.stem), []).append(p.name)
for (_, stem), names in _seen.items():
    if len(names) > 1:
        print(f"[警告] 主文件名冲突，输出会互相覆盖：{names}，请改名", file=sys.stderr)

pending = [f for f in files if not is_done(f)]

if not pending:
    print("没有需要转写的新音频，退出。")
    sys.exit(0)

print(f"待转写 {len(pending)} 个文件 | 模型：{MODEL_NAME} | 语言：{LANGUAGE or '自动检测'}")

model = whisper.load_model(MODEL_NAME)

failed = []
for f in pending:
    print(f"\n===== 转写中：{f} =====")
    try:
        if is_lfs_pointer(f):
            raise RuntimeError("这是 Git LFS 指针文件，不是真实音频（checkout 需要 lfs: true）")
        opts = {"fp16": False, "verbose": True}
        if LANGUAGE:
            opts["language"] = LANGUAGE
            if LANGUAGE == "zh":
                opts["initial_prompt"] = "以下是普通话的句子。"
        result = model.transcribe(str(f), **opts)
        d = out_dir_of(f)
        d.mkdir(parents=True, exist_ok=True)
        for fmt in ("srt", "txt"):
            get_writer(fmt, str(d))(result, f.name, {})
        print(f"完成：{f.name}")
    except Exception as e:
        print(f"[错误] {f}：{e}", file=sys.stderr)
        failed.append(str(f))

if failed:
    print("\n以下文件转写失败：\n" + "\n".join(failed), file=sys.stderr)
    sys.exit(1)
