import streamlit as st
import pdfplumber
import re
import PyPDF2
from io import BytesIO

# Function to extract SKUs and corresponding page numbers
def extract_sku_pages(pdf_file):
    sku_dict = {}
    
    # Open the uploaded PDF file
    with pdfplumber.open(pdf_file) as pdf:
        # Loop through each page and extract SKU info
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            
            # Find all occurrences of "SKU: xyz" using regex
            matches = re.findall(r'SKU:\s*([A-Za-z0-9\-]+)', text)
            
            for sku in matches:
                if sku in sku_dict:
                    sku_dict[sku].add(page_num)  # Add the page number to the set
                else:
                    sku_dict[sku] = {page_num}   # Initialize with a set of the page number
    return sku_dict

# Function to rearrange PDF pages
def rearrange_pdf(sku_dict, pdf_file):
    # Flattening the page order list to get the total page rearrangement
    rearranged_pages = [page for pages in sku_dict.values() for page in pages]
    
    # Open the original PDF and rearrange the pages
    reader = PyPDF2.PdfReader(pdf_file)
    writer = PyPDF2.PdfWriter()
    
    # Adjust page numbers (since PyPDF2 is zero-indexed)
    for page_num in rearranged_pages:
        writer.add_page(reader.pages[page_num - 1])
    
    # Save to an in-memory file
    output = BytesIO()
    writer.write(output)
    output.seek(0)
    return output

# Streamlit app starts here
st.title('PDF Rearranger based on SKU')

# Upload the PDF file
uploaded_file = st.file_uploader("Upload your Shipping PDF", type="pdf")

if uploaded_file is not None:
    st.write("Processing your PDF...")
    
    # Extract SKU and page info
    sku_dict = extract_sku_pages(uploaded_file)
    
    # Display the extracted SKU information
    st.write("Extracted SKU and pages:", sku_dict)
    
    # Rearrange the PDF based on the SKU page numbers
    rearranged_pdf = rearrange_pdf(sku_dict, uploaded_file)
    
    # Provide the download button for the rearranged PDF
    st.download_button(
        label="Download rearranged PDF",
        data=rearranged_pdf,
        file_name="rearranged_output.pdf",
        mime="application/pdf"
    )
