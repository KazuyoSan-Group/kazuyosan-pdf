# Import Packages
from flask import Flask, jsonify, redirect, render_template, request
from google.cloud import storage
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
import os
import uuid

# Initialization
app = Flask(__name__)
id = uuid.uuid1()
id_generator = id.hex
storage_client = storage.Client.from_service_account_json("service_account/cloud-storage") # Use ("/service_account/cloud_storage") for deploying in Cloud Run and call volume from Secret Manager
bucket = storage_client.bucket("kazuyosan-pdf")

# Routes
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/compress", methods=["POST"])
def compress():
    # Request file
    file = request.files["berkas"]
    
    if file:
        name = file.filename
        check_extension = name.split(".")
        
        # Check extension
        if check_extension[len(check_extension) - 1] != "pdf":
            return jsonify(
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
        return jsonify(
            {
                "status": "Error (File)",
                "description": "Please add the file"
            }
            )

@app.route("/decrypt", methods=["POST"])
def decrypt():
    # Request file
    file = request.files["berkas"]
    password = request.form["password"]
    
    if file:
        name = file.filename
        check_extension = name.split(".")
        
        # Check extension
        if check_extension[len(check_extension) - 1] != "pdf":
            return jsonify(
                {
                    "status": "Error (File)",
                    "description": "Wrong file extension. Make sure extension is .pdf"
                }
                )
        
        file.save(name) # Save file in local
        reader = PdfReader(name, strict=False)
        writer = PdfWriter()
        
        # Decrypt process
        if reader.is_encrypted:
            reader.decrypt(password)
        
        # Write page
        for page in reader.pages:
            writer.add_page(page)
        
        # Write page to file 
        with open ("result/decrypt-" + id_generator + ".pdf", "wb") as f:
            writer.write(f)
        
        # Uploaded file to GCS
        blob = bucket.blob("decrypt-" + id_generator + ".pdf")
        blob.upload_from_filename("result/decrypt-" + id_generator + ".pdf")
        
        # Make public and get link
        blob.make_public()
        
        # Delete all processing file
        os.remove(name)
        os.remove("result/decrypt-" + id_generator + ".pdf") 
        
        return blob.public_url
    else:
        return jsonify(
            {
                "status": "Error (File)",
                "description": "Please add the file"
            }
            )
            
@app.route("/encrypt", methods=["POST"])
def encrypt():
    # Request file
    file = request.files["berkas"]
    password = request.form["password"]
    
    if file:
        name = file.filename
        check_extension = name.split(".")
        
        # Check extension
        if check_extension[len(check_extension) - 1] != "pdf":
            return jsonify(
                {
                    "status": "Error (File)",
                    "description": "Wrong file extension. Make sure extension is .pdf"
                }
                )
        
        file.save(name) # Save file in local
        reader = PdfReader(name, strict=False)
        writer = PdfWriter()
        
        # Write page
        for page in reader.pages:
            writer.add_page(page)
        
        # Encrypt process
        writer.encrypt(password)
        
        # Write page to file 
        with open ("result/encrypt-" + id_generator + ".pdf", "wb") as f:
            writer.write(f)
        
        # Uploaded file to GCS
        blob = bucket.blob("encrypt-" + id_generator + ".pdf")
        blob.upload_from_filename("result/encrypt-" + id_generator + ".pdf")
        
        # Make public and get link
        blob.make_public()
        
        # Delete all processing file
        os.remove(name)
        os.remove("result/encrypt-" + id_generator + ".pdf") 
        
        return blob.public_url
    else:
        return jsonify(
            {
                "status": "Error (File)",
                "description": "Please add the file"
            }
            )
            
@app.route("/merge", methods=["POST"])
def merge():
    # Request file
    req_file = request.files.getlist("listGambar")
    file = {}
    
    # Get all uploaded file
    for x in range(len(req_file)):
        file[x] = req_file[x]
    
    if file:
        # Check extension
        for x in file:
            name = file[x].filename
            check_extension = name.split(".")
            
            if check_extension[len(check_extension) - 1] != "pdf":
                return jsonify(
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
        return jsonify(
            {
                "status": "Error (File)",
                "description": "Please add the file"
            }
            )
        
# APP Run
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True) 
