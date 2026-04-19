# BQ Sales Analytics API

Welcome to the **BQ Sales Analytics API**. This project serves as a comprehensive backend system built in Python (Flask) that interfaces with advanced machine learning predictive models and Google Cloud Platform (GCP) resources, delivering robust predictive and descriptive sales analytics data along with secure file upload/download operations.

## Key Features
- **Data Analytics:** Real-time descriptive reporting (e.g., top 10 sales, segmented metrics, regional performance) and predictive analytics for future sales forecasting.
- **Secure File Storage:** Endpoints for uploading, reading, and downloading system files securely.
- **Robust Security:** JWT-based user authentication integrated fully with a managed PostgreSQL connection (`Flask-SQLAlchemy`).
- **Role-Based Access Control (RBAC):** Privileged API routing defining what regular users versus administrative users can see and execute.
- **Global Error Handling:** All errors (from missing files to internal server crashes) are gracefully captured and returned as consistent JSON payloads.
- **Swagger Documentation:** Auto-generated interactive GUI (`flasgger`) mapping out all endpoints and models securely.

---

## 1. Global JSON Error Handling

In enterprise-level APIs, returning HTML-based 500 server crashes to clients is unacceptable. Our application features a **Global Error Handler** configured in `app.py` utilizing the `@app.errorhandler(Exception)` decorator. 

### How it Works:
Regardless of where a failure occurs (a database disconnection, a missing token, or an invalid file path), the request pipeline halts and forwards the exception to our handler. 

- **If it is a standard HTTP Exception** (like `404 Not Found` or `401 Unauthorized`), the handler intercepts the HTML response and rewrites it as structured JSON, returning the identical status error code.
- **If it is a critical unhandled backend Exception** (like a `KeyError` or timeout), it shields the stack trace, prevents the app from crashing, and automatically returns a sanitized `500 Internal Server Error` in standard JSON format:
```json
{
  "code": 500,
  "name": "Internal Server Error",
  "description": "An unexpected error occurred: connection timed out"
}
```

---

## 2. Authentication Concept & RBAC

### What is a Token?
A **JSON Web Token (JWT)** is a secure string that represents a user's session. When a user submits their username and password to `/auth/login`, the server verifies the credentials and returns a JWT. The client then passes this token in the headers (`Authorization: Bearer <token>`) for subsequent requests, proving their identity without needing to repeatedly send their password.

### What is a Protected Endpoint?
A protected endpoint is an API route that explicitly requires a valid JWT to be processed. If a request lacks the token, or if the token is tampered with/expired, the server immediately rejects the request with a `401 Unauthorized` response.

### Role-Based Access Control (RBAC)
Not all authenticated users are equal. **RBAC** ensures that users only have access to information pertinent to their permission level. 
In our application, we have two roles mapping to two distinct access tiers:
1. **Standard User:** Has basic access to high-level analytics operations (like getting the top 10 sales).
2. **Admin User (`is_admin=True`):** Has complete, unfettered access to all endpoints, including highly sensitive predictive algorithms and internal file system uploads/reads.

---

## 3. Auth Middleware & Line-by-Line Examples

Our security relies on two custom Python decorators found in `middlewares/auth_middleware.py`:

### `@token_required`
This decorator protects endpoints from unauthorized view. 

```python
@analytics_bp.route("/sales")
@token_required      # 1. Pipeline intercepts the request and checks the headers.
def sales():         # 2. If valid, 'flask.g.user' is populated and the function proceeds.
    return jsonify(get_10_sales_data())
```
*Note: Any logged-in user can execute this.*

### `@admin_required`
This decorator stacks on top of `@token_required` and strictly checks the `is_admin` boolean belonging to the user inside our Postgres database.

```python
@analytics_bp.route("/predict/<int:day>")
@token_required      # 1. Intercepts and parses the JWT token
@admin_required      # 2. Ensures that 'g.user.is_admin' equals True
def predict(day):    # 3. Only admins can reach the execution code!
    return jsonify(predict_sales(day))
```

---

## 4. Secure File Operations & Blobs

The project integrates with Google Cloud Storage to securely process user files. All operations revolve around a core cloud computing concept: the **Blob**.

