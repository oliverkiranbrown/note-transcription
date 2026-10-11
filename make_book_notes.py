"""Transcribe voice notes into a single Obsidian markdown file."""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date, datetime, time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

VAULT = Path(os.environ.get("VAULT", "~/Documents/Obsidian/MyVault")).expanduser()
NOTES_DIR = os.environ.get("NOTES_DIR", "Books")
RECORDINGS_DIR = VAULT / os.environ.get("RECORDINGS_DIR", "Media/Attachments")
DEFAULT_SRC = Path(os.environ.get("DEFAULT_SRC", "/Volumes/RECORDER"))
OUTPUT_FORMAT = os.environ.get("OUTPUT_FORMAT", "opus")
AUDIO_SUFFIXES = {".mp3", ".wav", ".m4a", ".opus", ".ogg", ".flac", ".aac"}
PAGE_RE = re.compile(r"page\s+(?:number\s+)?(\d+)", re.IGNORECASE)


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


def convert(src: Path, fmt: str, tmp_dir: str) -> Path:
    """Re-encode *src* to *fmt* using ffmpeg; return the path of the new file."""
    out = Path(tmp_dir) / src.with_suffix(f".{fmt}").name
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", str(src), str(out)],
        capture_output=True,
    )
    if result.returncode != 0:
        fail(f"ffmpeg failed on {src.name}:\n{result.stderr.decode().strip()}")
    return out


def heading(text: str, filename: str) -> str:
    m = PAGE_RE.search(text)
    return f"### Page {m.group(1)}" if m else f"### {filename}"


def block(title: str, embed: str, text: str) -> str:
    quote = "\n".join(f"> {ln}".rstrip() for ln in text.splitlines())
    return f"{title}\n\n{embed}\n\n{quote}"


def main():
    parser = argparse.ArgumentParser(description="Transcribe book voice notes into Obsidian markdown.")
    parser.add_argument("title", help="Book title, used as the output filename.")
    parser.add_argument("--from", dest="from_date", required=True, type=date.fromisoformat,
                        metavar="YYYY-MM-DD", help="Start date, inclusive.")
    parser.add_argument("--to", dest="to_date", required=True, type=date.fromisoformat,
                        metavar="YYYY-MM-DD", help="End date, inclusive.")
    parser.add_argument("--src", type=Path, default=DEFAULT_SRC, help="Folder containing audio files.")
    parser.add_argument("--model", default="small.en", help="Whisper model name.")
    parser.add_argument(
        "--output-format",
        default=OUTPUT_FORMAT,
        metavar="FMT",
        help="Target audio format for vault copies (default: %(default)s). "
             "Any format ffmpeg supports, e.g. opus, mp3, m4a, ogg.",
    )
    args = parser.parse_args()

    files = find_files(args.src, args.from_date, args.to_date)

    RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)

    from faster_whisper import WhisperModel
    model = WhisperModel(args.model, device="cpu")

    blocks = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, f in enumerate(files, 1):
            fmt = args.output_format.lstrip(".")
            needs_convert = f.suffix.lower() != f".{fmt}"
            audio = convert(f, fmt, tmp) if needs_convert else f
            dest = RECORDINGS_DIR / audio.name
            shutil.copy2(audio, dest)
            print(f"[{i}/{len(files)}] {f.name}" + (f" → {audio.name}" if needs_convert else ""))
            segments, _ = model.transcribe(str(f), language="en")
            text = "".join(s.text for s in segments).strip()
            blocks.append(block(heading(text, f.name), f"![[{audio.name}]]", text))

    out_dir = VAULT / NOTES_DIR.lstrip("/")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.title}.md"
    body = f"#book\n\n## Background\n\n\n## Notes\n\n" + "\n\n".join(blocks) + "\n"
    out_path.write_text(body, encoding="utf-8")
    print(out_path)


if __name__ == "__main__":
    main()