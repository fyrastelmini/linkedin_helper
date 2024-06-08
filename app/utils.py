import requests

# ______________________________ functions ______________________________________


# Function to handle different upload statuses
def message_handler(upload_status):
    if upload_status == "success":
        message = "File uploaded successfully"
    elif upload_status == "no_file":
        message = "No file uploaded, new file created"
    elif upload_status == "error":
        message = "Incorrect file, new file created"
    elif upload_status == "file_too_large":
        message = "Uploaded file is too large, new file created"
    elif upload_status == "empty":
        message = "Uploaded file is empty, new file created"
    elif upload_status == "new":
        message = "New file created successfully"
    elif upload_status == "new_line_ok":
        message = f"New line added successfully, current number of lines is: "
    elif upload_status == "new_line_no":
        message = f"Invalid line, current number of lines is: "
    else:
        message = ""
    return message
