#!/usr/bin/env python3
"""
Health Assessment Audio Tutor - Audio Build Pipeline
Uses Microsoft Edge Neural TTS (edge-tts), pydub, and FFmpeg.
Generates 22 high-yield audio tutorial MP3 lessons + 1 combined full master audio file.
"""

import os
import sys
import re
import asyncio
import subprocess
import argparse
import tempfile
from pathlib import Path
from pydub import AudioSegment

# Configuration
DEFAULT_VOICE = "en-GB-RyanNeural"
DEFAULT_RATE = "-4%"
SCRIPT_PATH = Path("Health_Assessment_Audio_Tutor_Script.md")
OUTPUT_DIR = Path("Health_Assessment_Audio")

# Canonical file names for the 22 parts
PART_FILENAMES = {
    1: "Part01_Welcome_Nursing_Process.mp3",
    2: "Part02_Data_Types_Sources_Methods_Validation.mp3",
    3: "Part03_Organizing_Documenting_Assessment_Tools.mp3",
    4: "Part04_History_Taking_Approach_Profile_Present_Illness.mp3",
    5: "Part05_History_Taking_Past_Family_Social_System_Review.mp3",
    6: "Part06_Physical_Assessment_Setting_Tools_Inspection_Palpation.mp3",
    7: "Part07_Percussion_Auscultation.mp3",
    8: "Part08_Vital_Signs_Temperature.mp3",
    9: "Part09_Vital_Signs_Pulse.mp3",
    10: "Part10_Vital_Signs_Respiration_Breathing_Patterns.mp3",
    11: "Part11_Vital_Signs_Blood_Pressure.mp3",
    12: "Part12_Respiratory_System_How_Breathing_Works.mp3",
    13: "Part13_Respiratory_Assessment_History_Red_Flags_General_Exam.mp3",
    14: "Part14_Respiratory_Assessment_Examining_The_Chest.mp3",
    15: "Part15_Cardiovascular_Assessment_Prep_Inspection_Palpation.mp3",
    16: "Part16_Cardiovascular_Assessment_Heart_Sounds_Murmurs_Peripheral.mp3",
    17: "Part17_Abdominal_Assessment_Map_History_Signs_Outside.mp3",
    18: "Part18_Abdominal_Assessment_Prep_Inspection_Auscultation.mp3",
    19: "Part19_Abdominal_Assessment_Percussion_Palpation_Special_Signs.mp3",
    20: "Part20_Genitourinary_System_Anatomy_Functions_Signs.mp3",
    21: "Part21_Genitourinary_Assessment_History_Exam_Urinalysis.mp3",
    22: "Part22_Fire_Round.mp3",
}

