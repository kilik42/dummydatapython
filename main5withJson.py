# import pandas as pd
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# from reportlab.platypus import Table, TableStyle
# from reportlab.lib import colors
# import json

# # Load JSON file
# file_path = "Dummy Data3.json"
# with open(file_path, "r") as file:
#     data = json.load(file)

# # Convert JSON to DataFrame
# df = pd.DataFrame(data)

# # Drop unnecessary fields (those starting with "FIELD")
# df = df.loc[:, ~df.columns.str.startswith("FIELD")]

# # Ensure required columns exist
# required_columns = ['Name', 'Amount', 'DATE', 'Address', 'Reason', 'Email Address', 'Phone Number']
# for col in required_columns:
#     if col not in df.columns:
#         print(f"Column '{col}' is missing. Adding it as empty.")
#         df[col] = ''  # Add missing column with default empty values

# # Clean the Amount column
# df['Amount'] = df['Amount'].replace(r'[\$,]', '', regex=True)  # Remove $ and commas
# df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')  # Convert to numeric; invalid values become NaN
# df = df.dropna(subset=['Amount'])  # Drop rows with invalid 'Amount'

# # Add Total column
# df['Total'] = df['Amount']

# # Prepare filtered data
# filtered_data = df[['Name', 'Amount', 'DATE', 'Address', 'Reason', 'Email Address', 'Phone Number', 'Total']].copy()
# filtered_data['DATE'] = pd.to_datetime(filtered_data['DATE'], errors='coerce')  # Convert DATE column to datetime
# filtered_data = filtered_data.dropna(subset=['DATE'])  # Drop rows with invalid DATE values
# filtered_data = filtered_data.sort_values('DATE')

# # Aggregate contributions
# total_contributions = filtered_data.groupby('Reason')['Total'].sum().reset_index()

# # Extract the first and last name dynamically
# first_and_last_name = filtered_data['Name'].dropna().iloc[0] if not filtered_data['Name'].dropna().empty else "First and Last Name"

# def generate_pdf(output_path):
#     c = canvas.Canvas(output_path, pagesize=letter)
#     width, height = letter
#     y_position = height - 50  # Start from the top margin
#     margin = 50  # Left margin
#     line_spacing = 20  # Space between sections and elements

#     def add_header():
#         """Adds the header with the title, name, and period details."""
#         nonlocal y_position
#         c.setFont("Helvetica-Bold", 16)
#         c.drawString(200, y_position, "Contribution Statement")
#         y_position -= line_spacing + 10
#         c.setFont("Helvetica", 10)
#         c.drawString(margin, y_position, first_and_last_name)
#         c.drawString(width - 200, y_position, "Period: 01/01/2024 - 12/31/2024")
#         y_position -= line_spacing
#         c.drawString(width - 200, y_position, "As of: 03/23/2025")
#         y_position -= line_spacing

#     def add_table(title, table_data, col_widths):
#         """Adds a table with the given title and data."""
#         nonlocal y_position
#         # Check for space; add a new page if needed
#         if y_position < 100:
#             add_new_page()

#         # Add title
#         c.setFont("Helvetica-Bold", 12)
#         c.drawString(margin, y_position, title)
#         y_position -= line_spacing

#         # Draw the table
#         table = Table(table_data, colWidths=col_widths)
#         table.setStyle(TableStyle([
#             ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#             ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
#             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#             ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#         ]))
#         table.wrapOn(c, width, height)
#         table.drawOn(c, margin, y_position - table._height)
#         y_position -= table._height + line_spacing

#     def add_new_page():
#         """Adds a new page and resets the y_position."""
#         nonlocal y_position
#         c.showPage()
#         c.setFont("Helvetica", 12)
#         y_position = height - 50

#     # Add header
#     add_header()

#     # Add Total Contributions table
#     total_table_data = [["Purpose/Fund", "Total Amount"]]
#     for _, row in total_contributions.iterrows():
#         total_table_data.append([row['Reason'], f"${row['Total']:.2f}"])
#     add_table("Total Contributions by Purpose/Fund", total_table_data, [300, 100])