### What is a Blob?
A **Blob** (Binary Large Object) is a file stored in a cloud bucket (in this case, GCP Cloud Storage). Unlike a traditional local filesystem with nested folders, cloud buckets use a flat architecture. You interact with data by requesting a "Blob" object by its programmatic key or name (e.g., `data.csv`). This Blob object acts as a direct memory reference to the remote cloud data, allowing you to manipulate it via the API.

### Line-by-Line Breakdown: `file_upload_service.py`

#### Uploading a File
```python
def upload_file(file, filename):
    # 1. We create a reference (Blob) inside our GCP bucket specifying the target filename.
    blob = bucket.blob(filename)
    
    # 2. We stream the raw bytes of the uploaded file directly from Flask to the Blob in GCP.
    blob.upload_from_file(file)
    
    # 3. We return the final filename to be saved in a database or returned over the API.
    return filename
```

#### Downloading a File
```python
def download_file(filename):
    # 1. We fetch the cloud reference (Blob) using the exact string name it was saved as.
    blob = bucket.blob(filename)
    
    # 2. We command the Blob to download the entire file into local memory as raw bytes, ready to be sent to the user as a file download attachment.
    return blob.download_as_bytes()
```

#### Reading File Content
```python
def read_file(filename):
    # 1. We locate the target file in the GCP bucket.
    blob = bucket.blob(filename)
    
    # 2. Instead of returning raw bytes, we ask GCP to decode the Blob directly into a UTF-8 string (text). This is extremely useful for explicitly previewing CSV/TXT file content as JSON internally within the API.
    return blob.download_as_text()
```

---

## 5. Database Models & Commands

We strictly map our Python objects to our PostgreSQL database using `SQLAlchemy`.

### Models
Currently, we have a central **User Model**:
- `id` (Integer, Primary Key)
- `username` (String, Unique)
- `password_hash` (String, Encrypted via bcrypt/werkzeug)
- `is_admin` (Boolean, dictating RBAC logic)

### Database Management Commands
To manage database migrations, `Flask-Migrate` tracks schema changes. If you change a model in `models/`, you push the changes to Postgres using your terminal:

```bash
# Initialize the migration folder (Run this only ONCE per project repository)
flask db init

# Generate a new migration script by detecting your Python code changes
flask db migrate -m "Added a new column to Users"

# Apply that generated script to the live PostgreSQL Database
flask db upgrade
```

---

## 6. GCP Compute Engine Deployment Steps

When development is done, deploy the API to a robust production environment on Google Cloud's Compute Engine.

### Phase 1: Provision the Server
1. Go to **Google Cloud Console > Compute Engine > VM instances**.
2. Click **Create Instance**.
3. Choose a machine type (e.g., `e2-micro` for getting started).
4. For OS, select **Ubuntu 22.04 LTS**.
5. In the Firewall section, check **Allow HTTP traffic** and **Allow HTTPS traffic**.
6. Create the instance and click **SSH** to open the terminal.

### Phase 2: Setup Environment & Clone
```bash
# Update Ubuntu package lists
sudo apt update && sudo apt upgrade -y

# Install Python, pip, and PostgreSQL development headers
sudo apt install python3-pip python3-venv python3-dev libpq-dev git -y

# Clone your project
git clone <your-github-repo-url> bq_sales_project
cd bq_sales_project

# Establish the Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Install all dependencies (including Gunicorn, our production server tool)
pip install -r requirements.txt
pip install gunicorn
```

### Phase 3: Setup Variables & Database
1. Create your `.env` file using `nano .env` and insert your secrets:
   ```text
   DATABASE_URL="postgresql+psycopg2://user:password@<DB_IP>:5432/sales-db"
   SECRET_KEY="your-production-secret-key"
   GCP_BUCKET_NAME="your-bucket-name"
   ```
2. Run database migrations on the live server:
   ```bash
   flask db upgrade
   ```

### Phase 4: Allow Traffic (Firewall)
By default, GCP blocks unauthorized ports. Since we will run Gunicorn on Port 5000, you must open it:
1. Go to the **Google Cloud Console > VPC Network > Firewall**.
2. Click **Create Firewall Rule**.
3. Name it `allow-flask-5000`.
4. Set **Targets** to "All instances in the network".
5. Set **Source IPv4 ranges** to `0.0.0.0/0`.
6. Under **Protocols and ports**, check **TCP** and type `5000`.
7. Click **Create**.

