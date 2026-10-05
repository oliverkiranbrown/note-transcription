# make-book-notes

A tiny personal CLI that turns voice notes recorded while reading a book into a single Obsidian markdown file, fully locally via [faster-whisper](https://github.com/SYSTRAN/faster-whisper).

## Why

Reading with a notebook in hand breaks the flow: you stop, write, lose the thread, and by the time you finish the book the notes never get written up. Instead, keep a small voice recorder (e.g. a Digital Voice Activated Dictaphone with noise reduction) beside you while you read. Whenever a passage is worth keeping, press record, say the page number, and talk through your thoughts for a few seconds — then get straight back to the book.

You end up with 10–15 short audio files per book, captured *while the ideas are fresh*, without ever leaving the page. When you finish the book, plug the recorder in and run this tool with the dates you read it. It collects every recording from that window, transcribes them locally, copies the audio into your vault, and assembles one note where each thought is a heading with the original recording embedded and transcribed beneath it. Your highlights, reactions, and half-formed ideas are seamlessly connected on the page, ready to be tidied up by hand.

## Install

```
uv sync
```

## Make it available from anywhere

Install it as a global command (like `pipx`) — no `cd` into the project, no `uv run` prefix:

```
uv tool install --editable .
```

This puts `make-book-notes` on your PATH (`~/.local/bin`) with its own isolated environment. The `--editable` flag means it runs directly from this project's source: edit `make_book_notes.py` and the change is live immediately, no reinstall needed. (If your shell can't find the command right after installing, run `hash -r` or open a new terminal tab.)

To uninstall later: `uv tool uninstall note-transcription`.

## Usage

From anywhere in your terminal:

```
make-book-notes "Book Title" --from 2026-09-01 --to 2026-09-20
```

Options: `--src PATH` (audio folder, default from `.env`), `--model NAME` (Whisper model, default `small.en`).

Finds `.mp3`/`.wav`/`.m4a` files under `--src` whose modified time falls in the date range (inclusive), copies them into `VAULT/RECORDINGS_DIR`, transcribes them oldest-first, and writes one block per recording to `VAULT/NOTES_DIR/<title>.md`:

```markdown
#book

## Background


## Notes

### Page 57

![[REC0003.mp3]]

> <transcribed text>
```

Blocks with no spoken page number use the audio filename as the heading. Configure paths via environment variables in `.env` (see `.env.example`): `VAULT`, `NOTES_DIR`, `RECORDINGS_DIR`, `DEFAULT_SRC`.