# Pronunciation Dictionary (26 mandated phonetic replacements + clinical variants)
PRONUNCIATION_MAP = [
    # Compound / multi-word terms first
    (re.compile(r"\bcondylomata\s+acuminata\b", re.IGNORECASE), "kon-dih-LOH-muh-tuh uh-kyoo-mih-NAH-tuh"),
    (re.compile(r"\bcaput\s+medusae\b", re.IGNORECASE), "KAP-ut meh-DOO-see"),
    (re.compile(r"\bKayser-Fleischer\b", re.IGNORECASE), "KY-zer FLY-sher"),
    (re.compile(r"\bPeutz-Jeghers\b", re.IGNORECASE), "POOTS JAY-gurz"),
    (re.compile(r"\bHering-Breuer\b", re.IGNORECASE), "HAIR-ing BROY-er"),
    (re.compile(r"\bCheyne-Stokes\b", re.IGNORECASE), "chain stokes"),
    (re.compile(r"\bBiot's\b", re.IGNORECASE), "bee-OH's"),
    (re.compile(r"\bBiot\b", re.IGNORECASE), "bee-OH"),
    (re.compile(r"\bBitot's\b", re.IGNORECASE), "bee-TOH's"),
    (re.compile(r"\bBitot\b", re.IGNORECASE), "bee-TOH"),
    (re.compile(r"\bKussmaul's\b", re.IGNORECASE), "KOOS-mowl's"),
    (re.compile(r"\bKussmaul\b", re.IGNORECASE), "KOOS-mowl"),
    (re.compile(r"\bborborygmi\b", re.IGNORECASE), "bor-bor-IG-my"),
    (re.compile(r"\bRovsing's\b", re.IGNORECASE), "ROV-sing's"),
    (re.compile(r"\bRovsing\b", re.IGNORECASE), "ROV-sing"),
    (re.compile(r"\bBuerger's\b", re.IGNORECASE), "BUR-ger's"),
    (re.compile(r"\bBuerger\b", re.IGNORECASE), "BUR-ger"),
    (re.compile(r"\bPeyronie's\b", re.IGNORECASE), "pay-roh-NEE's"),
    (re.compile(r"\bPeyronie\b", re.IGNORECASE), "pay-roh-NEE"),
    (re.compile(r"\bxanthelasma\b", re.IGNORECASE), "zan-thuh-LAZ-muh"),
    (re.compile(r"\bkoilonychia\b", re.IGNORECASE), "koy-loh-NIK-ee-uh"),
    (re.compile(r"\bleukonychia\b", re.IGNORECASE), "loo-koh-NIK-ee-uh"),
    (re.compile(r"\basterixis\b", re.IGNORECASE), "as-ter-IK-sis"),
    (re.compile(r"\bkwashiorkor\b", re.IGNORECASE), "kwash-ee-OR-kor"),
    (re.compile(r"\bhaemoptysis\b", re.IGNORECASE), "hee-MOP-tih-sis"),
    (re.compile(r"\bdyspnoea\b", re.IGNORECASE), "DISP-nee-uh"),
    (re.compile(r"\borthopnoea\b", re.IGNORECASE), "or-THOP-nee-uh"),
    (re.compile(r"\boedematous\b", re.IGNORECASE), "ih-DEM-uh-tus"),
    (re.compile(r"\boedema\b", re.IGNORECASE), "ih-DEE-muh"),
    (re.compile(r"\bpyrosis\b", re.IGNORECASE), "pie-ROH-sis"),
    (re.compile(r"\beructation\b", re.IGNORECASE), "ee-ruk-TAY-shun"),
    (re.compile(r"\bhypospadias\b", re.IGNORECASE), "hy-poh-SPAY-dee-us"),
    (re.compile(r"\bHomans's\b", re.IGNORECASE), "HOH-muns's"),
    (re.compile(r"\bHomans'\b", re.IGNORECASE), "HOH-muns'"),
    (re.compile(r"\bHomans\b", re.IGNORECASE), "HOH-muns"),
    (re.compile(r"\bG-I\b", re.IGNORECASE), "G I"),
    (re.compile(r"\be-G-F-R\b", re.IGNORECASE), "E G F R"),
    (re.compile(r"\beGFR\b", re.IGNORECASE), "E G F R"),
]


def apply_pronunciation(text: str) -> str:
    """Applies pronunciation respellings to text sent to the TTS engine."""
    res = text
    for pattern, replacement in PRONUNCIATION_MAP:
        res = pattern.sub(replacement, res)
    return res


