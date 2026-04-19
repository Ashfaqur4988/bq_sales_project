from google.cloud import storage
from config import GCP_BUCKET_NAME

# create client once (important)
client = storage.Client()
bucket = client.bucket(GCP_BUCKET_NAME)


def upload_file(file, filename):
    blob = bucket.blob(filename)
    blob.upload_from_file(file)
    return filename


def download_file(filename):
    blob = bucket.blob(filename)
    return blob.download_as_bytes()


def read_file(filename):
    blob = bucket.blob(filename)
    return blob.download_as_text()