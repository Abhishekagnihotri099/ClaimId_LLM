from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_invoice_pdf(file_name):
    # Create a canvas object to draw the PDF
    c = canvas.Canvas(file_name, pagesize=letter)
    width, height = letter
    
    # Set up the title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 40, "Invoice")
    
    # Add a line under the title
    c.setLineWidth(1)
    c.line(100, height - 50, width - 100, height - 50)
    
    # List of items for the invoice
    items = [
        ("Clutch", 1, "$100"),
        ("Suspension System", 2, "$200"),
        ("Exhaust System", 1, "$150"),
        ("Spark Plugs", 4, "$40"),
    ]
    
    # Set up the table header
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, height - 80, "Item")
    c.drawString(300, height - 80, "Quantity")
    c.drawString(400, height - 80, "Price")
    
    # Set the font for the items
    c.setFont("Helvetica", 12)
    
    # Starting y position for the items
    y_position = height - 100
    
    # Add the items to the PDF
    for item in items:
        c.drawString(100, y_position, item[0])  # Item name
        c.drawString(300, y_position, str(item[1]))  # Quantity
        c.drawString(400, y_position, item[2])  # Price
        y_position -= 20
    
    # Save the PDF
    c.save()

# Create the sample invoice PDF
create_invoice_pdf("invoice2.pdf")
