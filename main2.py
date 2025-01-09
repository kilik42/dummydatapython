import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

# Load and clean the data
file_path = "Dummy Data3.csv"  # Replace with your file path
data = pd.read_csv(file_path)
filtered_data = data[['Name', 'Amount', 'DATE', 'Reason']].dropna(subset=['Amount', 'DATE', 'Reason'])
filtered_data = filtered_data[filtered_data['Amount'] != 'Amount']
filtered_data['Amount'] = filtered_data['Amount'].replace(r'[\$,]', '', regex=True).astype(float)
filtered_data['DATE'] = pd.to_datetime(filtered_data['DATE'], errors='coerce')
filtered_data = filtered_data.dropna(subset=['DATE'])
filtered_data = filtered_data.sort_values('DATE')

# Aggregate contributions
total_contributions = filtered_data.groupby('Reason')['Amount'].sum().reset_index()
grand_total = total_contributions['Amount'].sum()

def generate_pdf(output_path):
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    y_position = height - 50  # Start from the top margin
    margin = 50  # Left margin

    def draw_table(table_data, x, y, col_widths):
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        table.wrapOn(c, width, height)
        table.drawOn(c, x, y)
        return table._height  # Return table height for dynamic positioning

    def add_page():
        nonlocal y_position
        c.showPage()
        c.setFont("Helvetica", 12)
        y_position = height - 50  # Reset y_position for the new page

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, y_position, "Contribution Statement")
    y_position -= 30
    c.setFont("Helvetica", 10)
    c.drawString(margin, y_position, "First and Last Name")
    c.drawString(width - 200, y_position, "Period: 01/01/2015 - 12/31/2015")
    y_position -= 15
    c.drawString(width - 200, y_position, "As of: 03/23/2016")
    y_position -= 40

    # Total Contributions by Purpose/Fund
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y_position, "Total Contributions by Purpose/Fund")
    y_position -= 20
    total_table_data = [["Purpose/Fund", "Amount"]]
    for _, row in total_contributions.iterrows():
        total_table_data.append([row['Reason'], f"${row['Amount']:.2f}"])
    total_table_data.append(["Total", f"${grand_total:.2f}"])

    table_height = draw_table(total_table_data, margin, y_position - 60, [300, 100])
    y_position -= table_height + 40

    # Add a page if there's not enough space for the next section
    if y_position < 100:
        add_page()

    # List of Individual Contributions
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y_position, "List of Individual Contributions")
    y_position -= 20
    individual_table_data = [["Date", "Note/Check", "Purpose/Fund", "Amount"]]
    for _, row in filtered_data.iterrows():
        individual_table_data.append([
            row['DATE'].strftime("%m/%d/%Y"),
            "178",  # Replace with actual Note/Check if available
            row['Reason'],
            f"${row['Amount']:.2f}"
        ])

    # Split individual contributions table across pages if necessary
    rows_per_page = 20
    for i in range(0, len(individual_table_data), rows_per_page):
        chunk = individual_table_data[i:i + rows_per_page]
        table_height = draw_table(chunk, margin, y_position - 300, [100, 100, 200, 100])
        y_position -= table_height + 40

        if i + rows_per_page < len(individual_table_data):  # Add a new page if there are more rows
            add_page()

    # Footer
    if y_position < 100:
        add_page()
    c.setFont("Helvetica", 10)
    c.drawString(margin, 30, "Unless otherwise noted, no goods or services were received in return for these contributions.")
    c.save()

# Generate the PDF
output_file = "Improved_Contribution_Report_Fixed.pdf"
generate_pdf(output_file)

print(f"PDF generated: {output_file}")
