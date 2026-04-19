import os
from dotenv import load_dotenv

load_dotenv()
from google.cloud import bigquery

client = bigquery.Client()

def run_query(query):
    query_job = client.query(query)
    results = query_job.result()
    return [dict(row) for row in results]

def get_10_sales_data():
    query ="""
    SELECT * 
FROM `fast-cascade-338616.sales_analytics.sales_data`
LIMIT 10;
    """
    return run_query(query)

def get_total_sales():
    query = """
    SELECT SUM(sales) as total_sales
    FROM `fast-cascade-338616.sales_analytics.sales_data`
    """
    return run_query(query)

def sales_by_region():
    query = """
    SELECT region, SUM(sales) as total_sales
    FROM `fast-cascade-338616.sales_analytics.sales_data`
    GROUP BY region
    ORDER BY total_sales DESC
    """
    return run_query(query)

def sales_trend():
    query = """
    SELECT order_date, SUM(sales) as total_sales
    FROM `fast-cascade-338616.sales_analytics.sales_data`
    GROUP BY order_date
    ORDER BY order_date
    """
    return run_query(query)

def predict_sales(day):
    query = f"""
    SELECT predicted_sales
    FROM ML.PREDICT(
      MODEL `fast-cascade-338616.sales_analytics.sales_forecast`,
      (SELECT {day} AS day)
    )
    """
    return run_query(query)

def get_customer_segments():
    query = """
    SELECT
      customer_id,
      total_spent,
      total_orders,
      centroid_id
    FROM ML.PREDICT(
      MODEL `fast-cascade-338616.sales_analytics.customer_segmentation`,
      (
        SELECT
          customer_id,
          SUM(CAST(sales AS FLOAT64)) AS total_spent,
          COUNT(*) AS total_orders
        FROM `fast-cascade-338616.sales_analytics.sales_data`
        GROUP BY customer_id
      )
    )
    """
    return run_query(query)