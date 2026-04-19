from functools import wraps
from flask import request, jsonify, g
import jwt
from config import SECRET_KEY
from models.user_model import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            parts = request.headers["Authorization"].split()
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]
        
        if not token:
            return jsonify({"message": "Token is missing!"}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.filter_by(id=data["user_id"]).first()
            if not current_user:
                raise Exception("User not found")
        except Exception as e:
            return jsonify({"message": "Token is invalid or expired!"}), 401
            
        g.user = current_user
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(g, 'user') or not g.user:
            return jsonify({"message": "Authentication required!"}), 401
        if not g.user.is_admin:
            return jsonify({"message": "Admin access required!"}), 403
        return f(*args, **kwargs)
    return decorated
