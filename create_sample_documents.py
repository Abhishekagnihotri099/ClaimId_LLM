import os
import shutil
import pandas as pd

def read_claim_numbers_from_csv(csv_file_path):
    """Read claim numbers from a CSV file."""
    # Load the CSV file
    df = pd.read_csv(csv_file_path)
    
    # Ensure the claim_number column exists in the CSV file
    if 'claim_number' not in df.columns:
        raise ValueError("The CSV file must have a 'claim_number' column.")
    
    # Return claim numbers as a list
    return df['claim_number'].astype(str).tolist()

def rename_and_move_pdf(claim_numbers, sample_pdf_path, invoice_folder):
    """Rename the PDF for each claim number and move it to the invoice folder."""
    # Ensure the invoice folder exists
    if not os.path.exists(invoice_folder):
        os.makedirs(invoice_folder)

    for claim_number in claim_numbers:
        # Construct the new file path for each claim number
        new_pdf_path = os.path.join(invoice_folder, f"{claim_number}.pdf")
        
        # Check if the sample PDF exists
        if os.path.exists(sample_pdf_path):
            # Rename and move the sample PDF
            shutil.copy(sample_pdf_path, new_pdf_path)
            print(f"Saved PDF for Claim {claim_number} as {new_pdf_path}")
        else:
            print(f"Sample PDF {sample_pdf_path} not found.")

# Example usage
csv_file_path = "claims.csv"  # Path to your CSV file containing claim numbers
sample_pdf_path = "sample.pdf"  # Path to the sample PDF
invoice_folder = "invoice"  # Folder where you want to save the renamed PDFs

# Step 1: Get claim numbers from the CSV file
claim_numbers = read_claim_numbers_from_csv(csv_file_path)

# Step 2: Rename and move the sample PDF for each claim number
rename_and_move_pdf(claim_numbers, sample_pdf_path, invoice_folder)
