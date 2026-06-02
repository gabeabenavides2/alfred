from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.ai.provider_factory import get_ai_provider

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        provider = get_ai_provider()
        response = await provider.generate_response(request.message)

        print(f"User message: {request.message}")
        print(f"AI response: {response}")
        return ChatResponse(response=response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))