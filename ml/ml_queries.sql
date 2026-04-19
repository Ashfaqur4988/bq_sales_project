#Sales Prediction Model
CREATE OR REPLACE MODEL `fast-cascade-338616.sales_analytics.sales_forecast`
OPTIONS(
  model_type='linear_reg',
  input_label_cols=['sales']
) AS

SELECT
  EXTRACT(DAYOFYEAR FROM date) AS day,
  CAST(sales AS FLOAT64) AS sales
FROM `fast-cascade-338616.sales_analytics.sales_data`;

#Predict Future Sales

SELECT *
FROM ML.PREDICT(
  MODEL `fast-cascade-338616.sales_analytics.sales_forecast`,
  (SELECT 120 AS day)
);

#Customer Segmentation (K-Means)

CREATE OR REPLACE MODEL `fast-cascade-338616.sales_analytics.customer_segmentation`
OPTIONS(
  model_type='kmeans',
  num_clusters=3
) AS

SELECT
  customer_id,
  SUM(CAST(sales AS FLOAT64)) AS total_spent,
  COUNT(*) AS total_orders
FROM `fast-cascade-338616.sales_analytics.sales_data`
GROUP BY customer_id;

-- Predict Customer Segments

SELECT *
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
);