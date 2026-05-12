# 🤖 Pro AI Service (FastAPI)

A high-performance AI microservice providing text summarisation, classification, and structured data extraction using **Groq** and **Llama 3.1**.

## 🚀 Features
- **Summarise**: Get concise summaries of long text.
- **Classify**: Categorize text into custom defined labels.
- **Extract**: Convert free text into structured JSON data.
- **Security**: Built-in API Key authentication (`X-API-Key` header).
- **Rate Limiting**: Protected against abuse (10 requests per minute).
- **Logging**: Full request/error logging for production monitoring.
- **Validation**: Robust data validation using Pydantic.

## 🛠️ Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure `.env`**:
   Ensure you have your `GROQ_API_KEY` and `APP_API_KEY` set.

3. **Run the server**:
   ```bash
   python main.py
   ```

## 🔌 API Documentation

Once running, visit `http://localhost:8001/docs` to see the full interactive Swagger documentation.

### Authentication
All POST endpoints require the following header:
`X-API-Key: super-secret-service-key-123`

### Example: Summarise
**URL**: `/summarise`
**Method**: `POST`
**Body**:
```json
{
  "text": "Your long text goes here..."
}
```

## 🏆 Assignment Requirements Met:
- [x] POST `/summarise`
- [x] POST `/classify`
- [x] POST `/extract`
- [x] GET `/health`
- [x] Proper Pydantic models
- [x] Error handling & Logging
- [x] **Stretch**: API key authentication
- [x] **Stretch**: Rate limiting (10 req/min)
