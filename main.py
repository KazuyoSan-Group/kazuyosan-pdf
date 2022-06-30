# Import Library
from flask import Flask, request
from PyPDF2 import PdfReader, PdfWriter
import json
import os

# Intialization Flask
app = Flask(__name__)

# API Key
api_key = "23870787-0181-4c26-be24-c8d7f4ec1c3d"

# Routes
@app.route("/")
def index():
    return json.dumps(
        {
            "status": "Success",
            "description": "Hello and welcome to KazuyoSan PDF"
        }
        )
    
@app.route("/compress", methods=["POST"])
def compress():
    # Request file and auth key
    auth = request.headers.get("auth")
    file = request.files["file"]
    
    # Check auth null
    if auth == "":
        return json.dumps(
            {
                "status": "Error (Authentication)",
                "description": "Auth key can't be null"
            }
            )
    # Check credentials
    elif auth != api_key:
        return json.dumps(
        {
            "status": "Error (Authentication)",
            "description": "Wrong auth key"
        }
        )
    else:
        if file:
            name = file.filename
            check_extension = name.split(".")
            
            # Check extension
            if check_extension[len(check_extension) - 1] != "pdf":
                return json.dumps(
                    {
                        "status": "Error (File)",
                        "description": "Wrong file extension. Make sure extension is .pdf"
                    }
                    )
            
            file.save(name)
            reader = PdfReader(name)
            writer = PdfWriter()
            
            # Compress and write page
            for page in reader.pages:
                page.compress_content_streams() # Compress method
                writer.add_page(page)
            
            os.remove(name) # Delete uploaded file
            
            # Write page to file 
            with open ("result-" + name, "wb") as f:
                writer.write(f)
            
            return json.dumps(
                {
                    "status": "Success",
                    "link": ""
                }
                )
        else:
            return json.dumps(
                {
                    "status": "Error (File)",
                    "description": "Please add the file"
                }
                )
        
# APP Run
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)