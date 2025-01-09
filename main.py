import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

# Load and clean the data
file_path = 'Dummy Data3.csv'  # Replace with the actual file path
data = pd.read_csv(file_path)

# Select relevant columns and clean data
filtered_data = data[['Name', 'Amount', 'DATE', 'Reason']].dropna(subset=['Amount', 'DATE', 'Reason'])
filtered_data = filtered_data[filtered_data['Amount'] != 'Amount']  # Remove header-like entries

# Convert Amount to numeric and DATE to datetime
filtered_data['Amount'] = filtered_data['Amount'].replace(r'[\$,]', '', regex=True).astype(float)
filtered_data['DATE'] = pd.to_datetime(filtered_data['DATE'], errors='coerce')

# Remove rows with invalid dates
filtered_data = filtered_data.dropna(subset=['DATE'])

# Sort data by date
filtered_data = filtered_data.sort_values('DATE')

# Aggregate total contributions by purpose/fund
total_contributions = filtered_data.groupby('Reason')['Amount'].sum().reset_index()

# Total amount
grand_total = total_contributions['Amount'].sum()

# Define PDF generation function
def generate_pdf(output_path):
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, height - 50, "Contribution Statement")

    # Date range and as-of date
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 80, "Period: 01/01/2024 - 12/31/2024")
    c.drawString(400, height - 80, "As of: 01/08/2025")

    # Section: Total Contributions by Purpose/Fund
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 110, "Total Contributions by Purpose/Fund")

    # Table for Total Contributions
    total_table_data = [["Purpose/Fund", "Amount"]]
    for _, row in total_contributions.iterrows():
        total_table_data.append([row['Reason'], f"${row['Amount']:.2f}"])
    total_table_data.append(["Total", f"${grand_total:.2f}"])

    table = Table(total_table_data, colWidths=[300, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Draw table
    table.wrapOn(c, 50, height - 200)
    table.drawOn(c, 50, height - 300)

    # Section: List of Individual Contributions
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 320, "List of Individual Contributions")

    # Table for Individual Contributions
    individual_table_data = [["Date", "Purpose/Fund", "Amount"]]
    for _, row in filtered_data.iterrows():
        individual_table_data.append([row['DATE'].strftime("%m/%d/%Y"), row['Reason'], f"${row['Amount']:.2f}"])

    individual_table = Table(individual_table_data, colWidths=[100, 300, 100])
    individual_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Draw table
    individual_table.wrapOn(c, 50, height - 500)
    individual_table.drawOn(c, 50, height - 700)

    # Footer
    c.setFont("Helvetica", 10)
    c.drawString(50, 30, "Unless otherwise noted, no goods or services were received in return for these contributions.")

    c.save()

# Generate the PDF report
output_file = "Contribution_Report.pdf"
generate_pdf(output_file)

print(f"PDF report generated: {output_file}")
