import pdfplumber 
import io 
from app.core.logging import logger 


def is_valid_cell(cell) -> bool: 
    if not cell: 
        return False 
    
    cell_str = str(cell).strip() 

    if not cell_str: 
        return False 
    
    # reject obviously empty/invalid cells 
    empty_markers = ["-", "n/a", "--", "__", "___", ":", ", ", "-"]
    if cell_str.lower() in empty_markers: 
        return False 
    
    return True 

def extract_text_from_pdf(content: bytes) -> str: 
    """
    Extract text and tables from PDF file     
    - Supports only text-based PDFs (not scanned images)
    - Tables are extracted as text
    """

    full_text = "" 

    try:
        # wrap bytes in io.BytesIO so pdfplumber can read it
        pdf_file = io.BytesIO(content)
        with pdfplumber.open(pdf_file) as pdf:
            logger.info(f"PDF opened: {len(pdf.pages)} pages")
            
            for page_num, page in enumerate(pdf.pages, start=1):
                # extract text outside tables only
                page_text = page.extract_text(x_tolerance=3, y_tolerance=3)
                if page_text: 
                    full_text += f"\n{page_text}"
            
                # extract tables from page 
                tables = page.extract_tables() 
                for table in tables:
                    # convert table to readble text format 
                    table_text = convert_table_to_text(table, page_num)
                    if table_text: 
                        full_text += table_text 

        logger.info(f"Successfully extracted text from {len(pdf.pages)} PDF pages")
    except Exception as e: 
        logger.error(f"Error extracting PDF text: {str(e)}")
        raise

    return full_text.strip()


def convert_table_to_text(table: list, page_num: int) -> str:
    """
    converts table data to readable text for LLM

    example input:
    [
        ["Test", "Value", "Normal Range"],
        ["Hemoglobin", "12.5", "13-17"],
        ["WBC", "7500", "4000-11000"]
    ]
    example input:
    [
        ["Test", "Value", "Normal Range"],
        ["Hemoglobin", "12.5", "13-17"],
        ["WBC", "7500", "4000-11000"]
    ]
    """
    
    if not table or len(table) < 2:
        return "" 
    
    result = "\n"

    # first row is headers
    headers = [str(h).strip() if h else "" for h in table[0]]

    valid_headers = [h for h in headers if is_valid_cell(h)]
    if not valid_headers: 
        logger.warning("No valid headers found in table")
        return ""

    # normalize all rows to same length as header
    for row in table[1:]:
        row_parts = [] 
        for i, cell in enumerate(row):
            if i < len(headers) and is_valid_cell(cell) and is_valid_cell(headers[i]):
                header = headers[i]
                clean_cell = str(cell).strip() if cell else ""
                row_parts.append(f"{header}: {clean_cell}")
        if row_parts: 
            result += ", ".join(row_parts) + "\n"

    logger.info(f"Table converted to text on page {page_num}")
    return result 

def extract_text_from_txt(content: bytes) -> str:
    """
    Extract text from TXT file
    """
    try:
        # decode bytes to utf-8 string
        text = content.decode("utf-8", errors="ignore")
        return text
    except Exception as e:
        logger.error(f"Error extracting TXT text: {str(e)}")
        raise


def extract_text(content: bytes, file_type: str) -> str:
    """
    single entry point for text extraction
    used by both router and celery worker
    accepts file_type string instead of UploadFile
    """
    if file_type == "pdf":
        text = extract_text_from_pdf(content)
    elif file_type == "txt":
        text = extract_text_from_txt(content)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

    if not text.strip():
        raise ValueError("No text could be extracted from file")

    return text
