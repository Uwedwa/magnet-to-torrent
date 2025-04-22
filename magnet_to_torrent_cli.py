import sys
import os
import subprocess
import threading
import tempfile
import time
import shutil
import re
import zipfile
import urllib.request
import platform
import argparse

class ResourceExtractor:
    @staticmethod
    def get_aria2c_path():

        if getattr(sys, 'frozen', False):

            app_dir = os.path.dirname(sys.executable)
        else:

            app_dir = os.path.dirname(os.path.abspath(__file__))

        resources_dir = os.path.join(app_dir, "resources")
        if not os.path.exists(resources_dir):
            os.makedirs(resources_dir)

        system = platform.system().lower()
        if system == "windows":
            aria2c_name = "aria2c.exe"
        else:
            aria2c_name = "aria2c"

        aria2c_path = os.path.join(resources_dir, aria2c_name)

        if os.path.exists(aria2c_path):
            return aria2c_path

        try:
            if system == "windows":

                print("Downloading aria2c...")
                download_url = "https://github.com/aria2/aria2/releases/download/release-1.36.0/aria2-1.36.0-win-64bit-build1.zip"
                zip_path = os.path.join(resources_dir, "aria2c.zip")
                urllib.request.urlretrieve(download_url, zip_path)

                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    for file in zip_ref.namelist():
                        if file.endswith("aria2c.exe"):
                            zip_ref.extract(file, resources_dir)
                            extracted_path = os.path.join(resources_dir, file)

                            shutil.move(extracted_path, aria2c_path)

                            extracted_dir = os.path.dirname(extracted_path)
                            if os.path.exists(extracted_dir) and extracted_dir != resources_dir:
                                shutil.rmtree(extracted_dir)
                            break

                if os.path.exists(zip_path):
                    os.remove(zip_path)
                print("aria2c downloaded successfully.")

            else:

                try:
                    subprocess.run(["aria2c", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                    return "aria2c"  
                except (subprocess.SubprocessError, FileNotFoundError):
                    print("Error: aria2c not found. Please install aria2c using your package manager.")
                    print("For example: sudo apt install aria2 (Ubuntu/Debian) or brew install aria2 (macOS)")
                    return None

            if os.path.exists(aria2c_path):
                return aria2c_path

        except Exception as e:
            print(f"Error extracting aria2c: {str(e)}")
            return None

        return None

def convert_magnet_to_torrent(magnet, output_path, verbose=False):
    """Convert a magnet link to a torrent file"""

    aria2c_path = ResourceExtractor.get_aria2c_path()
    if not aria2c_path:
        print("Error: Could not find or download aria2c. Please check your internet connection.")
        return False

    name = "download"
    if "dn=" in magnet:
        match = re.search(r"dn=([^&]+)", magnet)
        if match:
            name = match.group(1).replace("+", " ")

    temp_dir = tempfile.mkdtemp()

    try:

        output_dir = os.path.dirname(os.path.abspath(output_path))
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        print("Starting aria2c to download metadata...")

        cmd = [
            aria2c_path,
            "--dir=" + temp_dir,
            "--bt-metadata-only=true",
            "--bt-save-metadata=true",
            "--follow-torrent=mem",
            magnet
        ]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            if verbose:
                print(line)

            if "Download complete" in line:
                if verbose:
                    print("Metadata download complete. Finding torrent file...")
                break

        process.wait()

        if process.returncode != 0:
            print(f"Error: aria2c process failed with return code {process.returncode}")
            return False

        torrent_files = [f for f in os.listdir(temp_dir) if f.endswith('.torrent')]
        if not torrent_files:
            print("Error: No torrent file was created. The magnet link may be invalid.")
            return False

        torrent_path = os.path.join(temp_dir, torrent_files[0])

        if os.path.isdir(output_path):
            output_path = os.path.join(output_path, f"{name}.torrent")

        print(f"Saving torrent to {output_path}...")
        shutil.copy2(torrent_path, output_path)

        print(f"Success: Torrent file created at {output_path}")
        return True

    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return False

    finally:

        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except Exception as e:
            if verbose:
                print(f"Warning: Could not clean up temporary directory: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Convert magnet links to torrent files')
    parser.add_argument('magnet', help='The magnet link to convert (must start with "magnet:")')
    parser.add_argument('-o', '--output', help='Output path for the torrent file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed progress information')

    args = parser.parse_args()

    if not args.magnet.startswith('magnet:'):
        print("Error: Invalid magnet URL format. Must start with 'magnet:'")
        sys.exit(1)

    default_name = "download.torrent"
    if "dn=" in args.magnet:
        try:
            match = re.search(r"dn=([^&]+)", args.magnet)
            if match:
                default_name = match.group(1).replace("+", " ") + ".torrent"
        except:
            pass

    output_path = args.output if args.output else default_name

    if not output_path.endswith('.torrent'):
        output_path += '.torrent'

    success = convert_magnet_to_torrent(args.magnet, output_path, args.verbose)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()