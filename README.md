# make-book-notes

Transcribes voice notes recorded while reading a book into a single Obsidian markdown file, fully locally via [faster-whisper](https://github.com/SYSTRAN/faster-whisper).

## Install

```
uv sync
```

## Usage

```
make-book-notes "Book Title" --from 2026-09-01 --to 2026-09-20
```

Options: `--src PATH` (audio folder, default `/Volumes/RECORDER`), `--model NAME` (Whisper model, default `small.en`).

Finds `.mp3`/`.wav`/`.m4a` files under `--src` whose modified time falls in the date range (inclusive), copies them into `VAULT/Media/Attachments`, transcribes them oldest-first, and writes one block per recording to `VAULT/NOTES_DIR/<title>.md`:

```markdown
## Page 57
- 

![[REC0003.mp3]]

<transcribed text>
```

Blocks with no spoken page number use the audio filename as the heading. Edit `VAULT`, `NOTES_DIR`, `RECORDINGS_DIR`, and `DEFAULT_SRC` at the top of `make_book_notes.py`.

