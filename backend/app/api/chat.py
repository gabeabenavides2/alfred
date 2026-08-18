from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.provider_factory import get_ai_provider
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models.conversation import Conversation
from app.db.models.message import Message
from app.db.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.context_builder_service import ContextBuilder
from app.services.memory_manager import MemoryManager
from app.services.orchestrator_service import analyze_message
from app.ai.model_router import ModelRouter



router = APIRouter(prefix="/chat", tags=["chat"])
model_router = ModelRouter()


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        # Find an existing conversation or create a new one.
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
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found",
                )
        else:
            conversation = Conversation(
                user_id=current_user.id,
                title=request.message[:50],
                last_message_at=datetime.utcnow(),
            )

            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        # Save the user's message.
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message,
        )

        db.add(user_message)
        db.commit()
        db.refresh(user_message)

        # Ask the orchestrator what Alfred should do next.
        analysis = await analyze_message(request.message)

        # Store any long-term memories extracted by the orchestrator.
        if analysis.memories:
            memory_manager = MemoryManager(db)

            for candidate in analysis.memories:
                memory_type = candidate.memory_type

                if hasattr(memory_type, "value"):
                    memory_type = memory_type.value

                await memory_manager.create_memory(
                    user_id=current_user.id,
                    content=candidate.content,
                    memory_type=memory_type,
                    importance_score=candidate.importance_score,
                    source_message_id=user_message.id,
                )

            db.commit()

        # Use the orchestrator's direct response when no additional
        # context, tool, or final LLM call is needed.
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
            db.refresh(assistant_message)

            return ChatResponse(
                response=analysis.direct_response,
                conversation_id=conversation.id,
            )

        # Retrieve the information needed for the final response.
        context_builder = ContextBuilder(db)

        built_context = await context_builder.build_context(
            user_id=current_user.id,
            conversation_id=conversation.id,
            user_message=request.message,
            analysis=analysis,
        )

        # Convert the structured context into messages for the provider.
        messages: list[dict[str, str]] = []

        if built_context.memories:
            memory_lines = [
                f"- [{memory.memory_type}] {memory.content}"
                for memory in built_context.memories
            ]

            messages.append(
                {
                    "role": "system",
                    "content": (
                        "The following are relevant long-term memories "
                        "about the user:\n"
                        + "\n".join(memory_lines)
                        + "\n\nUse these memories only when relevant to "
                        "the user's request. Do not mention the memory "
                        "system or say that these memories were retrieved."
                    ),
                }
            )

        messages.extend(
            {
                "role": message.role,
                "content": message.content,
            }
            for message in built_context.conversation_messages
        )

        # Select the provider and model for this type of request.
        selection = model_router.select(analysis.model_route)

        print("\n========== MODEL ROUTING ==========")
        print(f"Route: {selection.route.value}")
        print(f"Provider: {selection.provider}")
        print(f"Model: {selection.model}")
        print("===================================\n")

        # Generate Alfred's final response using the selected model.
        provider = get_ai_provider(
            provider_name=selection.provider,
            model=selection.model,
        )

        response_text = await provider.generate_response(messages)

        # Save Alfred's response.
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=response_text,
        )

        conversation.last_message_at = datetime.utcnow()
        conversation.updated_at = datetime.utcnow()

        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)

        return ChatResponse(
            response=response_text,
            conversation_id=conversation.id,
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )