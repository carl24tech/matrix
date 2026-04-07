import tkinter as tk
from tkinter import filedialog, messagebox
import pikepdf
import os
from pathlib import Path

def select_pdf():
    root = tk.Tk()
    root.withdraw()
    
    file_path = filedialog.askopenfilename(
        title="Select Locked PDF",
        filetypes=[("PDF files", "*.pdf")]
    )
    
    if not file_path:
        messagebox.showinfo("Cancelled", "No file selected.")
        return None
    
    return file_path

def get_password():
    dialog = tk.Tk()
    dialog.title("Enter Password")
    dialog.geometry("350x120")
    dialog.resizable(False, False)
    
    tk.Label(dialog, text="Enter the password for this PDF:", pady=10).pack()
    
    password_var = tk.StringVar()
    entry = tk.Entry(dialog, textvariable=password_var, show="*", width=30)
    entry.pack(pady=5)
    entry.focus()
    
    result = {"password": None}
    
    def on_submit():
        result["password"] = password_var.get()
        dialog.destroy()
    
    def on_cancel():
        dialog.destroy()
    
    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=10)
    
    tk.Button(button_frame, text="Unlock", command=on_submit, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.LEFT, padx=5)
    
    entry.bind('<Return>', lambda e: on_submit())
    
    dialog.protocol("WM_DELETE_WINDOW", on_cancel)
    dialog.mainloop()
    
    return result["password"]

def get_save_path(original_path):
    original = Path(original_path)
    suggested_name = f"{original.stem}_unlocked{original.suffix}"
    suggested_path = original.parent / suggested_name
    
    root = tk.Tk()
    root.withdraw()
    
    save_path = filedialog.asksaveasfilename(
        title="Save Unlocked PDF As",
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        initialfile=suggested_name,
        initialdir=original.parent
    )
    
    return save_path

def unlock_pdf(input_path, password, output_path):
    try:
        with pikepdf.open(input_path, password=password) as pdf:
            pdf.save(output_path)
        return True, None
    except pikepdf.PasswordError:
        return False, "Incorrect password."
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    input_path = select_pdf()
    if not input_path:
        return
    
    password = get_password()
    if password is None:
        return
    
    if password == "":
        password = ""
    
    output_path = get_save_path(input_path)
    if not output_path:
        messagebox.showinfo("Cancelled", "Operation cancelled.")
        return
    
    success, error_msg = unlock_pdf(input_path, password, output_path)
    
    if success:
        messagebox.showinfo("Success", f"PDF unlocked successfully!\nSaved to:\n{output_path}")
    else:
        messagebox.showerror("Error", error_msg)

if __name__ == "__main__":
    main()
