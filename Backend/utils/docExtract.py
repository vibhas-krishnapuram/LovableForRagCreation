from io import BytesIO
import PyPDF2
from fastapi import UploadFile

async def extract_text_from_file(file: UploadFile):
    """Extract text content from an uploaded file (.txt, .pdf, or code files)."""

    if file is None:
        return ""

    content = await file.read()
    filename = file.filename.lower()


    if filename.endswith(".txt"):
        return content.decode("utf-8", errors="ignore")

 
    if filename.endswith(".pdf"):
        try:
            pdf = PyPDF2.PdfReader(BytesIO(content))
            extracted = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted.append(text)
            return "\n".join(extracted)
        except:
            return ""

 
    if filename.endswith((".py", ".js", ".ts", ".java", ".c", ".cpp", ".go", ".rs",
                          ".log", ".cfg", ".md", ".json", ".yaml", ".yml")):
        return content.decode("utf-8", errors="ignore")

    # Default fallback
    return content.decode("utf-8", errors="ignore")
