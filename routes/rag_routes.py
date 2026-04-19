from flask import Blueprint, request, jsonify
from services.rag_services import process_document, ask_question
from utils.file_utils import save_file

rag_bp = Blueprint('rag_bp', __name__)

@rag_bp.route("/upload", methods=["POST"])
def upload():
    """
    Upload a document for RAG processing
    ---
    tags:
      - RAG
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: The document file to upload
    responses:
      200:
        description: Document processed successfully
      400:
        description: No file uploaded
    """
    file = request.files.get("file")

    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    file_path = save_file(file)

    result = process_document(file_path)

    return jsonify({"message": result})


@rag_bp.route("/ask", methods=["POST"])
def ask():
    """
    Ask a question based on uploaded documents
    ---
    tags:
      - RAG
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - query
          properties:
            query:
              type: string
              example: "What were the total sales in Q1?"
    responses:
      200:
        description: Answer generated successfully
      400:
        description: Query is required
    """
    data = request.json
    query = data.get("query")

    if not query:
        return jsonify({"error": "Query is required"}), 400

    answer = ask_question(query)

    return jsonify({"answer": answer})