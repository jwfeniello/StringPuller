
![oupt](https://github.com/user-attachments/assets/c6a13a66-bd09-4b64-ae7f-8d1ce315c555)


[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-PS3-lightgrey.svg)](https://github.com)
[![License](https://img.shields.io/badge/License-Personal%20Use-green.svg)](https://github.com)

> **Audio extraction tool for Puppeteer (PS3) .sgb files**

---

## Overview

This tool extracts audio streams from Puppeteer's `.sgb` container files and converts them to **Dolby Digital AC3** format with optional **WAV** conversion support.

<details>
<summary><strong>What it does</strong></summary>

- Extracts audio streams from Puppeteer's `.sgb` container files
- Outputs to Dolby Digital AC3 format
- Optional WAV conversion with FFmpeg support  
- Organized file naming with audio type classification

</details>

---

## File Location

> **Note**  
> The `.sgb` files can be found in your Puppeteer game directory:

```bash
game/NPUA80959/USRDIR/data/sound/stream
```

---

## Requirements

| Component | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.6+ | Core functionality |
| **FFmpeg** | Latest *(optional)* | WAV conversion |

<details>
<summary><strong>Installation Instructions</strong></summary>

### Python 3.6+
- **Windows**: Download from [python.org](https://python.org)
- **macOS**: `brew install python3` or download from python.org
- **Linux**: `sudo apt install python3` or `sudo yum install python3`

### FFmpeg (Optional)
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` or `sudo yum install ffmpeg`

</details>

---

## Usage

**Step 1:** Run the extractor
```bash
python stringpuller.py
```

**Step 2:** Enter the path when prompted
```
*GAMEID*/USRDIR/data/sound/stream
```

---

## Output Structure

The tool creates an organized output directory structure:

```
extracted_puppeteer_ac3/
├── AC3 Files (Dolby Digital)
│   ├── filename_01_music.ac3
│   ├── filename_01_ambient.ac3
│   └── filename_01_demo.ac3
└── wav_converted/ (Optional)
    ├── filename_01_music.wav
    ├── filename_01_ambient.wav
    └── filename_01_demo.wav
```

### Audio Type Classification

<table>
<tr>
<th>File Pattern</th>
<th>Audio Type</th>
<th>Description</th>
</tr>
<tr>
<td><code>*_music.ac3</code></td>
<td><strong>Background Music</strong></td>
<td>Soundtrack and musical score</td>
</tr>
<tr>
<td><code>*_ambient.ac3</code></td>
<td><strong>Environmental</strong></td>
<td>Atmospheric sounds and ambient audio</td>
</tr>
<tr>
<td><code>*_demo.ac3</code></td>
<td><strong>Cutscenes</strong></td>
<td>Demo and narrative audio sequences</td>
</tr>
</table>

---

## Technical Details

<details>
<summary><strong>Supported Formats</strong></summary>

**Input:** `.sgb` (Puppeteer container files)  
**Output:** `.ac3` (Dolby Digital) + `.wav` (optional)

</details>

<details>
<summary><strong>Performance Notes</strong></summary>

- AC3 files maintain original audio quality
- WAV conversion provides broader compatibility
- Processing time varies with file size and system performance

</details>

---

## Troubleshooting

> **Warning**  
> Ensure you have read access to the Puppeteer game files

> **Tip**  
> AC3 files can be played directly in VLC, Windows Media Player, and most modern media players

---

## License

```
This tool is intended for personal use with legally owned copies of Puppeteer.
Audio content remains property of the original developers.
```

---

<div align="center">


</div>
