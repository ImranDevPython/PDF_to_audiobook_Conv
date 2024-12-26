import os
import PyPDF2
from gtts import gTTS
import pyttsx3
from langdetect import detect
import nltk
from tqdm import tqdm
import time

def normalize_pdf_path(path):
    """
    Normalize the PDF file path:
    1. Convert backslashes to forward slashes
    2. Add .pdf extension if missing
    3. Return absolute path
    
    Args:
        path (str): Input file path
    Returns:
        str: Normalized file path
    """
    # Convert backslashes to forward slashes
    normalized_path = path.replace('\\', '/')
    
    # Add .pdf extension if missing
    if not normalized_path.lower().endswith('.pdf'):
        normalized_path += '.pdf'
    
    # Convert to absolute path
    normalized_path = os.path.abspath(normalized_path)
    
    return normalized_path

class PDFToAudioConverter:
    def __init__(self):
        # Download necessary NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        # Initialize offline TTS engine as backup
        self.offline_engine = pyttsx3.init()
        
    def extract_text_from_pdf(self, pdf_path, page_range=None):
        """
        Extract text from PDF file with proper handling of formatting.
        
        Args:
            pdf_path (str): Path to the PDF file
            page_range (tuple): Optional tuple of (start_page, end_page) for specific pages
        """
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                # Determine page range
                if page_range:
                    start_page = max(0, page_range[0] - 1)  # Convert to 0-based index
                    end_page = min(total_pages, page_range[1])
                    pages_to_process = range(start_page, end_page)
                else:
                    pages_to_process = range(total_pages)
                
                for page_num in tqdm(pages_to_process, desc="Extracting text"):
                    text += pdf_reader.pages[page_num].extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")

    def preprocess_text(self, text):
        """Clean and preprocess text for better audio conversion."""
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Split into sentences for better pacing
        sentences = nltk.sent_tokenize(text)
        
        # Join sentences with proper spacing
        processed_text = ' '.join(sentences)
        return processed_text

    def detect_language(self, text):
        """Detect the language of the text."""
        try:
            return detect(text)
        except:
            return 'en'  # Default to English if detection fails

    def convert_to_audio(self, text, output_path, language='en', use_offline=False):
        """Convert text to audio using either gTTS (online) or pyttsx3 (offline)."""
        try:
            if not use_offline:
                # Online conversion using gTTS
                tts = gTTS(text=text, lang=language, slow=False)
                tts.save(output_path)
            else:
                # Offline conversion using pyttsx3
                self.offline_engine.save_to_file(text, output_path)
                self.offline_engine.runAndWait()
            return True
        except Exception as e:
            print(f"Error in conversion: {str(e)}")
            return False

    def convert_pdf_to_audiobook(self, pdf_path, output_dir="audio_output", page_range=None):
        """
        Main method to convert PDF to audiobook.
        
        Args:
            pdf_path (str): Path to the PDF file
            output_dir (str): Directory to save the audio file
            page_range (tuple): Optional tuple of (start_page, end_page) for specific pages
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract base name of PDF for output file
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        # Add page range to output filename if specified
        if page_range:
            output_path = os.path.join(output_dir, f"{base_name}_pages_{page_range[0]}-{page_range[1]}.mp3")
        else:
            output_path = os.path.join(output_dir, f"{base_name}.mp3")
        
        print("Starting conversion process...")
        
        # Extract text from PDF
        text = self.extract_text_from_pdf(pdf_path, page_range)
        
        # Preprocess the text
        processed_text = self.preprocess_text(text)
        
        # Detect language
        language = self.detect_language(processed_text)
        print(f"Detected language: {language}")
        
        # Try online conversion first, fall back to offline if needed
        print("Converting to audio...")
        success = self.convert_to_audio(processed_text, output_path, language)
        
        if not success:
            print("Online conversion failed. Falling back to offline conversion...")
            success = self.convert_to_audio(processed_text, output_path, language, use_offline=True)
        
        if success:
            print(f"Conversion complete! Audio saved to: {output_path}")
        else:
            print("Conversion failed. Please try again.")

if __name__ == "__main__":
    # Example usage
    converter = PDFToAudioConverter()
    
    # Get PDF path from user and normalize it
    pdf_path = input("Enter the path to your PDF file: ")
    pdf_path = normalize_pdf_path(pdf_path)
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        print("Error: File does not exist!")
        exit(1)
        
    # Get page range preference
    choice = input("Do you want to convert:\n1. Entire PDF\n2. Specific pages\nEnter your choice (1 or 2): ")
    
    page_range = None
    if choice == "2":
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                print(f"\nTotal pages in PDF: {total_pages}")
                
                while True:
                    try:
                        start_page = int(input(f"Enter start page (1-{total_pages}): "))
                        end_page = int(input(f"Enter end page (1-{total_pages}): "))
                        
                        if 1 <= start_page <= end_page <= total_pages:
                            page_range = (start_page, end_page)
                            break
                        else:
                            print("Invalid page range. Please try again.")
                    except ValueError:
                        print("Please enter valid numbers.")
        except Exception as e:
            print(f"Error reading PDF: {str(e)}")
            exit(1)
    
    # Convert PDF to audiobook
    converter.convert_pdf_to_audiobook(pdf_path, page_range=page_range)