### Phase 5: Run Gunicorn securely in the Background
Instead of complex reverse proxies like Nginx, we will run Gunicorn directly bound to the public IP. We use the `nohup` command (no hangup) so that the server remains running even after you close your SSH terminal!

```bash
nohup gunicorn --workers 3 --bind 0.0.0.0:5000 app:app > gunicorn_logs.txt 2>&1 &
```
*(Note: We use `app:app` because your Flask variable is named `app` inside `app.py`.)*

### Phase 6: You are Live!
Navigate your browser to `http://<your-Compute-Engine-IP>:5000/apidocs/` to test your fully deployed API!
If you ever want to stop the server, you can find its Process ID with `pkill gunicorn`.

---

## 7. RAG (Retrieval-Augmented Generation) Integrations

The API now fully supports an integrated RAG flow to query custom documents intelligently utilizing Langchain and HuggingFace/Groq.

### Core Concepts

**1. What is RAG?**  
**RAG (Retrieval-Augmented Generation)** is an AI framework that improves the quality of Large Language Model (LLM) responses by grounding the model on external sources of knowledge. Instead of relying solely on the data the LLM was originally trained on, a RAG agent first accesses specific, provided documents (like your PDFs or text files) to find relevant facts, and then provides those facts to the LLM to generate an accurate, context-aware answer. 

**2. What is an LLM?**  
An **LLM (Large Language Model)**, like OpenAI's GPT-4 or Meta's Llama 3 (which you are using via Groq), is an AI model trained on massive amounts of text data. It understands human language and can generate human-like text, summarize information, answer questions, and execute logic based on instructions (prompts) you give it.

**3. What are Embeddings?**  
**Embeddings** are numerical representations of text. In machine learning, texts are converted into lists of numbers (vectors) in a high-dimensional space so that computers can understand the "meaning" of the words. Text containing similar concepts will have embeddings that are mathematically close to each other. When a user asks a question, we convert the question into an embedding and find the text chunks with the "closest" embeddings to retrieve relevant context.

**4. The RAG Flow**  
The typical RAG process follows these steps:
1. **Load data:** Read documents (PDF, CSV, docx, etc.).
2. **Chunk data:** Split the documents into smaller text sections (because LLMs have a limit on how much text they can read at once).
3. **Embed:** Convert these text chunks into vectors using an embeddings model.
4. **Store:** Store these numerical vectors in a Vector Database (like FAISS) so they can be searched quickly.
5. **Retrieve:** When a user asks a question, convert the question into a vector and search the database for the most mathematically similar (relevant) chunks.
6. **Generate:** Feed these relevant chunks to the LLM as facts along with the user's question, so the LLM can generate a confident, source-backed answer.

### Code Breakdown: `services/rag_services.py`

#### Data Ingestion & Storage
```python
def process_document(file_path):
    global vector_store
    
    # 1. Load document via helper function
    documents = load_document(file_path)

    # 2. Chunk: splits files so LLMs can handle them, maintaining a 100 char overlap 
    # to avoid clipping sentences contextually.
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    docs = splitter.split_documents(documents)
    
    # 3. Embed & 4. Store in FAISS
    # We turn chunked text into mathematical vectors using locally hosted HuggingFace models,
    # and bind them to the FAISS Vector Database for querying later.
    vector_store = FAISS.from_documents(docs, embeddings)
    return "Document processed successfully"
```

#### Retrieval & Generation
```python
def ask_question(question):
    global vector_store
    
    # 5. Retrieve top 3 relevant chunks
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    relevant_docs = retriever.invoke(question)
    context = "\n".join([doc.page_content for doc in relevant_docs])
    
    # 6. LLM Evaluation
    llm = ChatGroq(model_name="llama-3.1-8b-instant", groq_api_key=GROQ_API_KEY)
    
    # We constrain the LLM context to avoid AI hallucinations
    prompt = f"Use the following context to answer the question.\nContext:\n{context}\nQuestion: {question}"
    
    response = llm.invoke(prompt)
    return response.content
```

### Code Breakdown: `routes/rag_routes.py`
Exposes the RAG flow as HTTP API endpoints:
- **`POST /rag/upload`**: Retrieves `multipart/form-data` uploads, saves them locally via `file_utils`, and processes them into embeddings via `process_document`.
- **`POST /rag/ask`**: Accepts a JSON `{"query": "your question"}` payload. Invokes the `ask_question()` retriever to query the FAISS in-memory DB and streams back the LLM's response.
