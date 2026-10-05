"""Transcribe voice notes into a single Obsidian markdown file."""

import argparse
import re
import shutil
import sys
from datetime import date, datetime, time
from pathlib import Path

VAULT = Path("~/Documents/Obsidian/MyVault").expanduser()
NOTES_DIR = "Books"
RECORDINGS_DIR = VAULT / "Media" / "Attachments"
DEFAULT_SRC = Path("/Volumes/RECORDER")
AUDIO_SUFFIXES = {".mp3", ".wav", ".m4a"}
PAGE_RE = re.compile(r"page\s+(\d+)", re.IGNORECASE)


def fail(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def find_files(src: Path, from_date: date, to_date: date) -> list[Path]:
    if not src.is_dir():
        fail(f"Source folder not found: {src}")
    start = datetime.combine(from_date, time.min)
    end = datetime.combine(to_date, time.max)
    files = [
        p for p in sorted(src.rglob("*"))
        if p.suffix.lower() in AUDIO_SUFFIXES
        and start <= datetime.fromtimestamp(p.stat().st_mtime) <= end
    ]
    if not files:
        fail(f"No audio files modified between {from_date} and {to_date}.")
    return sorted(files, key=lambda p: p.stat().st_mtime)


def heading(text: str, filename: str) -> str:
    m = PAGE_RE.search(text)
    return f"## Page {m.group(1)}" if m else f"## {filename}"


def main():
    parser = argparse.ArgumentParser(description="Transcribe book voice notes into Obsidian markdown.")
    parser.add_argument("title", help="Book title, used as the output filename.")
    parser.add_argument("--from", dest="from_date", required=True, type=date.fromisoformat,
                        metavar="YYYY-MM-DD", help="Start date, inclusive.")
    parser.add_argument("--to", dest="to_date", required=True, type=date.fromisoformat,
                        metavar="YYYY-MM-DD", help="End date, inclusive.")
    parser.add_argument("--src", type=Path, default=DEFAULT_SRC, help="Folder containing audio files.")
    parser.add_argument("--model", default="small.en", help="Whisper model name.")
    args = parser.parse_args()

    files = find_files(args.src, args.from_date, args.to_date)

    RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
    for f in files:
        shutil.copy2(f, RECORDINGS_DIR / f.name)

    from faster_whisper import WhisperModel
    model = WhisperModel(args.model, device="cpu")

    blocks = []
    for i, f in enumerate(files, 1):
        print(f"[{i}/{len(files)}] {f.name}")
        segments, _ = model.transcribe(str(f), language="en")
        text = "".join(s.text for s in segments).strip()
        blocks.append(f"{heading(text, f.name)}\n- \n\n![[{f.name}]]\n\n{text}")

    out_dir = VAULT / NOTES_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.title}.md"
    out_path.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
    print(out_path)


if __name__ == "__main__":
    main()