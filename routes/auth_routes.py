from flask import Blueprint, request, jsonify
from database import db
from models.user_model import User
import jwt
import datetime
from config import SECRET_KEY

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
            admin:
              type: boolean
    responses:
      201:
        description: User registered successfully
        examples:
          application/json: {"message": "User registered successfully!"}
      400:
        description: Validation error
    """
    data = request.get_json()
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"message": "Missing username or password"}), 400
    
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"message": "User already exists"}), 400
    
    is_admin = data.get("admin", False)
    
    new_user = User(username=data["username"], is_admin=is_admin)
    new_user.set_password(data["password"])
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully!"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login user
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful
        examples:
          application/json: {"token": "eyJhbGciOiJIUzI1NiIsInR5c...<jwt_token>"}
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"message": "Could not verify"}), 401
    
    user = User.query.filter_by(username=data["username"]).first()
    
    if user and user.check_password(data["password"]):
        token = jwt.encode({
            "user_id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY, algorithm="HS256")
        
        return jsonify({"token": token})
    
    return jsonify({"message": "Could not verify credentials"}), 401