#     # Add Individual Contributions table
#     individual_table_data = [["Date", "Name", "Address", "Email Address", "Phone Number", "Purpose/Fund", "Amount", "Total"]]
#     for _, row in filtered_data.iterrows():
#         individual_table_data.append([
#             row['DATE'].strftime("%m/%d/%Y"),
#             row['Name'],
#             row['Address'],
#             row['Email Address'],
#             row['Phone Number'],
#             row['Reason'],
#             f"${row['Amount']:.2f}",
#             f"${row['Total']:.2f}",
#         ])

#     # Break the individual contributions into chunks for pages
#     rows_per_page = 20
#     for i in range(0, len(individual_table_data), rows_per_page):
#         chunk = individual_table_data[i:i + rows_per_page]
#         add_table("List of Individual Contributions", chunk, [70, 100, 100, 100, 100, 100, 70, 70])

#     # Footer
#     if y_position < 100:
#         add_new_page()
#     c.setFont("Helvetica", 10)
#     c.drawString(margin, 30, "Unless otherwise noted, no goods or services were received in return for these contributions.")
#     c.save()

# # Generate the PDF
# output_file = "Final_Contribution_Report_From_JSON.pdf"
# generate_pdf(output_file)

# print(f"PDF generated: {output_file}")

import pandas as pd
from reportlab.lib.pagesizes import letter
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

# Drop unnecessary fields (those starting with "FIELD")
df = df.loc[:, ~df.columns.str.startswith("FIELD")]

# Ensure required columns exist
required_columns = ['Name', 'Amount', 'DATE', 'Address', 'Reason', 'Email Address', 'Phone Number']
for col in required_columns:
    if col not in df.columns:
        print(f"Column '{col}' is missing. Adding it as empty.")
        df[col] = ''  # Add missing column with default empty values

# Clean the Amount column
df['Amount'] = df['Amount'].replace(r'[\$,]', '', regex=True)  # Remove $ and commas
df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')  # Convert to numeric; invalid values become NaN
df = df.dropna(subset=['Amount'])  # Drop rows with invalid 'Amount'

# Add Total column
df['Total'] = df['Amount']

# Prepare filtered data
filtered_data = df[['Name', 'Amount', 'DATE', 'Address', 'Reason', 'Email Address', 'Phone Number', 'Total']].copy()
filtered_data['DATE'] = pd.to_datetime(filtered_data['DATE'], errors='coerce')  # Convert DATE column to datetime
filtered_data = filtered_data.dropna(subset=['DATE'])  # Drop rows with invalid DATE values
filtered_data = filtered_data.sort_values('DATE')

# Aggregate contributions
total_contributions = filtered_data.groupby('Reason')['Total'].sum().reset_index()

# Extract the first and last name dynamically
first_and_last_name = filtered_data['Name'].dropna().iloc[0] if not filtered_data['Name'].dropna().empty else "First and Last Name"

# PDF generation function
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
        c.drawString(width - 200, y_position, "Period: 01/01/2024 - 12/31/2024")
        y_position -= line_spacing
        c.drawString(width - 200, y_position, "As of: 03/23/2025")
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

        # Draw the table with adjusted column widths
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
    total_table_data = [["Purpose/Fund", "Total Amount"]]
    for _, row in total_contributions.iterrows():
        total_table_data.append([row['Reason'], f"${row['Total']:.2f}"])
    add_table("Total Contributions by Purpose/Fund", total_table_data, [300, 150])

    # Add Individual Contributions table
    individual_table_data = [["Date", "Name", "Address", "Email Address", "Phone Number", "Purpose/Fund", "Amount", "Total"]]
    for _, row in filtered_data.iterrows():
        individual_table_data.append([
            row['DATE'].strftime("%m/%d/%Y"),
            row['Name'],
            row['Address'],
            row['Email Address'],
            row['Phone Number'],
            row['Reason'],
            f"${row['Amount']:.2f}",
            f"${row['Total']:.2f}",
        ])

    # Adjust column widths for better layout
    col_widths = [70, 100, 150, 120, 100, 120, 70, 70]
    add_table("List of Individual Contributions", individual_table_data, col_widths)

    # Footer
    if y_position < 100:
        add_new_page()
    c.setFont("Helvetica", 10)
    c.drawString(margin, 30, "Unless otherwise noted, no goods or services were received in return for these contributions.")
    c.save()

# Generate the PDF
output_file = "Final_Contribution_Report_Properly_Formatted.pdf"
generate_pdf(output_file)

print(f"PDF generated: {output_file}")
