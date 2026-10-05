# make-book-notes

## Purpose

A tiny personal CLI. It transcribes voice notes I record while reading a book and writes them into my Obsidian vault as a single markdown file.

- Fully local: no network calls, no cloud APIs.
- No LLM-generated content: no summaries, no cleanup, no rewriting.
- Just for me: no GUI, no packaging for others, no configurability beyond what is listed below.

## Context

I keep a small USB voice recorder with an SD card by my bed. While reading, I record a short MP3 for each passage I like. I start each note by saying the page number ("page 57, they're talking about..."), then give my thoughts. I end up with roughly 10-15 recordings per book. When I finish the book, I plug the SD card into my computer and run this tool with the dates I read the book (from Goodreads).

## Usage

```
make-book-notes "Book Title" --from 2026-09-01 --to 2026-09-20
```

| Argument | Required | Description |
|---|---|---|
| `title` (positional) | yes | Book title. Used as the output filename. |
| `--from YYYY-MM-DD` | yes | Start date, inclusive. |
| `--to YYYY-MM-DD` | yes | End date, inclusive. |
| `--src PATH` | no | Folder containing the audio files. Defaults to `DEFAULT_SRC`. |
| `--model NAME` | no | Whisper model name. Defaults to `small.en`. |

## Behaviour

1. Recursively find audio files (`.mp3`, `.wav`, `.m4a`) under `--src`.
2. Keep only files whose modified time (`st_mtime`, local time) falls between the start of `--from` and the end of `--to`, inclusive.
3. Sort the remaining files by modified time, oldest first.
4. Load the Whisper model once, then transcribe each file locally with `faster-whisper` (English only, CPU is fine).
5. Write one markdown file to `VAULT / NOTES_DIR / "<title>.md"`. Overwrite if it exists; the audio is the source of truth, so the file is regenerated on each run.
6. Print one progress line per file to stdout (e.g. `[3/12] REC0003.mp3`), then the output path at the end.

## Output format

One block per recording, separated by a blank line:

```markdown
## Page 57
- 

<transcribed text>

## Page 63
- 

<transcribed text>
```

- **Heading:** `## Page N`, where N is the first match of the regex `page\s+(\d+)` (case-insensitive) in the transcript. If there is no match, use the audio filename as the heading instead (e.g. `## REC0003.mp3`).
- **Summary line:** an empty `- ` line, left blank for me to fill in by hand.
- **Body:** the raw transcript exactly as Whisper returns it, stripped of leading/trailing whitespace. No cleanup, no summarising.

## Config

Constants at the top of the script. No config file, no env vars.

```python
VAULT = Path("~/Documents/Obsidian/MyVault").expanduser()
NOTES_DIR = "Books"
DEFAULT_SRC = Path("/Volumes/RECORDER")
```

## Implementation constraints

- Python 3.10+.
- A single file, `make_book_notes.py`, of about 60 lines or fewer.
- Dependency: `faster-whisper` only. Everything else is standard library (`argparse`, `pathlib`, `datetime`, `re`).
- Plain functions only: no classes, no logging framework, no retry logic, no tests.
- Installable as a command with a minimal `pyproject.toml` console-script entry (`make-book-notes = make_book_notes:main`), or a shell alias, whichever is simpler.
- Fail loudly with a clear one-line error (and non-zero exit) if `--src` does not exist, or if no files match the date range.
- Code should be clean, minimal and readable, with no defensive over-engineering and no verbose comments.

## Out of scope

Summaries, tagging, speaker detection, a GUI, incremental/append mode, fetching dates from Goodreads (I pass them in manually), non-English transcription, and filtering by anything other than modified time.

## Known caveat

Date filtering relies on file modified time. If the recorder's clock is unset, files may all be stamped with a placeholder date. If that happens, the date filter should be changed to parse dates from filenames instead.

