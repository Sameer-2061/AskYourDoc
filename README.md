# AskYourDoc - AI-Powered Document Assistant

A production-ready, full-stack Retrieval-Augmented Generation (RAG) application that enables users to upload documents and conduct intelligent, context-aware conversations with their data. The application features a lightweight, high-performance architecture optimized for cloud deployment, utilizing Google Gemini for semantic embeddings and text generation, FastAPI for the backend service, and MongoDB for persistence.

## Live Deployments
- Frontend Application: https://ask-your-doc-eight.vercel.app
- Backend API Service: https://askyourdoc-api.onrender.com

## The RAG Architecture & Technical Pipeline

The core of AskYourDoc is its proprietary Retrieval-Augmented Generation (RAG) architecture, built to overcome the limitations of standard LLM context windows and static knowledge bases.

1. Unstructured Data Ingestion
When a user uploads documents via the frontend, the FastAPI backend intercepts the multipart form data. Utilizing specific libraries like PyMuPDF for PDFs and python-docx for Word files, the application extracts raw text streams from the documents dynamically, handling various encodings and formats.

2. Cloud-Based Vector Embeddings
To maintain a lightweight footprint suitable for resource-constrained cloud environments, the system delegates embedding generation to Google's cloud infrastructure using the models/gemini-embedding-001 model. This model converts the extracted text chunks into high-dimensional vector representations (arrays of floating-point numbers) that capture deep semantic meaning rather than relying on simple keyword matching.

3. Vector and Document Storage
The generated vector embeddings, alongside their corresponding raw text metadata and filenames, are indexed and stored in a MongoDB collection. This allows for persistent storage of document states without relying on in-memory vector databases.

4. Semantic Search and Mathematical Retrieval
When a user submits a query in Document Mode, the query text is vectorized via the same Gemini embedding API. The backend then executes a semantic search across the database by computing the Cosine Similarity between the query vector and all stored document vectors. This mathematical operation calculates the cosine of the angle between the two vectors in multidimensional space to determine contextual proximity. The system isolates the top matches with the highest similarity scores.

5. Context-Augmented Generation
The retrieved document blocks are concatenated into a structured prompt context. This augmented prompt, containing both the authoritative source text and the user's question, is dispatched to Google's LLMs (Gemini Flash variants). The model generates a comprehensive response restricted strictly to the injected document data, significantly minimizing the risk of AI hallucinations.

## Tech Stack
- Frontend: HTML5, CSS3 (Custom CSS properties, responsive design), JavaScript (Asynchronous Fetch API).
- Backend: FastAPI (Python high-performance web framework), Uvicorn.
- Artificial Intelligence: Google Gemini API via google-generativeai SDK, Semantic Text Embeddings, Cosine Similarity scoring.
- Database: MongoDB for unstructured document metadata and vector storage.
- Infrastructure: Render (Backend Cloud Hosting), Vercel (Frontend Global Edge Network).

## Installation and Local Setup (For Developers)

If you wish to run this application locally, follow these steps:

1. Clone the repository:
   git clone https://github.com/Sameer-2061/AskYourDoc.git
   cd AskYourDoc

2. Create and activate a virtual environment:
   python -m venv ai_env
   source ai_env/bin/activate  # On Windows use: ai_env\Scripts\activate

3. Install the required dependencies:
   pip install -r requirements.txt

4. Create a .env file in the root directory and populate your credentials:
   GEMINI_API_KEY=your_google_gemini_api_key
   MONGO_URI=your_mongodb_connection_string

5. Run the Uvicorn development server:
   uvicorn main:app --reload

The API will be available at http://127.0.0.1:8000.
 