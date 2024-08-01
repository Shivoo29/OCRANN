import os
import csv
import fitz  # PyMuPDF
import numpy as np
from PIL import Image

# Set the directory paths
pdf_dir = "Input"
output_dir = "Output"
flagged_file = "flagged_pdfs.csv"

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Open CSV file to write flagged PDFs
with open(flagged_file, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["Filename", "Reason"])

    # Iterate through all files in the directory
    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_dir, filename)
            
            try:
                # Open the PDF file
                doc = fitz.open(pdf_path)
                
                # Iterate through each page
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    
                    # Render page to an image (GPU acceleration if available)
                    pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
                    
                    # Convert to PIL Image
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    
                    # Save as PNG
                    output_filename = f"{os.path.splitext(filename)[0]}_page_{page_num+1}.png"
                    output_path = os.path.join(output_dir, output_filename)
                    img.save(output_path, "PNG")
                
                print(f"Converted {filename} to PNG")
                
            except fitz.FileDataError as e:
                # Log password-protected or errored PDFs
                csv_writer.writerow([filename, str(e)])
                print(f"Skipped {filename}: {str(e)}")
            
            except Exception as e:
                # Log any other errors
                csv_writer.writerow([filename, f"Error: {str(e)}"])
                print(f"Error processing {filename}: {str(e)}")

print("Conversion complete!")
print(f"Flagged PDFs have been logged in {flagged_file}")