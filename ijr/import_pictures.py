import frappe
import os
import sys

def execute():
    folder_to_import = '/path/to/folder'

    # Check if folder exists
    if not os.path.exists(folder_to_import):
        frappe.throw(f"Folder not found: {folder_to_import}")

    file_types = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.heic', '.heif')

    # Get all files in the folder recursively
    for root, dirs, files in os.walk(folder_to_import):
        for file in files:
            if file.endswith(file_types):
                parts = file.split('-')
                if len(parts) > 1:
                    theme = parts[0]
                    filename = parts[1]
                    fullpath = os.path.join(root, file)
                    if theme in ('Diversity', 'Human Resources', 'Trends', 'Infrastructure', 'Workload', 'Budgets'):
                        import_picture(fullpath, theme)
                    else:
                        import_picture(fullpath)
                else:
                    import_picture(fullpath)

def import_picture(filename, theme=None):
    print(f"Filename: {filename}, Theme: {theme}")

    with open(filename, 'rb') as f:
        file = frappe.new_doc("File")
        file.content = f.read()
        file.file_name = os.path.basename(filename)
        file.is_private = False
        file.save()
        file.reload()

    picture = frappe.new_doc("IJR Picture")
    picture.image = file.file_url
    picture.theme = theme
    picture.save()
    print(f"Saved picture: {picture.image}")
