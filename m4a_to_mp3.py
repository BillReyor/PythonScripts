import os
import subprocess
from mutagen.mp4 import MP4, MP4Cover
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TRCK, TDRC, TCON, APIC, Encoding

def convert_m4a_to_mp3(file_path):
    """
    Converts an M4A file to MP3 format using FFmpeg.

    Args:
    file_path (str): The file path of the M4A file to be converted.

    Returns:
    str: The file path of the converted MP3 file.
    """
    mp3_file = file_path.rsplit('.', 1)[0] + '.mp3'
    subprocess.run(['ffmpeg', '-y', '-i', file_path, '-acodec', 'libmp3lame', '-q:a', '2', mp3_file])
    return mp3_file

def copy_metadata_with_artwork(m4a_file, mp3_file):
    """
    Copies metadata and embedded artwork from an M4A file to an MP3 file.

    Args:
    m4a_file (str): The file path of the source M4A file.
    mp3_file (str): The file path of the target MP3 file.
    """
    m4a_tags = MP4(m4a_file)
    mp3_tags = MP3(mp3_file, ID3=ID3)

    # Mapping of M4A keys to MP3 ID3 frame classes
    tag_mapping = {
        "©nam": TIT2,  # Title
        "©ART": TPE1,  # Artist
        "©alb": TALB,  # Album
        "©day": TDRC,  # Year
        "trkn": TRCK,  # Track number
        "©gen": TCON,  # Genre
    }

    for m4a_key, FrameClass in tag_mapping.items():
        if m4a_key in m4a_tags and m4a_tags[m4a_key]:
            frame = FrameClass(encoding=Encoding.UTF8, text=[str(m4a_tags[m4a_key][0])])
            mp3_tags[frame.HashKey] = frame

    # Copy embedded artwork
    if 'covr' in m4a_tags:
        for cover in m4a_tags['covr']:
            mime = 'image/png' if cover.imageformat == MP4Cover.FORMAT_PNG else 'image/jpeg'
            apic_frame = APIC(encoding=3, mime=mime, type=3, desc='Cover', data=cover)
            mp3_tags[apic_frame.HashKey] = apic_frame
    
    mp3_tags.save()

def delete_file(file_path):
    """
    Deletes a file at the given file path.

    Args:
    file_path (str): The file path of the file to be deleted.
    """
    try:
        os.remove(file_path)
        print(f'Deleted {file_path}')
    except OSError as e:
        print(f"Error: {e.strerror}")

def remove_empty_folders(path):
    """
    Recursively removes empty folders from a specified directory.

    Args:
    path (str): The root directory path to start removing empty folders.
    """
    if not os.path.isdir(path):
        return

    files = os.listdir(path)
    if len(files):
        for f in files:
            fullpath = os.path.join(path, f)
            if os.path.isdir(fullpath):
                remove_empty_folders(fullpath)

    files = os.listdir(path)
    if len(files) == 0:
        print(f"Removing empty directory: {path}")
        os.rmdir(path)

def main(directory):
    """
    Main function to convert all M4A files to MP3, copy metadata, and remove empty folders.

    Args:
    directory (str): The root directory path to start the conversion process.
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file)
            if file.lower().endswith('.m4a'):
                print(f'Converting {full_path}...')
                mp3_path = convert_m4a_to_mp3(full_path)
                copy_metadata_with_artwork(full_path, mp3_path)
                delete_file(full_path)
                print(f'Converted to {mp3_path}')
            elif file.lower().endswith('.m4p'):
                delete_file(full_path)

    remove_empty_folders(directory)

if __name__ == "__main__":
    main('/Users/user/Desktop/Music')  # Replace with your directory path
