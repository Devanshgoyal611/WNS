from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from PIL import Image
import pytesseract
import os
from typing import List
import PyPDF2

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=80,
            length_function=len
        )
    
    async def process_text_file(self, file_path: str, filename: str) -> List[Document]:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        
        texts = self.text_splitter.split_text(text)
        documents = [
            Document(
                page_content=text,
                metadata={"source": filename, "type": "text"}
            ) for text in texts
        ]
        return documents
    
    async def process_pdf_file(self, file_path: str, filename: str) -> List[Document]:
        documents = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                if text.strip():
                    texts = self.text_splitter.split_text(text)
                    for text_chunk in texts:
                        documents.append(Document(
                            page_content=text_chunk,
                            metadata={
                                "source": filename,
                                "page": page_num + 1,
                                "type": "pdf"
                            }
                        ))
        return documents
    
    async def process_image_file(self, file_path: str, filename: str) -> List[Document]:
        try:
            # Extract text from image using OCR
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            
            if text.strip():
                documents = [Document(
                    page_content=text,
                    metadata={"source": filename, "type": "image"}
                )]
                return documents
            return []
        except Exception as e:
            print(f"Error processing image: {e}")
            return []
    
    async def process_document(self, file_path: str, filename: str) -> List[Document]:
        file_ext = filename.lower().split('.')[-1]
        
        if file_ext in ['txt', 'md']:
            return await self.process_text_file(file_path, filename)
        elif file_ext == 'pdf':
            return await self.process_pdf_file(file_path, filename)
        elif file_ext in ['jpg', 'jpeg', 'png', 'bmp']:
            return await self.process_image_file(file_path, filename)
        elif file_ext == 'docx':
            return await self.process_docx_file(file_path, filename)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        
# Make process_docx_file func

document_processor = DocumentProcessor()