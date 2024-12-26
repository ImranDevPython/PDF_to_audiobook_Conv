import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import os
import threading
import PyPDF2
from pdf_to_audio import PDFToAudioConverter, normalize_pdf_path

class PDFAudiobookGUI:
    def __init__(self):
        """Initialize the GUI application"""
        self.app = ctk.CTk()
        self.app.title("PDF Audiobook Converter")
        self.app.geometry("800x600")
        self.current_theme = "dark"
        
        self.setup_ui()
        self.converter = PDFToAudioConverter()
        
    def setup_ui(self):
        """Setup the main UI components"""
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.app)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Theme toggle button
        self.theme_button = ctk.CTkButton(
            self.main_frame,
            text="Toggle Theme",
            command=self.toggle_theme,
            width=100
        )
        self.theme_button.pack(anchor="ne", padx=5, pady=5)
        
        # File selection
        self.file_frame = ctk.CTkFrame(self.main_frame)
        self.file_frame.pack(fill="x", padx=10, pady=5)
        
        self.file_label = ctk.CTkLabel(self.file_frame, text="No file selected")
        self.file_label.pack(side="left", padx=5)
        
        self.browse_button = ctk.CTkButton(
            self.file_frame,
            text="Browse",
            command=self.browse_file,
            width=100
        )
        self.browse_button.pack(side="right", padx=5)
        
        # Page Selection
        self.page_frame = ctk.CTkFrame(self.main_frame)
        self.page_frame.pack(fill="x", padx=10, pady=5)
        
        self.page_selection_var = tk.StringVar(value="entire")
        
        self.page_label = ctk.CTkLabel(self.page_frame, text="Page Selection:")
        self.page_label.pack(side="left", padx=5)
        
        self.entire_pdf_radio = ctk.CTkRadioButton(
            self.page_frame,
            text="Entire PDF",
            variable=self.page_selection_var,
            value="entire",
            command=self.toggle_page_selection
        )
        self.entire_pdf_radio.pack(side="left", padx=5)
        
        self.specific_pages_radio = ctk.CTkRadioButton(
            self.page_frame,
            text="Specific Pages",
            variable=self.page_selection_var,
            value="specific",
            command=self.toggle_page_selection
        )
        self.specific_pages_radio.pack(side="left", padx=5)
        
        # Page range entry
        self.page_range_frame = ctk.CTkFrame(self.page_frame)
        self.page_range_frame.pack(side="left", padx=5)
        
        self.start_page_var = tk.StringVar()
        self.end_page_var = tk.StringVar()
        
        self.start_page_entry = ctk.CTkEntry(
            self.page_range_frame,
            width=60,
            textvariable=self.start_page_var,
            placeholder_text="Start"
        )
        self.start_page_entry.pack(side="left", padx=2)
        
        self.page_range_label = ctk.CTkLabel(self.page_range_frame, text="to")
        self.page_range_label.pack(side="left", padx=2)
        
        self.end_page_entry = ctk.CTkEntry(
            self.page_range_frame,
            width=60,
            textvariable=self.end_page_var,
            placeholder_text="End"
        )
        self.end_page_entry.pack(side="left", padx=2)
        
        # Preview button for specific pages
        self.preview_button = ctk.CTkButton(
            self.page_range_frame,
            text="Preview",
            command=self.update_preview,
            width=70
        )
        self.preview_button.pack(side="left", padx=5)
        
        # Initially disable page range entries and preview button
        self.start_page_entry.configure(state="disabled")
        self.end_page_entry.configure(state="disabled")
        self.preview_button.configure(state="disabled")
        
        # Text preview
        self.preview_frame = ctk.CTkFrame(self.main_frame)
        self.preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.preview_label = ctk.CTkLabel(self.preview_frame, text="Text Preview:")
        self.preview_label.pack(anchor="w", padx=5, pady=5)
        
        self.preview_text = ctk.CTkTextbox(
            self.preview_frame,
            height=200,
            wrap="word",
            font=("TkDefaultFont", 12)
        )
        self.preview_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Progress frame
        self.progress_frame = ctk.CTkFrame(self.main_frame)
        self.progress_frame.pack(fill="x", padx=10, pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", padx=5, pady=5)
        self.progress_bar.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(self.progress_frame, text="")
        self.status_label.pack(pady=5)
        
        # Convert button
        self.convert_button = ctk.CTkButton(
            self.main_frame,
            text="Convert to Audio",
            command=self.start_conversion
        )
        self.convert_button.pack(pady=10)
        
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        ctk.set_appearance_mode(self.current_theme)
        
    def toggle_page_selection(self):
        """Enable/disable page range entries based on selection"""
        if self.page_selection_var.get() == "specific":
            self.start_page_entry.configure(state="normal")
            self.end_page_entry.configure(state="normal")
            self.preview_button.configure(state="normal")
        else:
            self.start_page_entry.configure(state="disabled")
            self.end_page_entry.configure(state="disabled")
            self.preview_button.configure(state="disabled")
            self.start_page_var.set("")
            self.end_page_var.set("")
            if hasattr(self, 'current_file'):
                self.update_preview()
                
    def validate_page_range(self):
        """Validate the entered page range"""
        if self.page_selection_var.get() == "entire":
            return None
            
        try:
            start = int(self.start_page_var.get())
            end = int(self.end_page_var.get())
            
            if not hasattr(self, 'total_pages'):
                return None
                
            if 1 <= start <= end <= self.total_pages:
                return (start, end)
            else:
                self.show_error(f"Invalid page range. Please enter values between 1 and {self.total_pages}")
                return None
        except ValueError:
            self.show_error("Please enter valid page numbers")
            return None
            
    def show_error(self, message):
        """Show error message"""
        self.status_label.configure(text=message, text_color="red")
        
    def show_status(self, message):
        """Show status message"""
        self.status_label.configure(text=message, text_color="white")
        
    def browse_file(self):
        """Open file dialog for PDF selection"""
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            file_path = normalize_pdf_path(file_path)
            self.current_file = file_path
            self.file_label.configure(text=os.path.basename(file_path))
            
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    self.total_pages = len(pdf_reader.pages)
                    
                    # Clear previous text
                    self.preview_text.delete("1.0", "end")
                    
                    # Get first page text
                    first_page = pdf_reader.pages[0].extract_text()
                    if first_page.strip():
                        self.preview_text.insert("1.0", first_page)
                        self.show_status(f"PDF loaded successfully. Total pages: {self.total_pages}")
                    else:
                        self.preview_text.insert("1.0", "No readable text found in the first page.")
                        self.show_status(f"PDF loaded. Total pages: {self.total_pages}. Warning: First page may be empty or contain images only.")
                    
                    self.preview_text.update()
                    self.app.update_idletasks()
                    
            except Exception as e:
                self.show_error(f"Error reading PDF: {str(e)}")
                self.preview_text.delete("1.0", "end")
                self.preview_text.insert("1.0", "Error loading preview.")
                return
                
    def update_preview(self):
        """Update preview based on current page selection"""
        if not hasattr(self, 'current_file'):
            return
            
        try:
            with open(self.current_file, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                if self.page_selection_var.get() == "specific":
                    try:
                        start_page = int(self.start_page_var.get())
                        if 1 <= start_page <= len(pdf_reader.pages):
                            page_num = start_page - 1
                        else:
                            self.show_error(f"Invalid page number. Please enter a number between 1 and {len(pdf_reader.pages)}")
                            return
                    except ValueError:
                        self.show_error("Please enter a valid page number")
                        return
                else:
                    page_num = 0
                
                self.preview_text.delete("1.0", "end")
                page_text = pdf_reader.pages[page_num].extract_text()
                
                if page_text.strip():
                    self.preview_text.insert("1.0", page_text)
                    self.show_status(f"Showing preview of page {page_num + 1}")
                else:
                    self.preview_text.insert("1.0", f"No readable text found on page {page_num + 1}")
                    self.show_status(f"Warning: Page {page_num + 1} may be empty or contain images only")
                
                self.preview_text.update()
                self.app.update_idletasks()
                
        except Exception as e:
            self.show_error(f"Error updating preview: {str(e)}")
            self.preview_text.delete("1.0", "end")
            self.preview_text.insert("1.0", "Error loading preview")
            
    def start_conversion(self):
        """Start the conversion process in a separate thread"""
        if not hasattr(self, 'current_file'):
            self.show_error("Please select a PDF file first")
            return
            
        page_range = self.validate_page_range()
        if self.page_selection_var.get() == "specific" and page_range is None:
            return
            
        self.convert_button.configure(state="disabled")
        
        def conversion_thread():
            try:
                self.show_status("Converting PDF to audiobook...")
                self.progress_bar.set(0)
                self.app.update()
                
                output_dir = "audio_output"
                os.makedirs(output_dir, exist_ok=True)
                
                base_name = os.path.splitext(os.path.basename(self.current_file))[0]
                if page_range:
                    output_path = os.path.join(output_dir, f"{base_name}_pages_{page_range[0]}-{page_range[1]}.mp3")
                else:
                    output_path = os.path.join(output_dir, f"{base_name}.mp3")
                
                self.show_status("Extracting text from PDF...")
                text = self.converter.extract_text_from_pdf(self.current_file, page_range=page_range)
                if not text.strip():
                    raise Exception("No text could be extracted from the PDF")
                self.progress_bar.set(0.4)
                self.app.update()
                
                self.show_status("Processing text...")
                processed_text = self.converter.preprocess_text(text)
                if not processed_text.strip():
                    raise Exception("Text processing resulted in empty content")
                self.progress_bar.set(0.6)
                self.app.update()
                
                language = self.converter.detect_language(processed_text)
                self.show_status(f"Converting to audio (Language: {language})...")
                self.progress_bar.set(0.7)
                self.app.update()
                
                self.show_status("Attempting online conversion...")
                success = self.converter.convert_to_audio(processed_text, output_path, language)
                
                if not success:
                    self.show_status("Online conversion failed. Trying offline conversion...")
                    self.app.update()
                    success = self.converter.convert_to_audio(processed_text, output_path, language, use_offline=True)
                
                if success:
                    self.progress_bar.set(1.0)
                    self.show_status(f"Conversion complete! Audio saved to: {output_path}")
                else:
                    raise Exception("Both online and offline conversion methods failed")
                
            except Exception as e:
                error_msg = str(e)
                print(f"Conversion error: {error_msg}")
                self.show_error(f"Error during conversion: {error_msg}")
                self.progress_bar.set(0)
            finally:
                self.convert_button.configure(state="normal")
                self.app.update()
                
        threading.Thread(target=conversion_thread, daemon=True).start()
        
    def run(self):
        """Start the GUI application"""
        self.app.mainloop()

if __name__ == "__main__":
    app = PDFAudiobookGUI()
    app.run()
