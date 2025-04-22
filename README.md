<div align="left" style="position: relative;">
<img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-markdown-open.svg" align="right" width="30%" style="margin: -20px 0 0 20px;">
<h1>MAGNET-TO-TORRENT</h1>

<p align="left">
  <a href="https://github.com/Uwedwa/magnet-to-torrent/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/Uwedwa/magnet-to-torrent?style=flat&logo=gnu&logoColor=white&color=0080ff" alt="license">
  </a>
  <img src="https://img.shields.io/github/last-commit/Uwedwa/magnet-to-torrent?style=flat&logo=git&logoColor=white&color=0080ff" alt="last-commit">
  <img src="https://img.shields.io/github/languages/top/Uwedwa/magnet-to-torrent?style=flat&color=0080ff" alt="repo-top-language">
<!--  <img src="https://img.shields.io/github/languages/count/Uwedwa/magnet-to-torrent?style=flat&color=0080ff" alt="repo-language-count">-->
  <img src="https://img.shields.io/github/repo-size/Uwedwa/magnet-to-torrent?style=flat&color=0080ff" alt="repo-size">
</p>


A simple, user-friendly desktop application that allows you to convert magnet links to .torrent files.


## 👾 Features

- Convert magnet links to .torrent files with a simple GUI
- Automatically extracts torrent name from magnet links when available
- Windows compatibility
- Embedded aria2c for reliable metadata extraction
- Progress tracking during conversion
- No installation needed (portable application)



## ☑️ Requirements
Before getting started with magnet-to-torrent, ensure your runtime environment meets the following requirements:
- Python 3.6 or higher
- PyQt5
- Internet connection (for first-time setup to download aria2c)

## ⚙️Installation

### 🖥️ Option 1: Pre-built Binary for Windows

A pre-built binary for Windows is available in the [releases](https://github.com/uwedwa/magnet-to-torrent/releases) section.

### 🔧 Option 2: **Build from source:**

1. Clone the magnet-to-torrent repository:
```sh
❯ git clone https://github.com/Uwedwa/magnet-to-torrent/
```

2. Navigate to the project directory:
```sh
❯ cd magnet-to-torrent
```

3. Run the application:
```
python magnet_to_torrent_***.py
```

## 🤖 Usage

1. Launch the application
2. Paste a magnet link in the "Magnet URL" field
3. Choose an output location for the .torrent file or use the "Browse" button
4. Click "Convert" and wait for the process to complete
5. The application will notify you when the conversion is finished

## 🧠 How It Works

The application uses aria2c to download the torrent metadata from the BitTorrent network based on the magnet link's information. Once the metadata is obtained, it's saved as a .torrent file to your specified location.

## 📦 Dependencies

- [PyQt5](https://pypi.org/project/PyQt5/) Python bindings for the Qt5 application framework, used to create graphical user interfaces.
- [PyQt5_sip](https://pypi.org/project/PyQt5-sip/) A required module for PyQt5 that provides support for binding C++ libraries to Python.
- [argparse](https://docs.python.org/3/library/argparse.html) A module for parsing command-line arguments, facilitating the creation of user-friendly CLI interfaces.
- [urllib3](https://pypi.org/project/urllib3/) A powerful HTTP client for Python, offering connection pooling, SSL/TLS verification, and retry logic.
- [shutil](https://docs.python.org/3/library/shutil.html) Provides high-level file operations such as copying and removal of files and directories.
- [zipfile](https://docs.python.org/3/library/zipfile.html) Enables reading and writing of ZIP archive files.
- [platform](https://docs.python.org/3/library/platform.html) Accesses underlying platform’s identifying data like OS name and version.
- [subprocess](https://docs.python.org/3/library/subprocess.html) Spawns new processes, connects to their I/O streams, and obtains return codes.
- [re](https://docs.python.org/3/library/re.html) Supports regular expression operations for advanced string matching.
- [requests](https://pypi.org/project/requests/) A user-friendly HTTP library built for making requests simpler and more human-readable.

## 🔧 Building from Source

To create a standalone executable:

1. Install PyInstaller:
```
pip install pyinstaller
```

2. Create the executable:
```
pyinstaller --onefile --windowed magnet_to_torrent.py
```

3. The executable will be created in the `dist` folder

## 🤝 Contributing

Contributions are welcome! Here are some ways you can contribute:

1. Report bugs and issues
2. Suggest new features
3. Submit pull requests with code improvements
4. Improve documentation

Please ensure your code follows the project's coding style before submitting pull requests.

## 🎗 License

This project is licensed under the **GNU GPL v3** - see the [LICENSE](LICENSE) file for details.

# ⚠️ Disclaimer

This tool is designed for legitimate use cases such as downloading legal torrents from magnet links. The authors are not responsible for any misuse of this software. Please respect copyright laws and only download content you have the right to access.

## 🙌 Acknowledgements

- [aria2](https://aria2.github.io/) for providing the core functionality for metadata extraction
- [PyQt5](https://riverbankcomputing.com/software/pyqt/) for the GUI framework
- [Readme-Ai](https://readme-ai.streamlit.app/) for README.md file
