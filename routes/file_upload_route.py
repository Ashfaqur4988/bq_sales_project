from flask import Blueprint, request, send_file, jsonify
import io
from middlewares.auth_middleware import token_required, admin_required

from services.file_upload_service import (
    upload_file,
    download_file,
    read_file
)

file_bp = Blueprint("file", __name__)


@file_bp.route("/upload", methods=["POST"])
@token_required
@admin_required
def upload():
    """
    Upload a file
    ---
    tags:
      - Files
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: The file to upload
    responses:
      201:
        description: File uploaded successfully
        examples:
          application/json: {"message": "File uploaded", "filename": "sample.csv"}
      400:
        description: No file provided
        examples:
          application/json: {"error": "No file provided"}
    """
    if "file" not in request.files:
        return {"error": "No file provided"}, 400

    file = request.files["file"]
    filename = file.filename

    upload_file(file, filename)

    return {"message": "File uploaded", "filename": filename}, 201


@file_bp.route("/download/<filename>", methods=["GET"])
@token_required
@admin_required
def download(filename):
    """
    Download a file
    ---
    tags:
      - Files
    parameters:
      - in: path
        name: filename
        type: string
        required: true
        description: The name of the file to download
        example: "sample.csv"
    responses:
      200:
        description: A file download
    """
    file_bytes = download_file(filename)

    return send_file(
        io.BytesIO(file_bytes),
        download_name=filename,
        as_attachment=True
    )


@file_bp.route("/read/<filename>", methods=["GET"])
@token_required
@admin_required
def read_file_route(filename):
    """
    Read file content
    ---
    tags:
      - Files
    parameters:
      - in: path
        name: filename
        type: string
        required: true
        description: The name of the file to read
        example: "sample.csv"
    responses:
      200:
        description: The content of the file
        examples:
          application/json: {"filename": "sample.csv", "content": "col1,col2\nval1,val2"}
    """
    content = read_file(filename)

    return jsonify({
        "filename": filename,
        "content": content
    })