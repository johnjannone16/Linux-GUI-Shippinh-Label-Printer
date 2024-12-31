import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import fitz
import cv2
import pytesseract
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import inch
import os
import subprocess

def ai_crop_pdf_to_shipping_label(input_pdf_path, output_pdf_path, status_text):
    try:
        status_text.insert(tk.END, "Processing...\n")
        doc = fitz.open(input_pdf_path)
        pix = doc[0].get_pixmap(dpi=300)
        temp_image_path = "./temp_image.png"
        pix.save(temp_image_path)
        doc.close()

        image = cv2.imread(temp_image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        d = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        
        # Find bounding box
        x_min, y_min, x_max, y_max = float('inf'), float('inf'), 0, 0
        for i in range(len(d['text'])):
            if d['text'][i].strip():
                x, y, w, h = d['left'][i], d['top'][i], d['width'][i], d['height'][i]
                x_min = min(x_min, x)
                y_min = min(y_min, y)
                x_max = max(x_max, x + w)
                y_max = max(y_max, y + h)
        
        # Add padding for margins
        padding = 10
        x_min = max(x_min - padding, 0)
        y_min = max(y_min - padding, 0)
        x_max = min(x_max + padding, image.shape[1])
        y_max = min(y_max + padding, image.shape[0])
        cropped_image = image[y_min:y_max, x_min:x_max]

        # Check if output is landscape
        if cropped_image.shape[1] > cropped_image.shape[0]:  # width > height then landscape
            # Rotate the label 90 degrees counter-clockwise to make it portrait
            cropped_image = cv2.rotate(cropped_image, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # Calculate scaling factor for margins
        label_width, label_height = 4 * inch, 6 * inch
        margin = 1 / 16 * inch
        available_width = label_width - 2 * margin
        available_height = label_height - 2 * margin
        scale_x = available_width / cropped_image.shape[1]
        scale_y = available_height / cropped_image.shape[0]
        scale = min(scale_x, scale_y)

        # Save the cropped label temporarily to output as pdf
        cropped_image_path = "./cropped_image.png"
        cv2.imwrite(cropped_image_path, cropped_image)

        # Create a 4x6 canvas for the shipping label with margins
        c = canvas.Canvas(output_pdf_path, pagesize=(label_width, label_height))
        
        # Centering
        scaled_width = cropped_image.shape[1] * scale
        scaled_height = cropped_image.shape[0] * scale
        x_offset = (label_width - scaled_width) / 2
        y_offset = (label_height - scaled_height) / 2

        c.drawImage(
            cropped_image_path,
            x_offset, y_offset,
            width=scaled_width,
            height=scaled_height
        )
        c.save()

        # Clean up temporary files
        os.remove(temp_image_path)
        os.remove(cropped_image_path)

        # Print the label
        print_command = f"lp -d PRINTERNAMEINCUPS {output_pdf_path}"
        subprocess.run(print_command, shell=True, check=True)
        status_text.insert(tk.END, f"Printed USPS label to printer BY-482BT.\n")
    except Exception as e:
        status_text.insert(tk.END, f"An error occurred: {e}\n")

def select_input_file(entry):
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, file_path)

def select_output_file(entry):
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, file_path)

def start_conversion(input_entry, output_entry, status_text):
    input_path = input_entry.get()
    output_path = output_entry.get()
    if not os.path.isfile(input_path):
        messagebox.showerror("Error", "Invalid input file!")
        return
    if not output_path:
        messagebox.showerror("Error", "Please specify an output file!")
        return
    ai_crop_pdf_to_shipping_label(input_path, output_path, status_text)

# GUI init
root = tk.Tk()
root.title("Shipping Label Printer")

# Input file
tk.Label(root, text="Input PDF:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
input_entry = tk.Entry(root, width=50)
input_entry.grid(row=0, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=lambda: select_input_file(input_entry)).grid(row=0, column=2, padx=10, pady=5)

# Output file
tk.Label(root, text="Output PDF:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
output_entry = tk.Entry(root, width=50)
output_entry.grid(row=1, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=lambda: select_output_file(output_entry)).grid(row=1, column=2, padx=10, pady=5)

# Convert button
tk.Button(root, text="Convert", command=lambda: start_conversion(input_entry, output_entry, status_text)).grid(row=2, column=1, pady=10)

# Status area
tk.Label(root, text="Status:").grid(row=3, column=0, padx=10, pady=5, sticky="ne")
status_text = ScrolledText(root, width=60, height=10)
status_text.grid(row=3, column=1, columnspan=2, padx=10, pady=5)

root.mainloop()
