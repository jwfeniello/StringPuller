![STING PULLER](https://github.com/user-attachments/assets/4bda3c31-721f-4eff-8ae5-6ff4ef333551)

Audio extraction tool for Puppeteer (PS3) .sgb files.

## What it does

Extracts audio streams from Puppeteer's .sgb container files to Dolby Digital AC3 format. Optional conversion to WAV if you have FFmpeg installed.

## File location

The .sgb files are located at:
```
game\NPUA80959\USRDIR\data\sound\stream
```

## Requirements

- Python 3.6+
- FFmpeg (optional, for WAV conversion)

## Usage

1. Run:
   python stringpuller.py
   ```

## Output

Creates `extracted_puppeteer_ac3/` folder with:
- AC3 files (native Dolby Digital format)
- Optional `wav_converted/` subfolder if you choose conversion

File names are organized by type:
- `filename_01_music.ac3` (background music)
- `filename_01_ambient.ac3` (environmental sounds) 
- `filename_01_demo.ac3` (demo audio)
