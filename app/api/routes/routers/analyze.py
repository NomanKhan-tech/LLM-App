from fastapi import APIRouter
from app.services.llm_service import analyze_message
from app.schemas.chat import ChatRequest

router = APIRouter(prefix="/analyze", tags=["Analyze"])


@router.post("/")
def analyze(request: ChatRequest):
    response = analyze_message(request.message)
    return {"response": {"status": True, "analysisResponse": response}}
