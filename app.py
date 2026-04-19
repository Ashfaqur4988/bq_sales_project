from flask import Flask
from flasgger import Swagger
from routes.analytics_routes import analytics_bp
from routes.file_upload_route import file_bp
from routes.auth_routes import auth_bp
from routes.rag_routes import rag_bp
from database import db
from flask_migrate import Migrate
import config

# Import models so alembic can pick them up
import models.user_model 

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS

db.init_app(app)
migrate = Migrate(app, db)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

swagger_template = {
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "\nJWT Token. Format: \"Bearer {token}\""
        }
    },
    "security": [
        {
            "Bearer": []
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(analytics_bp, url_prefix="/analytics")
app.register_blueprint(file_bp, url_prefix="/file")
app.register_blueprint(rag_bp, url_prefix="/rag")

@app.route("/")
def home():
    """
    Root endpoint to check API status
    ---
    responses:
      200:
        description: Returns a success message if the API is running
    """
    return {"message": "analytics api running"}

# Global Error Handler
from werkzeug.exceptions import HTTPException
from flask import jsonify

@app.errorhandler(Exception)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    if isinstance(e, HTTPException):
        response = e.get_response()
        # replace the body with JSON
        response.data = jsonify({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }).data
        response.content_type = "application/json"
        return response
        
    # Return JSON for non-HTTP exceptions
    return jsonify({
        "code": 500,
        "name": "Internal Server Error",
        "description": "An unexpected error occurred: " + str(e)
    }), 500

if __name__ == "__main__":
    app.run(debug=True)