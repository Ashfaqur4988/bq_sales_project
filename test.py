import os
from dotenv import load_dotenv

load_dotenv()

from google.cloud import bigquery

print("Creds path:", os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

client = bigquery.Client()

query = "SELECT 1 as test"

results = client.query(query).result()

for row in results:
    print(row)