def parse_script(file_path: Path):
    """
    Parses Health_Assessment_Audio_Tutor_Script.md into 22 distinct parts.
    Strips top instruction block, # lines, and --- separators.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Script file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Locate part headings: ## PART <n> of 22. <Title>
    part_matches = list(re.finditer(r"^##\s*PART\s+(\d+)\s+of\s+22[.:]?\s*(.*)$", content, flags=re.MULTILINE))
    if len(part_matches) != 22:
        raise ValueError(f"Expected exactly 22 parts, but found {len(part_matches)}")

    parts = []
    for i, match in enumerate(part_matches):
        part_num = int(match.group(1))
        title = match.group(2).strip()
        start = match.end()
        end = part_matches[i + 1].start() if i + 1 < len(part_matches) else len(content)
        raw_section = content[start:end]

        # Break into paragraphs
        raw_paras = re.split(r"\n\s*\n", raw_section)
        clean_paras = []
        for p in raw_paras:
            p_strip = p.strip()
            if not p_strip:
                continue
            # Remove any line starting with # or ---
            lines = [line.strip() for line in p_strip.split("\n")]
            lines = [line for line in lines if not line.startswith("#") and line != "---"]
            cleaned_para = " ".join(lines).strip()
            if cleaned_para:
                clean_paras.append(cleaned_para)

        word_count = sum(len(p.split()) for p in clean_paras)
        parts.append({
            "part_num": part_num,
            "title": title,
            "paragraphs": clean_paras,
            "word_count": word_count,
            "filename": PART_FILENAMES.get(part_num, f"Part{part_num:02d}.mp3")
        })

    return parts


async def synthesize_chunk(text: str, voice: str, rate: str, output_path: str, retries: int = 3):
    """Synthesizes a chunk of text using edge-tts with automatic retry."""
    import edge_tts

    for attempt in range(1, retries + 1):
        try:
            communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
            await communicate.save(output_path)
            # Verify file exists and is not empty
            if os.path.exists(output_path) and os.path.getsize(output_path) > 100:
                return True
        except Exception as e:
            if attempt == retries:
                raise RuntimeError(f"TTS synthesis failed after {retries} attempts: {e}")
            await asyncio.sleep(1.0 * attempt)
    return False


async def produce_part_audio(part_data: dict, voice: str, rate: str, temp_dir: Path) -> Path:
    """
    Synthesizes each paragraph in a part, applies exact silences,
    and returns path to concatenated raw audio.
    """
    part_num = part_data["part_num"]
    paras = part_data["paragraphs"]
    part_temp_dir = temp_dir / f"part_{part_num:02d}"
    part_temp_dir.mkdir(parents=True, exist_ok=True)

    print(f"--> Building Part {part_num:02d} ({len(paras)} paragraphs, {part_data['word_count']} words)...")

    audio_segments = []
    # Concurrency semaphore to prevent hammering the network
    sem = asyncio.Semaphore(4)

    async def process_para(idx: int, para_text: str):
        async with sem:
            spoken_text = apply_pronunciation(para_text)
            para_path = part_temp_dir / f"para_{idx:03d}.mp3"
            await synthesize_chunk(spoken_text, voice, rate, str(para_path))
            return idx, para_path

    tasks = [process_para(i, p) for i, p in enumerate(paras)]
    results = await asyncio.gather(*tasks)
    results.sort(key=lambda x: x[0])

    for idx, para_path in results:
        para_text = paras[idx]
        seg = AudioSegment.from_file(str(para_path), format="mp3")
        audio_segments.append(seg)

        # Determine silence following this paragraph
        # Rules:
        # - Between paragraphs: 0.6 seconds (600ms)
        # - After "Pause and answer": 3 seconds (3000ms)
        # - After "Question N." in Part 22: 3 seconds (3000ms)
        # - Between a heading-level topic change: 1 second (1000ms)
        is_last = (idx == len(paras) - 1)
        if not is_last:
            if para_text.lower().startswith("pause and answer"):
                silence_ms = 3000
            elif part_num == 22 and re.match(r"^Question\s+\d+", para_text, re.IGNORECASE):
                silence_ms = 3000
            elif para_text.startswith("Recap.") or para_text.startswith("Next,"):
                silence_ms = 1000
            else:
                silence_ms = 600

            audio_segments.append(AudioSegment.silent(duration=silence_ms))

    # Add 400ms intro silence and 500ms trailing silence
    combined = AudioSegment.silent(duration=400)
    for s in audio_segments:
        combined += s
    combined += AudioSegment.silent(duration=500)

    raw_part_path = part_temp_dir / f"raw_part_{part_num:02d}.mp3"
    combined.export(str(raw_part_path), format="mp3", bitrate="192k")
    return raw_part_path


def normalize_loudness(input_path: Path, output_path: Path, target_lufs: float = -16.0):
    """
    Normalizes audio loudness to target LUFS (-16 LUFS) with mono 192kbps MP3 output using FFmpeg.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-af", f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11",
        "-ar", "44100",
        "-ac", "1",
        "-b:a", "192k",
        str(output_path)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg normalization failed:\n{res.stderr}")


