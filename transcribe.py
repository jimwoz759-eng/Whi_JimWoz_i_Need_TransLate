import os
import sys
from pathlib import Path

import torch
import whisper
from whisper.utils import get_writer

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


files   = [p for p in sorted(AUDIO_DIR.rglob("*")) if p.suffix.lower() in EXTS]
pending = [f for f in files if not is_done(f)]

if not pending:
    print("没有需要转写的新音频，退出。")
    sys.exit(0)

print(f"待转写 {len(pending)} 个文件 | 模型：{MODEL_NAME} | 语言：{LANGUAGE or '自动检测'}")

model = whisper.load_model(MODEL_NAME)

failed = []
for f in pending:
    print(f"\n===== 转写中：{f} =====", flush=True)
    try:
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
        print(f"完成：{f.name}", flush=True)
    except Exception as e:
        print(f"[错误] {f}：{e}", file=sys.stderr, flush=True)
        failed.append(str(f))

if failed:
    print("\n以下文件转写失败：\n" + "\n".join(failed), file=sys.stderr)
    sys.exit(1)
