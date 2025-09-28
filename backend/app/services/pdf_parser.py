import PyPDF2
import pdfplumber
from typing import Optional
class PDFParser: 
    def parse__pdf(self, file_path: str)->Optional[str]:
        try:
            text=""
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text()
                        if page_text:
                            text+=page_text+"\n"
            except Exception as e:
                print(f"pdf Plumber is shit :{e}")
            if not text.strip():
                try:
                    with open(file_path,'rb') as file:
                        pdf_reader=PyPDF2.PdfReader(file)
                        for page in pdf_reader.pages:
                            page_text=page.extract_text()

                            if page_text:
                                text+=page_text+"/n"
                except Exception as e:
                    print(f"PyPDF is shit:{e}")    
            
            if text.strip():
                return text.strip()
            else:
                return None
            
        except Exception as e:
            printf(f"PDF pasring is failed:{e}")
            return None