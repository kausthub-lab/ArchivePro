import tkinter as tk
from tkinter import filedialog, messagebox

# Manual ZIP File Creator with a User Interface
files_to_zip = []  # List to store selected files
output_zip_file = 'combined_files.zip'  # Default output ZIP file name

# Function to manually write a ZIP file structure
def write_zip(files, output):
    with open(output, 'wb') as zipf:
        file_offsets = []  # Stores offsets for each file's local header
        central_directory = []  # Stores central directory entries
        offset = 0  # Tracks the current byte offset in the ZIP file

        # Write local file headers and file content
        for file in files:
            try:
                with open(file, 'rb') as f:
                    data = f.read()

                # File metadata
                file_name = file.encode('utf-8')
                file_size = len(data)

                # Local file header
                file_header = (
                    b'\x50\x4b\x03\x04'  # Local file header signature
                    b'\x14\x00'  # Version needed to extract
                    b'\x00\x00'  # General purpose bit flag
                    b'\x00\x00'  # Compression method (0 = no compression)
                    b'\x00\x00\x00\x00'  # File modification time and date
                    b'\x00\x00\x00\x00'  # CRC-32 (zeros for simplicity)
                    + file_size.to_bytes(4, 'little')  # Compressed size
                    + file_size.to_bytes(4, 'little')  # Uncompressed size
                    + len(file_name).to_bytes(2, 'little')  # File name length
                    + b'\x00\x00'  # Extra field length
                    + file_name  # File name
                )

                # Write header and file content
                zipf.write(file_header)
                zipf.write(data)

                # Store the offset for the central directory
                file_offsets.append((file, offset))

                # Update the offset
                offset += len(file_header) + file_size

                print(f"Added {file} to ZIP archive.")

            except FileNotFoundError:
                print(f"File {file} not found. Skipping.")

        # Write central directory entries
        central_directory_offset = offset
        for file, file_offset in file_offsets:
            file_name = file.encode('utf-8')
            file_size = len(file_name)

            # Central directory file header
            central_directory_header = (
                b'\x50\x4b\x01\x02'  # Central directory file header signature
                b'\x14\x00'  # Version made by
                b'\x14\x00'  # Version needed to extract
                b'\x00\x00'  # General purpose bit flag
                b'\x00\x00'  # Compression method (0 = no compression)
                b'\x00\x00\x00\x00'  # File modification time and date
                b'\x00\x00\x00\x00'  # CRC-32 (zeros for simplicity)
                + file_size.to_bytes(4, 'little')  # Compressed size
                + file_size.to_bytes(4, 'little')  # Uncompressed size
                + len(file_name).to_bytes(2, 'little')  # File name length
                + b'\x00\x00'  # Extra field length
                + b'\x00\x00'  # File comment length
                + b'\x00\x00'  # Disk number start
                + b'\x00\x00'  # Internal file attributes
                + b'\x00\x00\x00\x00'  # External file attributes
                + file_offset.to_bytes(4, 'little')  # Relative offset of local header
                + file_name  # File name
            )

            central_directory.append(central_directory_header)
            offset += len(central_directory_header)

        # Write the central directory to the ZIP file
        for entry in central_directory:
            zipf.write(entry)

        # Write the end of central directory record
        end_of_central_directory = (
            b'\x50\x4b\x05\x06'  # End of central directory signature
            b'\x00\x00'  # Number of this disk
            b'\x00\x00'  # Disk where central directory starts
            + len(central_directory).to_bytes(2, 'little')  # Number of central directory records on this disk
            + len(central_directory).to_bytes(2, 'little')  # Total number of central directory records
            + sum(len(entry) for entry in central_directory).to_bytes(4, 'little')  # Size of central directory
            + central_directory_offset.to_bytes(4, 'little')  # Offset of start of central directory
            + b'\x00\x00'  # ZIP file comment length
        )

        zipf.write(end_of_central_directory)
        print(f"ZIP file {output} created successfully.")

# GUI functions
def add_files():
    global files_to_zip
    files = filedialog.askopenfilenames(title="Select Files to ZIP")
    files_to_zip.extend(files)
    file_list.delete(0, tk.END)
    for file in files_to_zip:
        file_list.insert(tk.END, file)

def create_zip():
    global output_zip_file
    if not files_to_zip:
        messagebox.showerror("Error", "No files selected to zip!")
        return

    output_zip_file = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("ZIP files", "*.zip")], title="Save ZIP File As")
    if output_zip_file:
        write_zip(files_to_zip, output_zip_file)
        messagebox.showinfo("Success", f"ZIP file created: {output_zip_file}")

# GUI setup
root = tk.Tk()
root.title("Manual ZIP Creator")

frame = tk.Frame(root)
frame.pack(pady=10)

add_button = tk.Button(frame, text="Add Files", command=add_files)
add_button.pack(side=tk.LEFT, padx=5)

create_button = tk.Button(frame, text="Create ZIP", command=create_zip)
create_button.pack(side=tk.LEFT, padx=5)

file_list = tk.Listbox(root, width=50, height=15)
file_list.pack(pady=10)

# Run the GUI event loop
root.mainloop()
