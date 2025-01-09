import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import json

# Load JSON file
file_path = "Dummy Data3.json"
with open(file_path, "r") as file:
    data = json.load(file)

# Convert JSON to DataFrame
df = pd.DataFrame(data)

# Drop unnecessary fields
df = df.loc[:, ~df.columns.str.startswith("FIELD")]

# Ensure required columns exist
required_columns = ['Name', 'Amount', 'DATE', 'Address', 'Reason', 'Email Address', 'Phone Number']
for col in required_columns:
    if col not in df.columns:
        df[col] = ''  # Add missing column with default empty values

# Clean the Amount column
df['Amount'] = df['Amount'].replace(r'[\$,]', '', regex=True)
df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
df = df.dropna(subset=['Amount'])

# Add Total column
df['Total'] = df['Amount']

# Prepare filtered data
filtered_data = df[['Name', 'Amount', 'DATE', 'Address', 'Reason', 'Email Address', 'Phone Number', 'Total']].copy()
filtered_data['DATE'] = pd.to_datetime(filtered_data['DATE'], errors='coerce')
filtered_data = filtered_data.dropna(subset=['DATE'])
filtered_data = filtered_data.sort_values('DATE')

# Aggregate contributions
total_contributions = filtered_data.groupby('Reason')['Total'].sum().reset_index()

# Extract the first and last name dynamically
first_and_last_name = filtered_data['Name'].dropna().iloc[0] if not filtered_data['Name'].dropna().empty else "First and Last Name"

# Define constants for column widths
def calculate_column_widths(page_width, margins):
    usable_width = page_width - 2 * margins
    return [
        usable_width * 0.10,  # Date
        usable_width * 0.15,  # Name
        usable_width * 0.25,  # Address
        usable_width * 0.20,  # Email Address
        usable_width * 0.10,  # Phone Number
        usable_width * 0.10,  # Purpose/Fund
        usable_width * 0.05,  # Amount
        usable_width * 0.05,  # Total
    ]

# Generate the PDF
def generate_pdf(output_path):
    c = canvas.Canvas(output_path, pagesize=landscape(letter))
    page_width, page_height = landscape(letter)
    margin = 50
    usable_width = page_width - 2 * margin
    y_position = page_height - 50
    line_spacing = 20

    def add_header():
        nonlocal y_position
        c.setFont("Helvetica-Bold", 16)
        c.drawString(margin, y_position, "Contribution Statement")
        y_position -= line_spacing + 10
        c.setFont("Helvetica", 10)
        c.drawString(margin, y_position, first_and_last_name)
        c.drawString(page_width - margin - 200, y_position, "Period: 01/01/2024 - 12/31/2024")
        y_position -= line_spacing
        c.drawString(page_width - margin - 200, y_position, "As of: 03/23/2025")
        y_position -= line_spacing

    def add_table(title, table_data, col_widths):
        nonlocal y_position
        if y_position < 100:
            add_new_page()
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y_position, title)
        y_position -= line_spacing

        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('ALIGN', (-2, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('WORDWRAP', (0, 0), (-1, -1)),  # Enable text wrapping
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        table.wrapOn(c, page_width, page_height)
        table.drawOn(c, margin, y_position - table._height)
        y_position -= table._height + line_spacing

    def add_new_page():
        nonlocal y_position
        c.showPage()
        c.setFont("Helvetica", 12)
        y_position = page_height - 50

    add_header()

    # Add Total Contributions table
    total_table_data = [["Purpose/Fund", "Total Amount"]]
    for _, row in total_contributions.iterrows():
        total_table_data.append([row['Reason'], f"${row['Total']:.2f}"])
    add_table("Total Contributions by Purpose/Fund", total_table_data, [usable_width * 0.7, usable_width * 0.3])

    # Add Individual Contributions table
    individual_table_data = [["Date", "Name", "Address", "Email Address", "Phone Number", "Purpose/Fund", "Amount", "Total"]]
    for _, row in filtered_data.iterrows():
        individual_table_data.append([
            row['DATE'].strftime("%m/%d/%Y"),
            row['Name'] if row['Name'] else "-",
            row['Address'] if row['Address'] else "-",
            row['Email Address'] if row['Email Address'] else "-",
            row['Phone Number'] if row['Phone Number'] else "-",
            row['Reason'],
            f"${row['Amount']:.2f}",
            f"${row['Total']:.2f}",
        ])
    col_widths = calculate_column_widths(page_width, margin)
    add_table("List of Individual Contributions", individual_table_data, col_widths)

    # Footer
    if y_position < 100:
        add_new_page()
    c.setFont("Helvetica", 10)
    c.drawString(margin, 30, "Unless otherwise noted, no goods or services were received in return for these contributions.")
    c.save()

# Generate the PDF
output_file = "Final_Contribution_Report_Redesigned.pdf"
generate_pdf(output_file)

print(f"PDF generated: {output_file}")
