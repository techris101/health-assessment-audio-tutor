# Health Assessment Audio Tutor 🎧

A complete 22-part high-yield clinical audio tutorial series generated from `Health_Assessment_Audio_Tutor_Script.md`.

## Features
- **Voice Engine**: Microsoft Edge Neural TTS (`en-GB-RyanNeural`).
- **Tone & Style**: Calm, authoritative senior clinical tutor.
- **Pronunciation Engine**: 26+ clinical phonetic respellings for complex eponyms, Latin roots, and medical jargon.
- **Precision Pacing**: SSML/digital silence pauses (0.6s between paragraphs, 3.0s after active recall questions, 1.0s between topics).
- **Acoustic Standards**: Loudness normalized to -16 LUFS (mono, 192 kbps MP3).
- **Lessons**: 22 standalone lessons plus `Health_Assessment_FULL.mp3` combined master.

## Repository Structure
- `Health_Assessment_Audio_Tutor_Script.md`: Complete source text and curriculum.
- `Antigravity_Audio_Build_Prompt.txt`: Engineering specifications and rules.
- `scripts/build_audio.py`: Synthesis, chunking, respelling, and normalization engine.
- `.github/workflows/build.yml`: Automated CI pipeline generating and publishing the audio files.
