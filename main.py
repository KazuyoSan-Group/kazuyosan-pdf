# Import Packages
from flask import Flask, redirect, render_template, request
from google.cloud import storage
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
import json
import os
import uuid

# Initialization
app = Flask(__name__)
id = uuid.uuid1()
id_generator = id.hex
storage_client = storage.Client.from_service_account_json("/service_account/cloud-storage")
bucket = storage_client.bucket("kazuyosan-pdf")

# API Key
api_key = os.environ["API_KEY"] # Call API Key from Environment Variable

# Routes
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/compress", methods=["POST"])
def compress():
    # Request file and auth key
    auth = request.args.get("auth")
    file = request.files["berkas"]
    
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
            
            file.save(name) # Save file in local
            reader = PdfReader(name, strict=False)
            writer = PdfWriter()
            
            # Compress and write page
            for page in reader.pages:
                page.compress_content_streams() # Compress method
                writer.add_page(page)
            
            # Write page to file 
            with open ("result/compressed-" + id_generator + ".pdf", "wb") as f:
                writer.write(f)
            
            # Uploaded file to GCS
            blob = bucket.blob("compressed-" + id_generator + ".pdf")
            blob.upload_from_filename("result/compressed-" + id_generator + ".pdf")
            
            # Make public and get link
            blob.make_public()
            
            # Delete all processing file
            os.remove(name)
            os.remove("result/compressed-" + id_generator + ".pdf") 
            
            return redirect(blob.public_url)
        else:
            return json.dumps(
                {
                    "status": "Error (File)",
                    "description": "Please add the file"
                }
                )
                    
@app.route("/merge", methods=["POST"])
def merge():
    # Request file and auth key
    # auth = request.headers.get("auth")
    req_file = request.files.getlist("listGambar")
    file = {}
    
    # Get all uploaded file
    for x in range(len(req_file)):
        file[x] = req_file[x]
    
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
            # Check extension
            for x in file:
                name = file[x].filename
                check_extension = name.split(".")
                
                if check_extension[len(check_extension) - 1] != "pdf":
                    return json.dumps(
                        {
                            "status": "Error (File)",
                            "description": "Wrong file extension. Make sure extension is .pdf"
                        }
                        )
            
            # Save all file in local
            for x in file:
                file[x].save(file[x].filename) 
                
            merger = PdfMerger(strict=False)
            
            # Append file to merger
            for pdf in file:
                merger.append(file[pdf].filename)
            
            # Write append file to merged file
            merger.write("result/merged-" + id_generator + ".pdf")
            merger.close()
            
            # Uploaded file to GCS
            blob = bucket.blob("merged-" + id_generator + ".pdf")
            blob.upload_from_filename("result/merged-" + id_generator + ".pdf")
            
            # Make public and get link
            blob.make_public()
            
            # Delete all processing file
            for x in file:
                os.remove(file[x].filename)
            os.remove("result/merged-" + id_generator + ".pdf")
            
            return redirect(blob.public_url)
        else:
            return json.dumps(
                {
                    "status": "Error (File)",
                    "description": "Please add the file"
                }
                )
        
# APP Run
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
