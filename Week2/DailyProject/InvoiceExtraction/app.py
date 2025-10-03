import streamlit as st
import os
from invoice_extract import InvoiceExtractor, get_file_type
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Invoice Extraction App",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .info-box {
        background-color: #A9A9A9;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .small-image {
        max-width: 400px;
        margin: 0 auto;
        display: block;
    }
</style>
""", unsafe_allow_html=True)

def initialize_extractor():
    """Initialize the invoice extractor with API key"""
    groq_api_key = os.getenv('GROQ_API_KEY')
    
    if not groq_api_key:
        st.error("❌ GROQ_API_KEY not found. Please set it in Streamlit secrets or environment variables.")
        st.info("""
        To set up your Groq API key:
        1. Get your API key from https://console.groq.com
        2. Set it as an environment variable: GROQ_API_KEY=your_key
        3. Or add it to Streamlit secrets in .streamlit/secrets.toml
        """)
        return None
    
    return InvoiceExtractor(groq_api_key)

def display_invoice_data(invoice_data):
    """Display extracted invoice data in a formatted way"""
    if "error" in invoice_data:
        st.markdown(f'<div class="error-box">❌ Error: {invoice_data["error"]}</div>', unsafe_allow_html=True)
        return
    
    st.markdown('<div class="success-box">✅ Invoice data extracted successfully!</div>', unsafe_allow_html=True)
    
    # Create columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Basic Information")
        if invoice_data.get('invoice_number'):
            st.write(f"**Invoice Number:** {invoice_data['invoice_number']}")
        if invoice_data.get('invoice_date'):
            st.write(f"**Invoice Date:** {invoice_data['invoice_date']}")
        if invoice_data.get('due_date'):
            st.write(f"**Due Date:** {invoice_data['due_date']}")
        if invoice_data.get('total_amount'):
            st.write(f"**Total Amount:** {invoice_data['total_amount']}")
        if invoice_data.get('subtotal'):
            st.write(f"**Subtotal:** {invoice_data['subtotal']}")
        if invoice_data.get('tax_amount'):
            st.write(f"**Tax Amount:** {invoice_data['tax_amount']}")
    
    with col2:
        st.subheader("👤 Client Information")
        if invoice_data.get('client_name'):
            st.write(f"**Client Name:** {invoice_data['client_name']}")
        if invoice_data.get('client_address'):
            st.write(f"**Client Address:** {invoice_data['client_address']}")
    
    st.subheader("🏢 Vendor Information")
    vendor_col1, vendor_col2 = st.columns(2)
    
    with vendor_col1:
        if invoice_data.get('vendor_name'):
            st.write(f"**Vendor Name:** {invoice_data['vendor_name']}")
        if invoice_data.get('vendor_address'):
            st.write(f"**Vendor Address:** {invoice_data['vendor_address']}")
    
    with vendor_col2:
        if invoice_data.get('vendor_email'):
            st.write(f"**Vendor Email:** {invoice_data['vendor_email']}")
        if invoice_data.get('vendor_phone'):
            st.write(f"**Vendor Phone:** {invoice_data['vendor_phone']}")
    
    # Display items if available
    if invoice_data.get('items') and isinstance(invoice_data['items'], list):
        st.subheader("🛒 Invoice Items")
        for i, item in enumerate(invoice_data['items']):
            with st.expander(f"Item {i+1}: {item.get('description', 'N/A')}"):
                item_col1, item_col2, item_col3 = st.columns(3)
                with item_col1:
                    st.write(f"**Quantity:** {item.get('quantity', 'N/A')}")
                with item_col2:
                    st.write(f"**Unit Price:** {item.get('unit_price', 'N/A')}")
                with item_col3:
                    st.write(f"**Total:** {item.get('total', 'N/A')}")

def main():
    """Main Streamlit application"""
    st.markdown('<h1 class="main-header">📄 Invoice Extraction App</h1>', unsafe_allow_html=True)
    
    # Initialize extractor
    extractor = initialize_extractor()
    if not extractor:
        return
    
    # Sidebar
    st.sidebar.title("About")
    st.sidebar.info("""
    This app extracts structured information from invoices using AI.
    
    **Supported formats:**
    - PDF files
    - Images (JPG, PNG, TIFF, BMP)
    
    **Extracted fields:**
    - Invoice number & dates
    - Amounts (total, subtotal, tax)
    - Vendor details
    - Client information
    - Line items
    """)
    
    st.sidebar.title("Instructions")
    st.sidebar.markdown("""
    1. Upload an invoice (PDF or image)
    2. Click 'Extract Information'
    3. View extracted data
    4. Download results as JSON
    """)
    
    # Main content
    st.markdown("""
    ### Upload Your Invoice
    Drag and drop your invoice file (PDF or image) below to extract information automatically.
    """)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'jpg', 'jpeg', 'png', 'tiff', 'bmp'],
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        # Display file info
        file_type = get_file_type(uploaded_file.name)
        file_size = uploaded_file.size / 1024  # KB
        
        st.markdown(f'<div class="info-box">📁 **File:** {uploaded_file.name} | **Type:** {file_type.upper()} | **Size:** {file_size:.1f} KB</div>', unsafe_allow_html=True)
        
        # Display preview for images - smaller size
        if file_type in ['jpg', 'jpeg', 'png']:
            st.markdown('<div class="small-image">', unsafe_allow_html=True)
            st.image(uploaded_file, caption="Uploaded Invoice Preview", width=400)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Extract button
        if st.button("🚀 Extract Invoice Information", type="primary", use_container_width=True):
            with st.spinner("🔍 Extracting text and analyzing invoice..."):
                try:
                    # Process the file
                    file_bytes = uploaded_file.getvalue()
                    invoice_data = extractor.process_document(
                        file_bytes=file_bytes, 
                        file_type=file_type
                    )
                    
                    # Display results
                    display_invoice_data(invoice_data)
                    
                    # Download button for JSON - using original filename
                    if "error" not in invoice_data:
                        json_data = json.dumps(invoice_data, indent=2)
                        
                        # Create JSON filename based on uploaded file name
                        original_filename = uploaded_file.name
                        json_filename = f"{os.path.splitext(original_filename)[0]}_extracted.json"
                        
                        st.download_button(
                            label="📥 Download as JSON",
                            data=json_data,
                            file_name=json_filename,
                            mime="application/json",
                            use_container_width=True
                        )
                        
                except Exception as e:
                    st.error(f"❌ Processing failed: {str(e)}")
    
    else:
        # Placeholder when no file is uploaded
        st.markdown("""
        <div style='text-align: center; padding: 50px; border: 2px dashed #ccc; border-radius: 10px;'>
            <h3>📁 Upload an invoice to get started</h3>
            <p>Supported formats: PDF, JPG, PNG, TIFF, BMP</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()