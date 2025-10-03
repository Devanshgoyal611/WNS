import re
import json
import pytesseract
from PIL import Image
import pdf2image
from groq import Groq
from typing import Dict, Any, Optional
import io
import os
from dotenv import load_dotenv

load_dotenv()

class InvoiceExtractor:
    def __init__(self, groq_api_key: str):
        """Initialize the InvoiceExtractor with Groq API client"""
        self.client = Groq(api_key=groq_api_key)
        self.extraction_prompt = """
        Extract the following information from the invoice text below. Return ONLY a valid JSON object with these fields:
        - invoice_number: The invoice number/identifier
        - invoice_date: The invoice date in YYYY-MM-DD format
        - total_amount: The total amount including currency
        - vendor_name: The name of the vendor/seller
        - vendor_address: The vendor's address
        - vendor_email: The vendor's email (if available)
        - vendor_phone: The vendor's phone number (if available)
        - client_name: The client/customer name
        - client_address: The client's address
        - due_date: The due date in YYYY-MM-DD format (if available)
        - tax_amount: The tax amount (if available)
        - subtotal: The subtotal amount (if available)
        - items: List of items with description, quantity, unit_price, and total

        If any field is not found, set it to null.

        Invoice Text:
        {text}

        Return ONLY the JSON object, no other text.
        """
    
    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image using Tesseract OCR"""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from image: {str(e)}")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using pdf2image and Tesseract"""
        try:
            # Convert PDF to images
            images = pdf2image.convert_from_path(pdf_path)
            full_text = ""
            
            for i, image in enumerate(images):
                text = pytesseract.image_to_string(image)
                full_text += f"Page {i+1}:\n{text}\n\n"
            
            return full_text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def extract_text_from_pdf_bytes(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF bytes"""
        try:
            images = pdf2image.convert_from_bytes(pdf_bytes)
            full_text = ""
            
            for i, image in enumerate(images):
                text = pytesseract.image_to_string(image)
                full_text += f"Page {i+1}:\n{text}\n\n"
            
            return full_text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF bytes: {str(e)}")
    
    def extract_text_from_image_bytes(self, image_bytes: bytes) -> str:
        """Extract text from image bytes"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from image bytes: {str(e)}")
    
    def clean_extracted_text(self, text: str) -> str:
        """Clean and preprocess extracted text"""
        # Remove extra whitespace and normalize line breaks
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        return text.strip()
    
    def extract_invoice_info(self, text: str) -> Dict[str, Any]:
        """Extract structured invoice information using Groq API"""
        try:
            # Clean the text
            cleaned_text = self.clean_extracted_text(text)
            
            if not cleaned_text:
                return {"error": "No text could be extracted from the document"}
            
            # Prepare the prompt
            prompt = self.extraction_prompt.format(text=cleaned_text)
            
            # Call Groq API
            completion = self.client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at extracting structured information from invoices. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=2048,
                top_p=1,
                stream=False,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            response_text = completion.choices[0].message.content
            invoice_data = json.loads(response_text)
            
            return invoice_data
            
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse JSON response: {str(e)}"}
        except Exception as e:
            return {"error": f"Error extracting invoice info: {str(e)}"}
    
    def process_document(self, file_path: str = None, file_bytes: bytes = None, file_type: str = None) -> Dict[str, Any]:
        """Main method to process invoice documents"""
        try:
            # Extract text based on file type
            if file_type == 'pdf':
                if file_path:
                    text = self.extract_text_from_pdf(file_path)
                else:
                    text = self.extract_text_from_pdf_bytes(file_bytes)
            elif file_type in ['jpg', 'jpeg', 'png', 'tiff', 'bmp']:
                if file_path:
                    text = self.extract_text_from_image(file_path)
                else:
                    text = self.extract_text_from_image_bytes(file_bytes)
            else:
                return {"error": f"Unsupported file type: {file_type}"}
            
            # Extract structured information
            invoice_info = self.extract_invoice_info(text)
            
            # Add metadata
            if "error" not in invoice_info:
                invoice_info["extraction_status"] = "success"
                invoice_info["raw_text_length"] = len(text)
            else:
                invoice_info["extraction_status"] = "failed"
            
            return invoice_info
            
        except Exception as e:
            return {"error": f"Processing error: {str(e)}", "extraction_status": "failed"}

# Utility function for file type detection
def get_file_type(filename: str) -> str:
    """Get file type from filename"""
    ext = filename.lower().split('.')[-1]
    if ext == 'pdf':
        return 'pdf'
    elif ext in ['jpg', 'jpeg', 'png', 'tiff', 'bmp']:
        return ext
    else:
        return 'unknown'