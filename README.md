# PDF to Audiobook Converter

A powerful Python application that converts PDF documents into audiobooks, featuring both a graphical user interface (GUI) and command-line interface (CLI). Created by [ImranDevPython](https://github.com/ImranDevPython).

## Features

- 📚 Convert entire PDFs or specific page ranges to audio
- 🎯 User-friendly GUI with modern design
- 👀 Live text preview functionality
- 🌐 Dual conversion modes: Online (gTTS) and Offline (pyttsx3)
- 🔤 Automatic language detection
- 📊 Progress tracking with status updates
- 🎨 Dark/Light theme toggle

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ImranDevPython/PDF_to_audiobook_Conv.git
cd PDF_to_audiobook_Conv
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### GUI Version

1. Run the GUI application:
```bash
python pdf_audiobook_gui.py
```

2. Using the GUI:
   - Click "Browse" to select your PDF file
   - Choose between converting the entire PDF or specific pages
   - For specific pages, enter the page range and use "Preview" to verify content
   - Click "Convert to Audio" to start the conversion
   - Monitor progress through the status bar and messages
   - Find the converted audio file in the `audio_output` directory

### Command Line Version

1. Run the command-line version:
```bash
python pdf_to_audio.py
```

2. Follow the prompts:
   - Enter the path to your PDF file
   - Choose between converting the entire PDF or specific pages
   - If selecting specific pages, enter the start and end page numbers
   - Wait for the conversion to complete

## Requirements

- Python 3.7+
- Required packages (automatically installed via requirements.txt):
  - customtkinter
  - PyPDF2
  - gTTS
  - pyttsx3
  - langdetect
  - nltk
  - tqdm

## File Structure

```
PDF_to_audiobook_Conv/
├── pdf_audiobook_gui.py   # GUI application
├── pdf_to_audio.py        # Core conversion logic & CLI
├── requirements.txt       # Package dependencies
└── audio_output/         # Generated audiobooks directory
```

## Troubleshooting

1. **No audio output**: 
   - Ensure the PDF contains actual text (not just scanned images)
   - Check if the PDF is not password protected
   - Verify you have internet connection for online conversion

2. **Conversion fails**: 
   - Try using specific page ranges instead of entire PDF
   - Check if the PDF is corrupted
   - Ensure all dependencies are properly installed

3. **Language issues**:
   - The app automatically detects the language
   - Falls back to English if detection fails
   - Supports multiple languages through gTTS

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Created by [ImranDevPython](https://github.com/ImranDevPython)

## Acknowledgments

- CustomTkinter for the modern GUI components
- gTTS and pyttsx3 for text-to-speech conversion
- PyPDF2 for PDF processing
