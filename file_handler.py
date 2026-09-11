"""
File handling and processing for Astra
"""

import os
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
import csv
import json

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'csv', 'py', 'js', 'java', 'cpp', 'c', 'go', 'rs', 'md'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
UPLOAD_FOLDER = 'uploads'

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type(filename):
    """Determine file type from extension"""
    ext = filename.rsplit('.', 1)[1].lower()
    if ext == 'pdf':
        return 'pdf'
    elif ext == 'csv':
        return 'csv'
    elif ext in ['py', 'js', 'java', 'cpp', 'c', 'go', 'rs']:
        return 'code'
    else:
        return 'text'

def extract_text_from_pdf(file_path):
    """Extract text content from PDF"""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_text_from_csv(file_path):
    """Extract text content from CSV"""
    try:
        text = ""
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                text += ", ".join(row) + "\n"
        return text
    except Exception as e:
        return f"Error reading CSV: {str(e)}"

def extract_text_from_file(file_path):
    """Extract text from various file types"""
    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.csv'):
        return extract_text_from_csv(file_path)
    else:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

def save_uploaded_file(file, user_id):
    """Save uploaded file to disk"""
    if not file or not allowed_file(file.filename):
        return None, "File not allowed"
    
    filename = secure_filename(file.filename)
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    filepath = os.path.join(UPLOAD_FOLDER, f"{user_id}_{filename}")
    
    try:
        file.save(filepath)
        return filepath, None
    except Exception as e:
        return None, str(e)
