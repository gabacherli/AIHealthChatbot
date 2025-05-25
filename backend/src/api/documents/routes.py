"""
Document routes.
This module contains the routes for document management.
"""
import os
import logging
from flask import request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt
from werkzeug.utils import secure_filename
from ...services.document_service import DocumentService
from ...config import get_config

from . import documents_bp

# Set up logging
logger = logging.getLogger(__name__)

config = get_config()
document_service = DocumentService()

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

@documents_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_document():
    """
    Upload a document.

    Returns:
        A JSON response with the upload status.
    """
    # Get user info from JWT token
    claims = get_jwt()
    username = claims.get("sub", "anonymous")  # JWT sub contains username
    user_id = claims.get("user_id", "anonymous")  # Get actual user ID from additional claims
    user_role = claims.get("role", "patient")

    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        # Process the file
        try:
            # Create user-specific upload directory if it doesn't exist (use username for folder)
            upload_dir = os.path.join(config.UPLOAD_FOLDER, username)
            os.makedirs(upload_dir, exist_ok=True)
            # Save the file
            file_path = os.path.join(upload_dir, filename)
            file.save(file_path)

            # Process and store the document
            document_id = document_service.process_and_store_document(
                file_path,
                filename,
                user_role=user_role,
                user_id=user_id
            )

            return jsonify({
                "message": "Document uploaded and processed successfully",
                "document_id": document_id,
                "filename": filename
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "File type not allowed"}), 400

@documents_bp.route("/list", methods=["GET"])
@jwt_required()
def list_documents():
    """
    List all documents for the current user.

    Returns:
        A JSON response with the list of documents.
    """
    try:
        # Get user ID
        claims = get_jwt()
        user_id = claims.get("user_id", "anonymous")  # Get actual user ID from additional claims

        # Get documents for the user (use user_id for filtering)
        documents = document_service.get_documents_by_user(str(user_id))

        return jsonify({"documents": documents})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@documents_bp.route("/download/<filename>", methods=["GET"])
@jwt_required()
def download_document(filename):
    """
    Download a document with enhanced medical image support.

    Args:
        filename: The name of the file to download.

    Returns:
        The file for download.
    """
    try:
        # Get user ID
        claims = get_jwt()
        username = claims.get("sub", "anonymous")  # JWT sub contains username

        # Secure the filename
        secure_name = secure_filename(filename)

        # First, try to get the file from the file system (standard approach)
        upload_dir = os.path.abspath(os.path.join(config.UPLOAD_FOLDER, username))
        file_path = os.path.join(upload_dir, secure_name)

        if os.path.exists(file_path):
            # File exists on disk - serve it directly
            return send_from_directory(
                upload_dir,
                secure_name,
                as_attachment=True
            )

        # If file not found on disk, check if it's a medical image stored in the database
        # Try to retrieve medical image data from the database (use username for file path)
        image_data = document_service.get_medical_image_data(secure_name, username)

        if image_data:

            # Determine content type based on file extension
            file_ext = secure_name.lower().split('.')[-1] if '.' in secure_name else ''
            content_type_map = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'gif': 'image/gif',
                'bmp': 'image/bmp',
                'tiff': 'image/tiff'
            }
            content_type = content_type_map.get(file_ext, 'application/octet-stream')

            # Create response with image data
            from flask import Response
            return Response(
                image_data,
                mimetype=content_type,
                headers={
                    'Content-Disposition': f'attachment; filename="{secure_name}"',
                    'Content-Length': str(len(image_data))
                }
            )

        # File not found anywhere
        return jsonify({"error": f"Medical image not found: {secure_name}"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@documents_bp.route("/delete/<filename>", methods=["DELETE"])
@jwt_required()
def delete_document(filename):
    """
    Delete a document.

    Args:
        filename: The name of the file to delete.

    Returns:
        A JSON response with the deletion status.
    """
    try:
        # Get user info from JWT token - use same logic as upload and list
        claims = get_jwt()
        user_id = claims.get("user_id", "anonymous")  # Get actual user ID from additional claims

        # Secure the filename
        secure_name = secure_filename(filename)

        # Check if document exists before deletion attempt
        documents_before = document_service.get_documents_by_user(str(user_id))
        doc_exists = any(doc['filename'] == secure_name for doc in documents_before)

        if not doc_exists:
            return jsonify({
                "error": "Document not found or you do not have permission to delete it"
            }), 404

        # Delete the document using the same user_id format as used in listing
        num_deleted = document_service.delete_document(secure_name, str(user_id))

        # Verify deletion by checking if document still exists
        documents_after = document_service.get_documents_by_user(str(user_id))
        doc_still_exists = any(doc['filename'] == secure_name for doc in documents_after)

        if num_deleted > 0 and not doc_still_exists:
            return jsonify({
                "message": "Document deleted successfully",
                "chunks_deleted": num_deleted,
                "verified": True
            })
        elif not doc_still_exists:
            # Document was deleted but count might be wrong
            return jsonify({
                "message": "Document deleted successfully",
                "chunks_deleted": 1,
                "verified": True
            })
        else:
            return jsonify({
                "error": "Document deletion failed - document still exists"
            }), 500
    except Exception as e:
        logger.error(f"Error deleting document {filename}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@documents_bp.route("/search", methods=["POST"])
@jwt_required()
def search_documents():
    """
    Search for documents.

    Returns:
        A JSON response with the search results.
    """
    data = request.get_json()
    query = data.get("query", "")

    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        # Get user info for filtering
        claims = get_jwt()
        user_id = claims.get("sub", "anonymous")
        user_role = claims.get("role", "patient")

        # Get optional filters
        filters = data.get("filters", {})

        # Add user ID and role to filters if not explicitly provided
        if "user_id" not in filters:
            filters["user_id"] = user_id

        if "user_role" not in filters:
            filters["user_role"] = user_role

        # Search for documents
        results = document_service.search_documents(query, filters)

        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
