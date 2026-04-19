from flask import Blueprint, jsonify
from services.analytics_services import *
from middlewares.auth_middleware import token_required, admin_required

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/sales")
@token_required
def sales():
    """
    Get top 10 sales data
    ---
    tags:
      - Analytics
    responses:
      200:
        description: Returns the top 10 sales data records
        examples:
          application/json: [{"id": 1, "product": "Widget A", "sale_amount": 1500}, {"id": 2, "product": "Widget B", "sale_amount": 1200}]
    """
    return jsonify(get_10_sales_data())

@analytics_bp.route("/total-sales")
@token_required
def total_sales():
    """
    Get total sales
    ---
    tags:
      - Analytics
    responses:
      200:
        description: Returns the total aggregated sales data
        examples:
          application/json: {"total_sales": 150000}
    """
    return jsonify(get_total_sales())

@analytics_bp.route("/sales-by-region")
@token_required
def region_sales():
    """
    Get sales grouped by region
    ---
    tags:
      - Analytics
    responses:
      200:
        description: Returns sales statistics segmented by region
        examples:
          application/json: {"North": 50000, "South": 70000, "East": 30000}
    """
    return jsonify(sales_by_region())

@analytics_bp.route("/predict/<int:day>")
@token_required
@admin_required
def predict(day):
    """
    Predict sales for a specific day
    ---
    tags:
      - Analytics
    parameters:
      - in: path
        name: day
        type: integer
        required: true
        description: The day number to predict sales for
        example: 30
    responses:
      200:
        description: Returns the predicted sales amount for the specified day
        examples:
          application/json: {"predicted_sales": 5400}
    """
    return jsonify(predict_sales(day))

@analytics_bp.route("/customer-segments")
@token_required
@admin_required
def customer_segments():
    """
    Get customer segmentation data
    ---
    tags:
      - Analytics
    responses:
      200:
        description: Returns data outlining distinct customer segments
        examples:
          application/json: {"Low Value": 300, "Mid Value": 150, "High Value": 50}
    """
    return jsonify(get_customer_segments())
