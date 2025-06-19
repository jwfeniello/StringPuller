#!/usr/bin/env python3
"""
StringPuller - Ultimate Puppeteer Audio Extractor
Comprehensive AC3 detection for Puppeteer's .sgb audio containers
Finds ALL AC3 streams including damaged/offset headers
"""

import os
import struct
from pathlib import Path

class StringPuller:
    def __init__(self):
        self.folder_path = None
        self.output_folder = None
        self.total_streams_found = 0
        self.total_files_processed = 0
    
    def comprehensive_ac3_detection(self, data, filename):
        """Ultra-comprehensive AC3 detection for Puppeteer"""
        streams = []
        data_len = len(data)
        
        print(f"      🎭 PUPPETEER AC3 scan: {data_len:,} bytes...")
        
        # Strategy 1: Perfect AC3 sync detection
        perfect_ac3_streams = self.find_perfect_ac3_streams(data)
        streams.extend(perfect_ac3_streams)
        
        # Strategy 2: Offset AC3 detection (headers with padding)
        offset_ac3_streams = self.find_offset_ac3_streams(data)
        streams.extend(offset_ac3_streams)
        
        # Strategy 3: AC3 frame pattern detection
        frame_ac3_streams = self.find_ac3_frame_patterns(data)
        streams.extend(frame_ac3_streams)
        
        # Strategy 4: Puppeteer container structure analysis
        container_ac3_streams = self.analyze_puppeteer_structure(data, filename)
        streams.extend(container_ac3_streams)
        
        # Strategy 5: Missing AC3 recovery (fill gaps)
        recovered_streams = self.recover_missing_ac3_streams(data, streams)
        streams.extend(recovered_streams)
        
        return streams
    
    def find_perfect_ac3_streams(self, data):
        """Find AC3 streams with perfect 0B 77 headers"""
        streams = []
        ac3_signature = b'\x0B\x77'
        
        print("         🎯 Perfect AC3 sync detection...")
        
        pos = 0
        found_count = 0
        
        while True:
            pos = data.find(ac3_signature, pos)
            if pos == -1:
                break
            
            # Validate AC3 header
            if self.validate_ac3_header(data, pos):
                stream_size = self.calculate_ac3_stream_size(data, pos)
                
                streams.append({
                    'method': 'perfect_ac3',
                    'start': pos,
                    'size': stream_size,
                    'confidence': 'high'
                })
                
                found_count += 1
                pos += stream_size if stream_size > 1000 else 1000
            else:
                pos += 1
        
        if found_count > 0:
            print(f"         ✅ Found {found_count} perfect AC3 streams")
        
        return streams
    
    def find_offset_ac3_streams(self, data):
        """Find AC3 streams that might be offset by padding"""
        streams = []
        
        print("         🔍 Offset AC3 detection...")
        
        # Look for AC3 patterns with up to 16 bytes of preceding padding
        found_count = 0
        
        for offset in range(1, 17):  # Check 1-16 byte offsets
            search_pos = offset
            
            while search_pos < len(data) - 16:
                # Look for potential AC3 after padding
                chunk = data[search_pos:search_pos + 16]
                
                for i in range(len(chunk) - 1):
                    if chunk[i] == 0x0B and chunk[i + 1] == 0x77:
                        actual_pos = search_pos + i
                        
                        if self.validate_ac3_header(data, actual_pos):
                            # Check if we haven't already found this stream
                            if not any(abs(s['start'] - actual_pos) < 100 for s in streams):
                                stream_size = self.calculate_ac3_stream_size(data, actual_pos)
                                
                                streams.append({
                                    'method': 'offset_ac3',
                                    'start': actual_pos,
                                    'size': stream_size,
                                    'confidence': 'medium',
                                    'offset': offset + i
                                })
                                
                                found_count += 1
                
                search_pos += 4096  # Jump in 4KB increments for speed
        
        if found_count > 0:
            print(f"         ✅ Found {found_count} offset AC3 streams")
        
        return streams
    
    def find_ac3_frame_patterns(self, data):
        """Find AC3 by analyzing frame patterns"""
        streams = []
        
        print("         📊 AC3 frame pattern analysis...")
        
        # AC3 frames have specific bit patterns
        # Look for repeated frame structures
        frame_candidates = []
        
        # Scan for potential AC3 frame starts
        for i in range(0, len(data) - 8, 2048):  # Every 2KB
            chunk = data[i:i + 8]
            
            # AC3 frames often start with specific patterns
            if len(chunk) >= 4:
                # Check for AC3-like patterns (not just 0B 77)
                if self.looks_like_ac3_frame(chunk):
                    frame_candidates.append(i)
        
        # Group nearby candidates into streams
        if frame_candidates:
            current_start = frame_candidates[0]
            frame_count = 1
            
            for i in range(1, len(frame_candidates)):
                gap = frame_candidates[i] - frame_candidates[i-1]
                
                if gap < 50000:  # 50KB - same stream
                    frame_count += 1
                else:
                    # Finalize current stream
                    if frame_count >= 3:  # At least 3 frames
                        stream_size = frame_candidates[i-1] + 10000 - current_start
                        
                        streams.append({
                            'method': 'frame_pattern',
                            'start': current_start,
                            'size': min(stream_size, len(data) - current_start),
                            'confidence': 'medium',
                            'frames': frame_count
                        })
                    
                    current_start = frame_candidates[i]
                    frame_count = 1
            
            # Don't forget last stream
            if frame_count >= 3:
                stream_size = len(data) - current_start
                streams.append({
                    'method': 'frame_pattern',
                    'start': current_start,
                    'size': stream_size,
                    'confidence': 'medium',
                    'frames': frame_count
                })
        
        if streams:
            print(f"         ✅ Found {len(streams)} frame pattern streams")
        
        return streams
    
    def analyze_puppeteer_structure(self, data, filename):
        """Analyze Puppeteer-specific container structure"""
        streams = []
        
        print("         🎭 Puppeteer container analysis...")
        
        # Look for Puppeteer-specific patterns
        puppeteer_markers = [
            b'RIFF', b'WAVE', b'DATA', b'SDAT',
            b'\x00\x00\x01\x00', b'\x00\x00\x02\x00',  # Potential size markers
            b'@G\x47\x40',  # Pattern we saw in working extraction
        ]
        
        structure_points = []
        
        for marker in puppeteer_markers:
            pos = 0
            while True:
                pos = data.find(marker, pos)
                if pos == -1:
                    break
                structure_points.append(pos)
                pos += len(marker)
        
        # Sort structure points
        structure_points.sort()
        
        # Extract regions between structure points
        for i in range(len(structure_points) - 1):
            start = structure_points[i]
            end = structure_points[i + 1]
            size = end - start
            
            # Only consider reasonable-sized chunks
            if 5000 < size < 50 * 1024 * 1024:  # 5KB to 50MB
                # Check if this chunk contains AC3-like data
                chunk_sample = data[start:start + min(1024, size)]
                if self.chunk_looks_like_ac3(chunk_sample):
                    streams.append({
                        'method': 'puppeteer_structure',
                        'start': start,
                        'size': size,
                        'confidence': 'medium'
                    })
        
        if streams:
            print(f"         ✅ Found {len(streams)} structure-based streams")
        
        return streams
    
    def recover_missing_ac3_streams(self, data, existing_streams):
        """Fill gaps to recover missing AC3 streams"""
        streams = []
        
        print("         🔧 Recovering missing AC3 streams...")
        
        # Sort existing streams by start position
        existing_streams.sort(key=lambda x: x['start'])
        
        # Look for large gaps between streams
        for i in range(len(existing_streams) - 1):
            current_end = existing_streams[i]['start'] + existing_streams[i]['size']
            next_start = existing_streams[i + 1]['start']
            gap_size = next_start - current_end
            
            # If there's a significant gap, extract it as potential AC3
            if gap_size > 50000:  # 50KB gap
                # Sample the gap to see if it looks like audio
                gap_sample = data[current_end:current_end + min(4096, gap_size)]
                
                if self.chunk_looks_like_ac3(gap_sample):
                    streams.append({
                        'method': 'gap_recovery',
                        'start': current_end,
                        'size': gap_size,
                        'confidence': 'low'
                    })
        
        # Also check for data before first stream and after last stream
        if existing_streams:
            # Before first stream
            first_start = existing_streams[0]['start']
            if first_start > 10000:  # At least 10KB before
                streams.append({
                    'method': 'pre_stream_recovery',
                    'start': 0,
                    'size': first_start,
                    'confidence': 'low'
                })
            
            # After last stream
            last_stream = existing_streams[-1]
            last_end = last_stream['start'] + last_stream['size']
            if len(data) - last_end > 10000:  # At least 10KB after
                streams.append({
                    'method': 'post_stream_recovery',
                    'start': last_end,
                    'size': len(data) - last_end,
                    'confidence': 'low'
                })
        
        if streams:
            print(f"         ✅ Recovered {len(streams)} missing streams")
        
        return streams
    
    def validate_ac3_header(self, data, pos):
        """Validate AC3 header at position"""
        if pos + 5 > len(data):
            return False
        
        # Check AC3 sync word
        if data[pos] != 0x0B or data[pos + 1] != 0x77:
            return False
        
        # Basic AC3 header validation
        try:
            # Check frame size (bytes 2-3)
            frame_size = ((data[pos + 2] & 0x3F) << 8) | data[pos + 3]
            if frame_size == 0 or frame_size > 3840:  # Max AC3 frame size
                return False
            
            # Check sample rate and bit rate codes
            sr_code = (data[pos + 4] & 0xC0) >> 6
            bsid = (data[pos + 5] & 0xF8) >> 3
            
            if sr_code > 3 or bsid > 16:
                return False
            
            return True
        except:
            return False
    
    def calculate_ac3_stream_size(self, data, start_pos):
        """Calculate AC3 stream size"""
        max_size = min(len(data) - start_pos, 50 * 1024 * 1024)  # Max 50MB
        
        # Try to find the end of the AC3 stream
        # Look for next AC3 sync or end of meaningful data
        current_pos = start_pos + 1000  # Skip first frame
        
        while current_pos < start_pos + max_size - 2:
            # Look for next AC3 sync
            if data[current_pos] == 0x0B and data[current_pos + 1] == 0x77:
                # Check if this is a new stream (large gap) or continuation
                gap = current_pos - start_pos
                if gap > 10 * 1024 * 1024:  # 10MB = probably new stream
                    return gap
            
            # Look for long runs of zeros (end of stream)
            if current_pos + 1000 < len(data):
                chunk = data[current_pos:current_pos + 1000]
                if chunk.count(0) > 900:  # 90% zeros
                    return current_pos - start_pos
            
            current_pos += 4096  # Jump in 4KB increments
        
        # Default: reasonable chunk size
        return min(max_size, 20 * 1024 * 1024)  # 20MB default
    
    def looks_like_ac3_frame(self, chunk):
        """Check if chunk looks like start of AC3 frame"""
        if len(chunk) < 4:
            return False
        
        # Check for various AC3-like patterns
        patterns = [
            b'\x0B\x77',  # Standard AC3
            b'\x77\x0B',  # Byte-swapped AC3
        ]
        
        for pattern in patterns:
            if chunk.startswith(pattern):
                return True
        
        # Check for high entropy (audio-like randomness)
        if len(chunk) >= 8:
            unique_bytes = len(set(chunk[:8]))
            if unique_bytes >= 6:  # Good variety of bytes
                return True
        
        return False
    
    def chunk_looks_like_ac3(self, chunk):
        """Check if a chunk contains AC3-like audio data"""
        if len(chunk) < 100:
            return False
        
        # Check for AC3 patterns within chunk
        if b'\x0B\x77' in chunk:
            return True
        
        # Check entropy
        byte_counts = [0] * 256
        for byte in chunk:
            byte_counts[byte] += 1
        
        # Calculate entropy
        entropy = 0
        for count in byte_counts:
            if count > 0:
                prob = count / len(chunk)
                entropy -= prob * (prob * 8)  # Simplified entropy
        
        # High entropy suggests audio/compressed data
        return entropy > 6
    
    def remove_overlapping_streams(self, streams):
        """Remove overlapping streams, prefer higher confidence"""
        if not streams:
            return []
        
        # Sort by confidence first, then by start position
        confidence_order = {'high': 3, 'medium': 2, 'low': 1}
        streams.sort(key=lambda x: (confidence_order.get(x.get('confidence', 'low'), 0), -x['start']), reverse=True)
        
        unique_streams = []
        
        for stream in streams:
            # Check for overlap with higher-confidence streams
            overlaps = False
            
            for existing in unique_streams:
                overlap_start = max(stream['start'], existing['start'])
                overlap_end = min(stream['start'] + stream['size'], existing['start'] + existing['size'])
                overlap_size = max(0, overlap_end - overlap_start)
                
                # If >30% overlap, consider it duplicate
                overlap_ratio = overlap_size / min(stream['size'], existing['size'])
                if overlap_ratio > 0.3:
                    overlaps = True
                    break
            
            if not overlaps:
                unique_streams.append(stream)
        
        return unique_streams
    
    def extract_puppeteer_ac3_file(self, file_path):
        """Extract all AC3 streams from a Puppeteer .sgb file"""
        filename = Path(file_path).name
        print(f"🎭 EXTRACTING: {filename}")
        print("=" * 60)
        
        # Load file
        with open(file_path, 'rb') as f:
            data = f.read()
        
        file_size = len(data)
        print(f"📏 File size: {file_size:,} bytes ({file_size / 1024 / 1024:.1f} MB)")
        
        # Comprehensive AC3 detection
        all_streams = self.comprehensive_ac3_detection(data, filename)
        
        if not all_streams:
            print("      ❌ No AC3 streams found")
            return 0
        
        # Remove overlaps
        unique_streams = self.remove_overlapping_streams(all_streams)
        
        print(f"\n      💾 EXTRACTION SUMMARY")
        print(f"      Found {len(all_streams)} total streams")
        print(f"      Extracting {len(unique_streams)} unique streams")
        print()
        
        # Extract streams
        extracted_count = 0
        
        for i, stream in enumerate(unique_streams, 1):
            try:
                # Extract data
                start = stream['start']
                size = stream['size']
                stream_data = data[start:start + size]
                
                # Generate clean filename
                base_name = Path(filename).stem
                
                # Determine file type from base name
                file_type = ""
                if "bgm" in base_name.lower():
                    file_type = "music"
                elif "amb" in base_name.lower():
                    file_type = "ambient"
                elif "demo" in base_name.lower():
                    file_type = "demo"
                elif "voice" in base_name.lower():
                    file_type = "voice"
                else:
                    file_type = "audio"
                
                # Clean, user-friendly filename
                output_filename = f"{base_name}_{i:02d}_{file_type}.ac3"
                output_file = self.output_folder / output_filename
                
                # Write file
                with open(output_file, 'wb') as f:
                    f.write(stream_data)
                
                size_mb = len(stream_data) / 1024 / 1024
                print(f"         ✅ {output_filename} ({size_mb:.1f} MB)")
                extracted_count += 1
                
            except Exception as e:
                print(f"         ❌ Failed to extract stream {i}: {e}")
        
        print(f"\n      🎉 Extracted {extracted_count} AC3 files!")
        return extracted_count
    
    def check_ffmpeg_available(self):
        """Check if ffmpeg is available"""
        try:
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def convert_ac3_to_wav(self, ac3_file, wav_file):
        """Convert single AC3 file to WAV using ffmpeg"""
        try:
            import subprocess
            cmd = [
                'ffmpeg', '-i', str(ac3_file), 
                '-acodec', 'pcm_s16le',  # 16-bit PCM
                '-ar', '44100',          # 44.1kHz sample rate
                '-y',                    # Overwrite output
                str(wav_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return result.returncode == 0
        except Exception as e:
            print(f"         ❌ Conversion failed: {e}")
            return False
    
    def offer_wav_conversion(self):
        """Offer to convert AC3 files to WAV"""
        print("🎵 WAV CONVERSION OPTION")
        print("-" * 40)
        
        # Check if ffmpeg is available
        if not self.check_ffmpeg_available():
            print("❌ FFmpeg not found!")
            print("💡 Install FFmpeg to enable WAV conversion:")
            print("   • Download from: https://ffmpeg.org/download.html")
            print("   • Add to PATH or place ffmpeg.exe in this folder")
            return
        
        print("✅ FFmpeg detected!")
        print("🎵 Convert AC3 files to WAV format for better compatibility?")
        print("   WAV files work in more audio editors and players")
        print()
        
        while True:
            choice = input("Convert to WAV? (y/n/h for help): ").lower().strip()
            
            if choice == 'h':
                print("\n💡 WAV Conversion Help:")
                print("   • WAV files are uncompressed (larger but higher quality)")
                print("   • Better compatibility with audio editors")
                print("   • AC3 files will be kept alongside WAV files")
                print("   • Each file takes 30-60 seconds to convert")
                print()
                continue
            
            elif choice in ['y', 'yes']:
                self.batch_convert_to_wav()
                break
                
            elif choice in ['n', 'no']:
                print("✅ Keeping AC3 format - perfect for media players!")
                break
                
            else:
                print("Please enter 'y' for yes, 'n' for no, or 'h' for help")
    
    def batch_convert_to_wav(self):
        """Convert all AC3 files to WAV"""
        print("\n🔄 CONVERTING AC3 TO WAV")
        print("=" * 40)
        
        # Find all AC3 files in output folder
        ac3_files = list(self.output_folder.glob("*.ac3"))
        
        if not ac3_files:
            print("❌ No AC3 files found to convert")
            return
        
        print(f"📋 Converting {len(ac3_files)} AC3 files to WAV...")
        print("⏱️  This may take several minutes...")
        print()
        
        # Create WAV subfolder
        wav_folder = self.output_folder / "wav_converted"
        wav_folder.mkdir(exist_ok=True)
        
        successful_conversions = 0
        failed_conversions = 0
        
        for i, ac3_file in enumerate(ac3_files, 1):
            # Generate WAV filename
            wav_filename = ac3_file.stem + ".wav"
            wav_file = wav_folder / wav_filename
            
            print(f"🔄 [{i}/{len(ac3_files)}] Converting: {ac3_file.name}")
            
            # Convert
            if self.convert_ac3_to_wav(ac3_file, wav_file):
                # Check if WAV file was created and has reasonable size
                if wav_file.exists() and wav_file.stat().st_size > 1000:
                    wav_size = wav_file.stat().st_size / 1024 / 1024
                    print(f"         ✅ Created: {wav_filename} ({wav_size:.1f} MB)")
                    successful_conversions += 1
                else:
                    print(f"         ❌ Conversion failed: Invalid output")
                    failed_conversions += 1
            else:
                print(f"         ❌ Conversion failed")
                failed_conversions += 1
        
        # Summary
        print(f"\n🎉 CONVERSION COMPLETE!")
        print(f"✅ Successful: {successful_conversions}")
        if failed_conversions > 0:
            print(f"❌ Failed: {failed_conversions}")
        print(f"📂 WAV files location: {wav_folder}")
        print()
        print("💡 You now have both AC3 and WAV versions!")
        print("   • AC3: Smaller, perfect for media players")
        print("   • WAV: Larger, perfect for audio editing")

    def get_folder_path(self):
        """Get the .sgb folder path from user"""
        print("STRINGPULLER - Puppeteer Audio Extractor")
        print("=" * 50)
        print()
        print("Please enter the path to your Puppeteer .sgb files.")
        print()
        print("Common locations:")
        print("  Windows: D:\\game\\NPUA80959\\USRDIR\\data\\sound\\stream")
        print("  or: C:\\Users\\YourName\\Desktop\\Puppeteer\\stream")
        print()
        print("You can also drag and drop the folder into this window.")
        print()
        
        while True:
            folder_path = input("Folder path: ").strip()
            
            # Remove quotes if user dragged folder
            folder_path = folder_path.strip('"').strip("'")
            
            if not folder_path:
                print("Please enter a folder path.")
                continue
            
            # Check if path exists
            if not os.path.exists(folder_path):
                print(f"Path not found: {folder_path}")
                print("Please check the path and try again.")
                continue
            
            # Check if it's a directory
            if not os.path.isdir(folder_path):
                print("Please enter a folder path, not a file.")
                continue
            
            # Check for .sgb files
            import glob
            sgb_files = glob.glob(os.path.join(folder_path, "*.sgb"))
            
            if not sgb_files:
                print(f"No .sgb files found in: {folder_path}")
                retry = input("Continue anyway? (y/n): ").lower()
                if retry in ['y', 'yes']:
                    break
                else:
                    continue
            else:
                print(f"Found {len(sgb_files)} .sgb files. Perfect!")
                break
        
        self.folder_path = folder_path
        print()

    def process_all_puppeteer_files(self):
        """Process all Puppeteer .sgb files"""
        # Get folder path from user
        self.get_folder_path()
        
        print("STRINGPULLER - PUPPETEER AUDIO EXTRACTOR")
        print("=" * 80)
        print(f"Target folder: {self.folder_path}")
        print("Comprehensive AC3 detection for ALL streams!")
        print()
        
        if not os.path.exists(self.folder_path):
            print(f"Error: Folder not found: {self.folder_path}")
            return
        
        # Get all .sgb files
        folder = Path(self.folder_path)
        sgb_files = [f for f in folder.iterdir() if f.suffix.lower() == '.sgb']
        
        if not sgb_files:
            print("No .sgb files found!")
            return
        
        print(f"Found {len(sgb_files)} .sgb files")
        print()
        
        # Create output folder
        self.output_folder = folder / "extracted_puppeteer_ac3"
        self.output_folder.mkdir(exist_ok=True)
        print(f"Output folder: {self.output_folder}")
        print()
        
        # Process each file
        for i, file_path in enumerate(sgb_files, 1):
            streams_extracted = self.extract_puppeteer_ac3_file(file_path)
            self.total_streams_found += streams_extracted
            self.total_files_processed += 1
            
            if i < len(sgb_files):
                print("\n" + "="*80 + "\n")
        
        # Final summary
        print("STRINGPULLER EXTRACTION COMPLETE!")
        print("=" * 80)
        print(f"StringPuller v1.0 - Puppeteer Audio Extractor")
        print(f"Files processed: {self.total_files_processed}")
        print(f"AC3 streams extracted: {self.total_streams_found}")
        print(f"Output folder: {self.output_folder}")
        print()
        
        # Optional WAV conversion
        if self.total_streams_found > 0:
            self.offer_wav_conversion()
        
        print("Your Puppeteer audio collection is ready!")
        print("Play files with VLC, Audacity, or any media player")

def main():
    extractor = StringPuller()
    
    try:
        extractor.process_all_puppeteer_files()
    except KeyboardInterrupt:
        print("\nExtraction cancelled!")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()