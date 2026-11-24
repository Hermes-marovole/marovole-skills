# Long X video → transcript + chapter outline

Use when the post body is only a caption and the substance is a long (10–60 min) talk/tutorial video.

## Procedure

1. Metadata + variants: `curl -s https://api.fxtwitter.com/<handle>/status/<id> -o tw.json`; read `tweet.media.videos[].variants` (mp4 bitrates) and `duration`.
2. Download the 480p variant (enough for audio and title-strip OCR, ~110 MB for 40 min). Use ABSOLUTE paths and `curl -L -o v.mp4 -w "%{http_code} %{size_download}\n"`, then `ls -la` — a background command with `cd ~/...` and `curl -s` can silently produce no file, and you only find out after the long step.
3. Audio: `ffmpeg -y -loglevel error -i v.mp4 -ac 1 -ar 16000 a.wav`.
4. Transcribe in the background (terminal background=true, notify=true) so you can do frame work meanwhile:
   `uvx --from mlx-whisper mlx_whisper a.wav --model mlx-community/whisper-large-v3-turbo --language zh --output-format txt --output-dir . --initial-prompt "以下是普通话的句子，使用简体中文。"` (40 min ≈ 2–3 min on M2 Max; the initial prompt keeps output in simplified Chinese).
5. Chapter outline while whisper runs:
   - Overview: `ffmpeg -vf "fps=1/120,scale=240:-1,tile=5x4" -frames:v 1 grid.jpg` → vision tells you the layout (talking head + whiteboard, burned-in chapter bar at top, subtitles).
   - If there is a top chapter bar: `ffmpeg -vf "fps=1/30,crop=480:56:0:0,tile=2x21" -frames:v 2 strip%d.jpg` (480-wide source; each image = 21 min at 30 s granularity). Vision reads every cell; cell index × 30 s = timestamp. This yields a full chapter/sub-question table with start times — far more reliable than inferring structure from the transcript.
6. Loop check: `re.findall(r'(.{2,12}?)\1{5,}', text)`. Whisper txt has no timestamps, so locate the looped region using the chapter table (which sub-question it falls under), cut a generous window `ffmpeg -ss <start> -t <len> -i a.wav seg.wav`, re-run with `--condition-on-previous-text False`, and splice the clean segment over the looped lines (mark the splice in the saved transcript).
7. Deliver the full 1080p download in parallel: start it as one background curl (notify=true) while the 480p/audio work proceeds — the 1080p variant (13 Mbps, ~780 MB for 46 min) completes before transcription does, so the user gets the file without waiting for analysis.
8. Before transcribing, verify the audio extracted from the SMALL file matches the full duration (`ffprobe` the wav; a 480p variant can be a truncation) — the session hit a case where the full 46-min wav transcribed fine from the small file, but check, don't assume.
9. Save the full transcript as its own note next to the main doc, with a header noting machine transcription and known homophone errors (e.g. 小王叔/小黄书=小红书，Bodyly=Body，即算=肌酸). The main doc links to it. PPT slides often carry the exact terminology the ASR mangles — pull one frame per claimed list/dosage and vision-read it to correct the transcript before writing anything that quotes numbers.

## Writing from the transcript

- Use the chapter table as the doc skeleton; keep the speaker's examples (they carry the method).
- Mark the speaker's self-claims (growth numbers, platform-mechanic claims) as unverified; mark illustrative numbers in examples as illustrative, not facts.