def get_audio_duration_seconds(file_path: Path) -> float:
    """Returns audio duration in seconds using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        return float(res.stdout.strip())
    except Exception:
        # Fallback to pydub if ffprobe has an issue
        seg = AudioSegment.from_file(str(file_path))
        return len(seg) / 1000.0


def create_full_combined(part_files: list, output_path: Path, silence_between_parts_ms: int = 2000):
    """Concatenates all 22 normalized part files with 2 seconds silence between parts."""
    print(f"--> Combining {len(part_files)} parts into {output_path.name}...")
    full_audio = AudioSegment.empty()
    sep_silence = AudioSegment.silent(duration=silence_between_parts_ms)

    for i, pf in enumerate(part_files):
        seg = AudioSegment.from_file(str(pf), format="mp3")
        full_audio += seg
        if i < len(part_files) - 1:
            full_audio += sep_silence

    temp_combined = output_path.parent / "temp_full.mp3"
    full_audio.export(str(temp_combined), format="mp3", bitrate="192k")
    normalize_loudness(temp_combined, output_path, target_lufs=-16.0)
    if temp_combined.exists():
        temp_combined.unlink()


def format_duration(seconds: float) -> str:
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"


async def main():
    parser = argparse.ArgumentParser(description="Health Assessment Audio Tutor Build Tool")
    parser.add_argument("--part", type=int, help="Build a single part by index (1 to 22)")
    parser.add_argument("--all", action="store_true", help="Build all 22 parts and full combined audio")
    parser.add_argument("--voice", type=str, default=DEFAULT_VOICE, help="Edge-TTS voice identifier")
    parser.add_argument("--rate", type=str, default=DEFAULT_RATE, help="Speech rate adjustment (e.g. -4%)")
    parser.add_argument("--verify-only", action="store_true", help="Parse script and print breakdown without synthesis")
    args = parser.parse_args()

    parts = parse_script(SCRIPT_PATH)
    total_words = sum(p["word_count"] for p in parts)
    print(f"=== Health Assessment Audio Tutor Pipeline ===")
    print(f"Engine: Microsoft Edge Neural TTS (edge-tts)")
    print(f"Voice: {args.voice} (Pace: {args.rate})")
    print(f"Total parts parsed: {len(parts)} | Total words: {total_words}")

    if args.verify_only:
        print("\n--- Parsed Parts Overview ---")
        for p in parts:
            est_min = p["word_count"] / 150.0
            print(f"Part {p['part_num']:02d}: {p['title']} ({p['word_count']} words, ~{est_min:.1f} mins) -> {p['filename']}")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)

        targets = []
        if args.part:
            target = next((p for p in parts if p["part_num"] == args.part), None)
            if not target:
                print(f"Error: Part {args.part} not found.")
                sys.exit(1)
            targets = [target]
        else:
            targets = parts

        results = []
        for p in targets:
            raw_path = await produce_part_audio(p, args.voice, args.rate, temp_dir)
            out_file = OUTPUT_DIR / p["filename"]
            print(f"--> Normalizing loudness to -16 LUFS: {out_file.name}")
            normalize_loudness(raw_path, out_file, target_lufs=-16.0)

            dur_sec = get_audio_duration_seconds(out_file)
            expected_sec = (p["word_count"] / 150.0) * 60.0
            diff_ratio = abs(dur_sec - expected_sec) / expected_sec if expected_sec > 0 else 0
            flagged = diff_ratio > 0.25

            results.append({
                "part_num": p["part_num"],
                "filename": p["filename"],
                "title": p["title"],
                "word_count": p["word_count"],
                "duration_sec": dur_sec,
                "expected_sec": expected_sec,
                "diff_ratio": diff_ratio,
                "flagged": flagged
            })

        # If building all parts, compile full master
        if args.all and len(targets) == 22:
            full_master = OUTPUT_DIR / "Health_Assessment_FULL.mp3"
            part_files = [OUTPUT_DIR / p["filename"] for p in parts]
            create_full_combined(part_files, full_master, silence_between_parts_ms=2000)
            full_dur = get_audio_duration_seconds(full_master)
            print(f"--> Health_Assessment_FULL.mp3 created! Total runtime: {format_duration(full_dur)}")

        # Build Quality Report Markdown
        report_path = OUTPUT_DIR / "build_report.md"
        total_actual_sec = sum(r["duration_sec"] for r in results)

        report_lines = [
            "# Health Assessment Audio Tutor — Build Quality Report\n",
            f"- **Engine**: Microsoft Edge Neural TTS (`edge-tts`)",
            f"- **Voice**: `{args.voice}`",
            f"- **Pace Adjustment**: `{args.rate}`",
            f"- **Total Runtime (Individual Parts)**: {format_duration(total_actual_sec)}",
            f"- **Loudness Normalization**: -16 LUFS (mono, 192 kbps)\n",
            "## Quality Check Summary Table\n",
            "| Part | Title | Words | Expected | Actual | Variance | Status |",
            "|---|---|---|---|---|---|---|",
        ]

        for r in results:
            var_pct = f"{r['diff_ratio'] * 100:.1f}%"
            status = "⚠️ FLAGGED (>25%)" if r["flagged"] else "✅ PASS"
            report_lines.append(
                f"| Part {r['part_num']:02d} | {r['title']} | {r['word_count']} | {format_duration(r['expected_sec'])} | {format_duration(r['duration_sec'])} | {var_pct} | {status} |"
            )

        report_md = "\n".join(report_lines)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_md)

        print("\n" + report_md)


if __name__ == "__main__":
    asyncio.run(main())
