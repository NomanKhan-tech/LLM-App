from sqlalchemy.orm import Session

from app.models.message import Message
from app.models.conversation import Conversation


def get_conversation_history(
    db: Session,
    conversation_id: int,
):
    conversation = (
        db.query(Conversation).filter(Conversation.id == conversation_id).first()
    )

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(20)
        .all()
    )

    messages.reverse()

    history = []

    # Add conversation summary first
    if conversation and conversation.summary:
        history.append(
            {
                "role": "system",
                "content": f"Conversation summary: {conversation.summary}",
            }
        )

    # Add recent messages
    for message in messages:
        history.append(
            {
                "role": message.role,
                "content": message.content,
            }
        )

    return history
