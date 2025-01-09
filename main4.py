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

# Extract the first and last name dynamically
first_and_last_name = filtered_data['Name'].dropna().iloc[0] if not filtered_data['Name'].dropna().empty else "First and Last Name"

def generate_pdf(output_path):
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    y_position = height - 50  # Start from the top margin
    margin = 50  # Left margin
    line_spacing = 20  # Space between sections and elements

    def add_header():
        """Adds the header with the title, name, and period details."""
        nonlocal y_position
        c.setFont("Helvetica-Bold", 16)
        c.drawString(200, y_position, "Contribution Statement")
        y_position -= line_spacing + 10
        c.setFont("Helvetica", 10)
        c.drawString(margin, y_position, first_and_last_name)
        c.drawString(width - 200, y_position, "Period: 01/01/2015 - 12/31/2015")
        y_position -= line_spacing
        c.drawString(width - 200, y_position, "As of: 03/23/2016")
        y_position -= line_spacing

    def add_table(title, table_data, col_widths):
        """Adds a table with the given title and data."""
        nonlocal y_position
        # Check for space; add a new page if needed
        if y_position < 100:
            add_new_page()

        # Add title
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y_position, title)
        y_position -= line_spacing

        # Draw the table
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        table.wrapOn(c, width, height)
        table.drawOn(c, margin, y_position - table._height)
        y_position -= table._height + line_spacing

    def add_new_page():
        """Adds a new page and resets the y_position."""
        nonlocal y_position
        c.showPage()
        c.setFont("Helvetica", 12)
        y_position = height - 50

    # Add header
    add_header()

    # Add Total Contributions table
    total_table_data = [["Purpose/Fund", "Amount"]]
    for _, row in total_contributions.iterrows():
        total_table_data.append([row['Reason'], f"${row['Amount']:.2f}"])
    total_table_data.append(["Total", f"${grand_total:.2f}"])
    add_table("Total Contributions by Purpose/Fund", total_table_data, [300, 100])

    # Add Individual Contributions table
    individual_table_data = [["Date", "Note/Check", "Purpose/Fund", "Amount"]]
    for _, row in filtered_data.iterrows():
        individual_table_data.append([
            row['DATE'].strftime("%m/%d/%Y"),
            "178",  # Replace with actual Note/Check if available
            row['Reason'],
            f"${row['Amount']:.2f}"
        ])

    # Break the individual contributions into chunks for pages
    rows_per_page = 20
    for i in range(0, len(individual_table_data), rows_per_page):
        chunk = individual_table_data[i:i + rows_per_page]
        add_table("List of Individual Contributions", chunk, [100, 100, 200, 100])

    # Footer
    if y_position < 100:
        add_new_page()
    c.setFont("Helvetica", 10)
    c.drawString(margin, 30, "Unless otherwise noted, no goods or services were received in return for these contributions.")
    c.save()

# Generate the PDF
output_file = "Final_Contribution_Report_No_Overlap.pdf"
generate_pdf(output_file)

print(f"PDF generated: {output_file}")
