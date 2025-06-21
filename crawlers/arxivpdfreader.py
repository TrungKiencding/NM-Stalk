import pdfplumber
from io import BytesIO
import requests
session = requests.Session()
from typing import List, Dict


def get_arxiv_pdf_links(abs_links: List[str]) -> List[str]:
    """
    Convert arXiv abstract page links to direct PDF links.

    Parameters:
    - abs_links: List of links to arXiv abstract pages.

    Returns:
    - List of links to the corresponding PDF files.
    """
    pdf_links = []
    for link in abs_links:
        if '/abs/' in link:
            pdf_links.append(link.replace('/abs/', '/pdf/') + '.pdf')
        else:
            pdf_links.append(link)  # leave unchanged if not a standard abs link
    return pdf_links

def extract_pdf_text(url):
    """
    Extract text from a PDF.

    Args:
        url (str): URL of the PDF file.

    Returns:
        str: Extracted text content or error message.
    """
    try:
        response = session.get(url, timeout=20)  # Set timeout to 20 seconds
        if response.status_code != 200:
            return f"Error: Unable to retrieve the PDF (status code {response.status_code})"
        
        # Open the PDF file using pdfplumber
        with pdfplumber.open(BytesIO(response.content)) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text
        
        # Limit the text length
        cleaned_text = full_text
        return cleaned_text
    except requests.exceptions.Timeout:
        return "Error: Request timed out after 20 seconds"
    except Exception as e:
        return f"Error: {str(e)}"
    
def arxivPaperReader(url):
    pdfUrl = get_arxiv_pdf_links(url)
    return extract_pdf_text(pdfUrl)