from openai import OpenAI
from sqlalchemy.orm import Session

from app.core.config import OPENAI_API_KEY
from app.models.conversation import Conversation
from app.models.message import Message
import logging

logger = logging.getLogger(__name__)


client = OpenAI(api_key=OPENAI_API_KEY)


def generate_summary(
    messages: list[dict],
    existing_summary: str | None = None,
) -> str:

    logger.info(
        "SUMMARY LLM | preparing %s messages",
        len(messages),
    )

    conversation_text = "\n".join(
        f"{message['role']}: {message['content']}" for message in messages
    )

    if existing_summary:
        input_text = (
            f"Existing conversation summary:\n"
            f"{existing_summary}\n\n"
            f"New conversation messages:\n"
            f"{conversation_text}"
        )
    else:
        input_text = conversation_text

    logger.info("SUMMARY LLM | sending request")

    response = client.responses.create(
        model="gpt-5.6-luna",
        instructions=(
            "Update the conversation summary using the existing summary "
            "and the new messages. Keep important facts, user goals, "
            "decisions, preferences, and useful context for future messages. "
            "Return only the updated summary."
        ),
        input=input_text,
    )

    logger.info("SUMMARY LLM | response received")

    return response.output_text


def save_conversation_summary(
    db: Session,
    conversation_id: int,
    summary: str,
):
    conversation = (
        db.query(Conversation).filter(Conversation.id == conversation_id).first()
    )

    if conversation is None:
        raise ValueError("Conversation not found")

    conversation.summary = summary

    db.commit()
    db.refresh(conversation)

    return conversation


def should_summarize(
    message_count: int,
    unsummarized_count: int,
) -> bool:
    return message_count > 20 and unsummarized_count >= 10


def manage_memory(
    db: Session,
    conversation_id: int,
):
    logger.info(
        "MEMORY CHECK | conversation_id=%s",
        conversation_id,
    )

    conversation = (
        db.query(Conversation).filter(Conversation.id == conversation_id).first()
    )

    if conversation is None:
        raise ValueError("Conversation not found")

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    message_count = len(messages)

    logger.info(
        "MEMORY CHECK | message_count=%s",
        message_count,
    )

    # Keep the latest 20 messages in normal conversation history.
    old_messages = messages[:-20]

    # Find old messages that have not yet been included
    # in the conversation summary.
    unsummarized_messages = [
        message for message in old_messages if not message.summary_included
    ]

    unsummarized_count = len(unsummarized_messages)

    logger.info(
        "MEMORY SUMMARY | old_messages=%s | unsummarized=%s",
        len(old_messages),
        unsummarized_count,
    )

    # Only summarize when:
    # 1. Conversation has more than 20 messages.
    # 2. At least 10 old messages are waiting to be summarized.
    if not should_summarize(
        message_count,
        unsummarized_count,
    ):
        logger.info("MEMORY CHECK | summarization not required")
        return

    logger.info("MEMORY CHECK | summarization triggered")

    if not unsummarized_messages:
        logger.info("MEMORY SUMMARY | no new messages require summarization")
        return

    message_data = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in unsummarized_messages
    ]

    logger.info(
        "MEMORY SUMMARY | sending %s unsummarized messages to LLM",
        len(message_data),
    )

    summary = generate_summary(
        message_data,
        existing_summary=conversation.summary,
    )

    logger.info("MEMORY SUMMARY | summary generated")

    save_conversation_summary(
        db=db,
        conversation_id=conversation_id,
        summary=summary,
    )

    # Mark these messages as already included
    # in the conversation summary.
    for message in unsummarized_messages:
        message.summary_included = True

    db.commit()

    logger.info(
        "MEMORY SUMMARY | %s messages marked as summarized",
        len(unsummarized_messages),
    )

    logger.info("MEMORY SUMMARY | summary saved and tracking updated")
