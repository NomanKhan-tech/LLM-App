from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.schemas.message import MessageCreate, MessageResponse
from app.services.conversation_service import get_conversation_history
from app.services.llm_service import ask_llm
from app.services.memory_service import manage_memory

router = APIRouter(
    prefix="/conversations/{conversation_id}/messages",
    tags=["Messages"],
)


@router.post("", response_model=MessageResponse)
def create_message(
    conversation_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Save user's message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=message_data.content,
    )

    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    # Load conversation history
    history = get_conversation_history(
        db=db,
        conversation_id=conversation.id,
    )

    # Ask AI
    assistant_content = ask_llm(history)

    # Save AI response
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=assistant_content,
    )

    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)

    # Manage conversation memory
    manage_memory(
        db=db,
        conversation_id=conversation.id,
    )

    return assistant_message


@router.get("", response_model=list[MessageResponse])
def get_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    return messages
