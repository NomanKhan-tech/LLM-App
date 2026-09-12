from fastapi import APIRouter, Depends, HTTPException
from app.services.guardrail_service import detect_prompt_injection
from app.services.llm_service import ask_llm
from app.schemas.chat import ChatRequest
from app.services.rate_limit_service import check_rate_limit
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.guardrail_service import contains_sensitive_data, validate_llm_output

router = APIRouter(
    prefix="/api/v1/chat",
    tags=["Chat"],
)


@router.post("/")
def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    user_id = current_user.id

    if not check_rate_limit(user_id):
        return {
            "response": {
                "status": False,
                "message": "Rate limit exceeded. Please try again later.",
            }
        }

    if detect_prompt_injection(request.message):
        return {
            "response": {
                "status": False,
                "message": "Potential prompt injection detected.",
            }
        }

    if contains_sensitive_data(request.message):
        return {
            "response": {
                "status": False,
                "message": "Sensitive information detected. Please remove secrets or personal financial information.",
            }
        }

    try:
        response = ask_llm(request.message)
        validated_response = validate_llm_output(response)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="AI service temporarily unavailable.",
        )

    return {
        "response": {
            "status": True,
            "llm_response": validated_response,
        }
    }
