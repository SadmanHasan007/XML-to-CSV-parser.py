import tkinter as tk
from tkinter import filedialog
import csv
import requests
import xml.etree.ElementTree as ET

def strip_namespace(tag):
    """Remove namespace from the tag."""
    return tag.split('}')[-1] if '}' in tag else tag

def get_dynamic_fieldnames(root):
    """
    Extract dynamic field names and map stripped names to full names
    to support value extraction and CSV headers.
    """
    if not root.findall(".//item"):
        print("No <item> tags found in the XML.")
        return {}

    fieldnames = {}
    for item in root.findall(".//item"):
        for child in item:
            if child.text and child.text.strip():
                stripped = strip_namespace(child.tag)
                fieldnames[stripped] = child.tag  # map Capitalized -> full tag with ns
    return fieldnames

def convert_to_csv(xml_content, output_file):
    """Convert XML content to CSV dynamically based on XML structure."""
    try:
        root = ET.fromstring(xml_content)
        fieldname_map = get_dynamic_fieldnames(root)

        if not fieldname_map:
            status_label.config(text="No usable data found in XML.")
            return

        # Capitalize headers
        fieldnames = [name.capitalize() for name in fieldname_map.keys()]
        original_tags = {name.capitalize(): fieldname_map[name] for name in fieldname_map}

        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for item in root.findall('.//item'):
                row = {
                    header: (
                        item.find(original_tags[header]).text.strip()
                        if item.find(original_tags[header]) is not None and item.find(original_tags[header]).text
                        else ''
                    )
                    for header in fieldnames
                }
                writer.writerow(row)

        status_label.config(text=f"CSV file created successfully: {output_file}")
    except ET.ParseError:
        status_label.config(text="Error parsing the XML file. Please check its structure.")
    except Exception as e:
        status_label.config(text=f"An error occurred: {e}")

def upload_file():
    """Open file manager for XML file selection."""
    global file_path
    file_path = filedialog.askopenfilename(
        title="Select XML File",
        filetypes=[("XML Files", "*.xml"), ("All Files", "*.*")]
    )
    if file_path:
        status_label.config(text=f"Selected file: {file_path}")
    else:
        status_label.config(text="No file selected!")

def paste_url():
    """Handle URL input."""
    global rss_url
    rss_url = rss_url_entry.get()
    if rss_url:
        status_label.config(text=f"Pasted URL: {rss_url}")
    else:
        status_label.config(text="No URL provided!")

def convert_data():
    """Convert XML file or URL after user clicks Convert."""
    if file_path:
        save_path = filedialog.asksaveasfilename(
            title="Save CSV File As",
            initialfile="untitled.csv",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )
        if save_path:
            with open(file_path, 'r', encoding='utf-8') as xml_file:
                xml_content = xml_file.read()
            convert_to_csv(xml_content, save_path)
        else:
            status_label.config(text="File save canceled.")
    elif rss_url:
        save_path = filedialog.asksaveasfilename(
            title="Save CSV File As",
            initialfile="untitled.csv",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )
        if save_path:
            try:
                response = requests.get(rss_url)
                response.raise_for_status()
                convert_to_csv(response.text, save_path)
            except requests.exceptions.RequestException as e:
                status_label.config(text=f"Error fetching URL: {e}")
        else:
            status_label.config(text="File save canceled.")
    else:
        status_label.config(text="No input provided. Please upload a file or paste a URL.")

# Initialize global variables
file_path = None
rss_url = None

# Create GUI
root = tk.Tk()
root.title("XML to CSV Converter")

# Upload XML File Section
tk.Label(root, text="Upload XML File:").pack()
upload_button = tk.Button(root, text="Choose File", command=upload_file)
upload_button.pack()

# Paste RSS URL Section
tk.Label(root, text="Enter RSS URL:").pack()
rss_url_entry = tk.Entry(root, width=50)
rss_url_entry.pack()
paste_url_button = tk.Button(root, text="Paste URL", command=paste_url)
paste_url_button.pack()

# Convert Button
convert_button = tk.Button(root, text="Convert Data", command=convert_data)
convert_button.pack()

# Status Label
status_label = tk.Label(root, text="")
status_label.pack()

root.mainloop()
