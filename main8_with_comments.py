# Import required libraries
import pandas as pd  # For data manipulation and processing
from reportlab.lib.pagesizes import letter, landscape  # For PDF page dimensions
from reportlab.pdfgen import canvas  # For generating PDF files
from reportlab.platypus import Table, TableStyle  # For creating tables in PDFs
from reportlab.lib import colors  # For table styling colors
import json  # For working with JSON files
import os  # For creating directories and file paths

# Load JSON file
file_path = "Dummy Data3.json"  # Path to the JSON file containing the data
with open(file_path, "r") as file:
    data = json.load(file)  # Load JSON data into a Python dictionary

# Convert JSON to DataFrame
df = pd.DataFrame(data)  # Convert JSON data to a pandas DataFrame

# Drop unnecessary fields
df = df.loc[:, ~df.columns.str.startswith("FIELD")]  # Remove columns starting with 'FIELD'

# Ensure required columns exist
required_columns = ['Name', 'Amount', 'DATE', 'Address', 'Reason', 'Email Address', 'Phone Number']
for col in required_columns:
    if col not in df.columns:  # Check if the column is missing
        df[col] = ''  # Add missing column with default empty values

# Clean the Amount column
df['Amount'] = df['Amount'].replace(r'[\$,]', '', regex=True)  # Remove '$' and ',' from Amount values
df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')  # Convert Amount to numeric, set invalid values to NaN
df = df.dropna(subset=['Amount'])  # Drop rows with invalid or missing Amount values

# Add Total column
df['Total'] = df['Amount']  # Create a Total column, initially the same as Amount

# Prepare directory for PDF reports
output_dir = "Individual_Reports"  # Directory to store the generated PDF reports
os.makedirs(output_dir, exist_ok=True)  # Create the directory if it does not exist

# Function to calculate column widths
def calculate_column_widths(page_width, margins):
    """
    Calculate proportional column widths for the table.
    """
    usable_width = page_width - 2 * margins  # Calculate usable page width after accounting for margins
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

# Generate individual PDF for each Name
for name, group in df.groupby('Name'):  # Group data by the 'Name' column
    # Filter and prepare data for the current individual
    filtered_data = group[['Name', 'Amount', 'DATE', 'Address', 'Reason', 'Email Address', 'Phone Number', 'Total']].copy()
    filtered_data['DATE'] = pd.to_datetime(filtered_data['DATE'], errors='coerce')  # Convert DATE to datetime
    filtered_data = filtered_data.dropna(subset=['DATE'])  # Drop rows with invalid or missing DATE values
    filtered_data = filtered_data.sort_values('DATE')  # Sort data by DATE

    # Aggregate contributions for this individual
    total_contributions = filtered_data.groupby('Reason')['Total'].sum().reset_index()  # Sum totals grouped by Reason

    # PDF generation function
    def generate_pdf(output_path, person_name):
        """
        Generate a PDF for the given individual.
        """
        c = canvas.Canvas(output_path, pagesize=landscape(letter))  # Create a canvas with landscape orientation
        page_width, page_height = landscape(letter)  # Get page dimensions
        margin = 50  # Margin size
        usable_width = page_width - 2 * margin  # Usable width for content
        y_position = page_height - 50  # Initial vertical position for content
        line_spacing = 20  # Spacing between lines

        # Function to add the header
        def add_header():
            nonlocal y_position
            c.setFont("Helvetica-Bold", 16)  # Set font for the title
            c.drawString(margin, y_position, "Contribution Statement")  # Title
            y_position -= line_spacing + 10
            c.setFont("Helvetica", 10)  # Set font for the name and period
            c.drawString(margin, y_position, person_name)  # Individual's name
            c.drawString(page_width - margin - 200, y_position, "Period: 01/01/2024 - 12/31/2024")  # Reporting period
            y_position -= line_spacing
            c.drawString(page_width - margin - 200, y_position, "As of: 03/23/2025")  # Date of report generation
            y_position -= line_spacing

        # Function to add a table
        def add_table(title, table_data, col_widths):
            nonlocal y_position
            if y_position < 100:  # Check if there is enough space for the table
                add_new_page()
            c.setFont("Helvetica-Bold", 12)  # Set font for the table title
            c.drawString(margin, y_position, title)  # Table title
            y_position -= line_spacing

            # Create and style the table
            table = Table(table_data, colWidths=col_widths, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Header background color
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Header text color
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Center-align header
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),  # Left-align content
                ('ALIGN', (-2, 1), (-1, -1), 'RIGHT'),  # Right-align Amount and Total
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Bold font for header
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Add gridlines
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Top-align content
                ('FONTSIZE', (0, 0), (-1, -1), 8),  # Font size for table content
                ('WORDWRAP', (0, 0), (-1, -1)),  # Enable text wrapping
                ('LEFTPADDING', (0, 0), (-1, -1), 4),  # Padding inside cells
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            table.wrapOn(c, page_width, page_height)  # Wrap table to fit the page
            table.drawOn(c, margin, y_position - table._height)  # Draw table
            y_position -= table._height + line_spacing

        # Function to add a new page
        def add_new_page():
            nonlocal y_position
            c.showPage()  # Create a new page
            c.setFont("Helvetica", 12)  # Reset font
            y_position = page_height - 50  # Reset vertical position

        add_header()  # Add the header

        # Add Total Contributions table
        total_table_data = [["Purpose/Fund", "Total Amount"]]  # Header row
        for _, row in total_contributions.iterrows():
            total_table_data.append([row['Reason'], f"${row['Total']:.2f}"])  # Data rows
        add_table("Total Contributions by Purpose/Fund", total_table_data, [usable_width * 0.7, usable_width * 0.3])

        # Add Individual Contributions table
        individual_table_data = [["Date", "Name", "Address", "Email Address", "Phone Number", "Purpose/Fund", "Amount", "Total"]]  # Header row
        for _, row in filtered_data.iterrows():
            individual_table_data.append([
                row['DATE'].strftime("%m/%d/%Y"),  # Format date
                row['Name'] if row['Name'] else "-",  # Default to '-' if Name is missing
                row['Address'] if row['Address'] else "-",  # Default to '-' if Address is missing
                row['Email Address'] if row['Email Address'] else "-",  # Default to '-' if Email Address is missing
                row['Phone Number'] if row['Phone Number'] else "-",  # Default to '-' if Phone Number is missing
                row['Reason'],  # Contribution purpose
                f"${row['Amount']:.2f}",  # Format Amount
                f"${row['Total']:.2f}",  # Format Total
            ])
        col_widths = calculate_column_widths(page_width, margin)  # Calculate column widths
        add_table("List of Individual Contributions", individual_table_data, col_widths)

        # Footer
        if y_position < 100:  # Ensure enough space for the footer
            add_new_page()
        c.setFont("Helvetica", 10)  # Set font for footer
        c.drawString(margin, 30, "Unless otherwise noted, no goods or services were received in return for these contributions.")  # Footer text
        c.save()  # Save the PDF

    # Generate PDF for this individual
    output_file = os.path.join(output_dir, f"{name.replace(' ', '_')}_Contribution_Report.pdf")  # File path
    generate_pdf(output_file, name)  # Generate the PDF

print(f"Individual reports have been generated in the '{output_dir}' directory.")  # Print completion message
