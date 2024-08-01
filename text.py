import PyPDF2
import os
from PIL import Image
import pytesseract
import io
import json

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                if '/XObject' in page['/Resources']:
                    xObject = page['/Resources']['/XObject'].get_object()
                    for obj in xObject:
                        if xObject[obj]['/Subtype'] == '/Image':
                            size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                            data = xObject[obj].get_data()
                            if xObject[obj]['/ColorSpace'] == '/DeviceRGB':
                                mode = "RGB"
                            else:
                                mode = "P"
                            
                            img = Image.open(io.BytesIO(data))
                            text += pytesseract.image_to_string(img) + "\n\n"
                
                # Also try to extract text directly (in case there's any text layer)
                text += page.extract_text() + "\n\n"
    except Exception as e:
        text = f"Error processing {pdf_path}: {str(e)}"
    return text

def process_file_or_directory(input_path, output_dir):
    if os.path.isfile(input_path) and input_path.lower().endswith('.pdf'):
        process_single_pdf(input_path, output_dir)
    elif os.path.isdir(input_path):
        for filename in os.listdir(input_path):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(input_path, filename)
                process_single_pdf(pdf_path, output_dir)
    else:
        print(f"Error: {input_path} is not a valid PDF file or directory")

def process_single_pdf(pdf_path, output_dir):
    filename = os.path.basename(pdf_path)
    output_filename = os.path.splitext(filename)[0] + ".json"
    output_path = os.path.join(output_dir, output_filename)
    
    text = extract_text_from_pdf(pdf_path)
    result = {filename: text}
    
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(result, json_file, ensure_ascii=False, indent=4)
    
    print(f"Processed {filename}. Output saved to {output_path}")

# Get input from user
input_path = input("Enter the path to your PDF file or directory containing PDF files: ").strip()
output_dir = input("Enter the directory for output JSON files: ").strip()

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Process the input
process_file_or_directory(input_path, output_dir)

print("Processing complete.")