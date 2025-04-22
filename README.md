# Magnet to Torrent Converter

A simple, user-friendly desktop application that allows you to convert magnet links to .torrent files.

![Magnet to Torrent Converter](https://placehold.co/600x300?text=Magnet+to+Torrent+Converter)

## Features

- Convert magnet links to .torrent files with a simple GUI
- Automatically extracts torrent name from magnet links when available
- Windows compatibility
- Embedded aria2c for reliable metadata extraction
- Progress tracking during conversion
- No installation needed (portable application)

## Requirements

- Python 3.6 or higher
- PyQt5
- Internet connection (for first-time setup to download aria2c)

## Installation

### Option 1: From Source

1. Clone this repository:
```
git clone https://github.com/yourusername/magnet-to-torrent.git
```

2. Install required dependencies:
```
pip install PyQt5
```

3. Run the application:
```
python magnet_to_torrent.py
```

### Option 2: Pre-built Binary for Windows

A pre-built binary for Windows is available in the [releases](https://github.com/yourusername/magnet-to-torrent/releases) section.

## Usage

1. Launch the application
2. Paste a magnet link in the "Magnet URL" field
3. Choose an output location for the .torrent file or use the "Browse" button
4. Click "Convert" and wait for the process to complete
5. The application will notify you when the conversion is finished

## How It Works

The application uses aria2c to download the torrent metadata from the BitTorrent network based on the magnet link's information. Once the metadata is obtained, it's saved as a .torrent file to your specified location.

## Dependencies

- [PyQt5](https://pypi.org/project/PyQt5/) - For the graphical user interface
- [aria2c](https://aria2.github.io/) - For downloading torrent metadata (automatically downloaded by the application)

## Building from Source

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

## Contributing

Contributions are welcome! Here are some ways you can contribute:

1. Report bugs and issues
2. Suggest new features
3. Submit pull requests with code improvements
4. Improve documentation

Please ensure your code follows the project's coding style before submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is designed for legitimate use cases such as downloading legal torrents from magnet links. The authors are not responsible for any misuse of this software. Please respect copyright laws and only download content you have the right to access.

## Acknowledgements

- [aria2](https://aria2.github.io/) for providing the core functionality for metadata extraction
- [PyQt5](https://riverbankcomputing.com/software/pyqt/) for the GUI framework
