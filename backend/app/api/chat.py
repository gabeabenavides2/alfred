from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.provider_factory import get_ai_provider
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models.conversation import Conversation
from app.services.memory_manager import MemoryManager
from app.db.models.message import Message
from app.db.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.orchestrator_service import analyze_message


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        if request.conversation_id:
            conversation = (
                db.query(Conversation)
                .filter(
                    Conversation.id == request.conversation_id,
                    Conversation.user_id == current_user.id,
                )
                .first()
            )

            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
        else:
            conversation = Conversation(
                user_id=current_user.id,
                title=request.message[:50],
                last_message_at=datetime.utcnow(),
            )

            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message,
        )

        db.add(user_message)
        db.commit()
        db.refresh(user_message)

        analysis = await analyze_message(request.message)

        await memory_manager.process_memories(
            db=db,
            user_id=current_user.id,
            source_message_id=user_message.id,
            extracted_memories=analysis.memories,
        )

        if analysis.can_respond_directly and analysis.direct_response:
            assistant_message = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=analysis.direct_response,
            )

            conversation.last_message_at = datetime.utcnow()
            conversation.updated_at = datetime.utcnow()

            db.add(assistant_message)
            db.commit()

            return ChatResponse(
                response=analysis.direct_response,
                conversation_id=conversation.id,
            )

        recent_messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.asc())
            .limit(20)
            .all()
        )

        messages = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in recent_messages
        ]

        provider = get_ai_provider()
        response_text = await provider.generate_response(messages)

        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=response_text,
        )

        conversation.last_message_at = datetime.utcnow()
        conversation.updated_at = datetime.utcnow()

        db.add(assistant_message)
        db.commit()

        return ChatResponse(
            response=response_text,
            conversation_id=conversation.id,
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))