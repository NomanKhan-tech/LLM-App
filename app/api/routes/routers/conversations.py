from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.conversation import Conversation
from app.schemas.conversation import ConversationCreate, ConversationResponse
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.post(
    "",
    response_model=ConversationResponse,
)
def create_conversation(
    conversation_data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = Conversation(
        title=conversation_data.title,
        user_id=current_user.id,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation
