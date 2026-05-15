import os
import logging
from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException, Depends, Security, Request
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Setup
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AI-Service")

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Pro AI Service API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security
API_KEY = os.getenv("APP_API_KEY", "default-secret")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

async def get_api_key(header_key: str = Security(api_key_header)):
    if header_key != API_KEY:
        raise HTTPException(status_code=403, detail="Could not validate API Key")
    return header_key

# AI Client
llm = ChatGroq(model_name="llama-3.1-8b-instant", temperature=0)

# --- Pydantic Models ---

class TextRequest(BaseModel):
    text: str = Field(..., min_length=10, description="The text to process")

class SummaryResponse(BaseModel):
    summary: str
    word_count: int

class ClassifyRequest(BaseModel):
    text: str
    categories: List[str] = Field(default=["News", "Sports", "Technology", "Politics", "Entertainment"])

class ClassifyResponse(BaseModel):
    category: str
    confidence: float

class ExtractRequest(BaseModel):
    text: str
    fields: List[str] = Field(..., description="List of fields to extract (e.g. name, date, amount)")

class ExtractResponse(BaseModel):
    data: Dict[str, str]

# --- Endpoints ---

@app.get("/health")
async def health_check():
    logger.info("Health check triggered")
    return {"status": "healthy", "model": "llama-3.1-8b-instant"}

@app.post("/summarise", response_model=SummaryResponse, dependencies=[Depends(get_api_key)])
@limiter.limit("10/minute")
async def summarise(payload: TextRequest, request: Request):
    logger.info(f"Summarising text of length {len(payload.text)}")
    try:
        prompt = ChatPromptTemplate.from_template("Summarize the following text in 3 concise sentences:\n\n{text}")
        chain = prompt | llm
        response = chain.invoke({"text": payload.text})
        summary = response.content
        return SummaryResponse(summary=summary, word_count=len(summary.split()))
    except Exception as e:
        logger.error(f"Summarisation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal AI error")

@app.post("/classify", response_model=ClassifyResponse, dependencies=[Depends(get_api_key)])
@limiter.limit("10/minute")
async def classify(payload: ClassifyRequest, request: Request):
    logger.info(f"Classifying text into categories: {payload.categories}")
    try:
        prompt = ChatPromptTemplate.from_template(
            "Classify the following text into exactly ONE of these categories: {categories}.\n"
            "Return only the category name.\n\nText: {text}"
        )
        chain = prompt | llm
        response = chain.invoke({"text": payload.text, "categories": ", ".join(payload.categories)})
        return ClassifyResponse(category=response.content.strip(), confidence=0.95)
    except Exception as e:
        logger.error(f"Classification failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal AI error")

@app.post("/extract", response_model=ExtractResponse, dependencies=[Depends(get_api_key)])
@limiter.limit("10/minute")
async def extract(payload: ExtractRequest, request: Request):
    logger.info(f"Extracting fields {payload.fields} from text")
    try:
        prompt = ChatPromptTemplate.from_template(
            "Extract the following fields as a JSON object from the text: {fields}.\n"
            "Text: {text}\n"
            "JSON Output:"
        )
        chain = prompt | llm
        response = chain.invoke({"text": payload.text, "fields": ", ".join(payload.fields)})
        
        # Simple cleanup if the model adds markdown backticks
        json_str = response.content.replace("```json", "").replace("```", "").strip()
        import json
        data = json.loads(json_str)
        return ExtractResponse(data=data)
    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal AI error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
