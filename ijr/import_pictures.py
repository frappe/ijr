import frappe
import os
import sys

# bench --site ijr.test execute ijr.import_pictures.execute --args "('<folder-path>',)"

def execute(folder_to_import):
    # Check if folder exists
    if not os.path.exists(folder_to_import):
        frappe.throw(f"Folder not found: {folder_to_import}")

    file_types = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.heic', '.heif')

    # Get all files in the folder recursively
    for root, dirs, files in os.walk(folder_to_import):
        for file in files:
            if file.endswith(file_types):
                parts = file.split('-')
                fullpath = os.path.join(root, file)
                if len(parts) > 1:
                    theme = parts[0]
                    filename = parts[1]
                    if theme in ('Diversity', 'Human Resources', 'Trends', 'Infrastructure', 'Workload', 'Budgets'):
                        # title should be filename without extension
                        title = os.path.splitext(filename)[0]
                        import_picture(fullpath, theme, title=title)
                    else:
                        import_picture(fullpath)
                else:
                    import_picture(fullpath)

def import_picture(filename, theme=None, title=None):
    print(f"Filename: {filename}, Theme: {theme}, Title: {title}")

    with open(filename, 'rb') as f:
        file = frappe.new_doc("File")
        file.content = f.read()
        base_name = os.path.basename(filename)
        # collapse spaces and replace with underscore
        file_name = '_'.join(base_name.split())
        file.file_name = file_name
        file.is_private = False
        file.save()
        file.reload()

    picture = frappe.new_doc("IJR Picture")
    picture.title = title or base_name
    picture.image = file.file_url
    picture.theme = theme
    picture.save()
    file.db_set({
        "attached_to_doctype": "IJR Picture",
        "attached_to_name": picture.name,
        "attached_to_field": "image"
    })
    print(f"Saved picture: {picture.image}")
