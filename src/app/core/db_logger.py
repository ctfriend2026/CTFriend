from typing import Optional, List, Dict, Any
import uuid
import os
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Text,
    ForeignKey,
    TIMESTAMP,
    func,
    BigInteger,
    Boolean,
    SmallInteger,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()


class User(Base):
    """Represents a user in the database."""

    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    conversations = relationship("Conversation", backref="user", cascade="all, delete")


class Conversation(Base):
    """Represents a single chat session in the database."""

    __tablename__ = "conversations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    started_at = Column(TIMESTAMP, server_default=func.now())

    messages = relationship("Message", backref="conversation", cascade="all, delete")


class Message(Base):
    """Represents a single message within a conversation."""

    __tablename__ = "messages"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    conversation_id = Column(
        UUID(as_uuid=True), ForeignKey(column="conversations.id", ondelete="CASCADE")
    )
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    feedback = Column(SmallInteger, nullable=True)
    source_ip = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


# DATABASE_URL = "postgresql+psycopg2://postgres:postgres@db:5432/metrics"
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal: sessionmaker[Session] = sessionmaker(bind=engine)


def init_db() -> None:
    """
    Initializes the database by creating all tables defined in the Base metadata.
    This function is idempotent and can be safely called multiple times.
    """
    Base.metadata.create_all(bind=engine)


def is_valid_token(token: str) -> bool:
    """
    Checks if a user token exists in the database and the user is marked as active.

    Args:
        token: The user token to validate.

    Returns:
        True if the token is valid and active, False otherwise.
    """
    if not token:
        return False
    with SessionLocal() as session:
        user: Optional[User] = session.query(User).filter_by(username=token).first()
        return user is not None and user.is_active


def log_message(
    token: str,
    conversation_id: Optional[str],
    role: str,
    content: str,
    source_ip: Optional[str] = None,
) -> Optional[str]:
    """
    Logs a message to the database for a validated, active user.

    If the conversation_id does not exist, a new conversation is created.
    If the user token is invalid or the user is inactive, no action is taken.

    Args:
        token: The user's authentication token.
        conversation_id: The ID of the current conversation. Can be None to start a new one.
        role: The role of the message sender ("user" or "assistant").
        content: The text content of the message.

    Returns:
        The string representation of the conversation ID, or None if logging failed.
    """
    with SessionLocal() as session:
        user: Optional[User] = session.query(User).filter_by(username=token).first()
        if not user or not user.is_active:
            return None

        conversation: Optional[Conversation] = None
        if conversation_id:
            try:
                conv_uuid = uuid.UUID(conversation_id)
                conversation = (
                    session.query(Conversation).filter_by(id=conv_uuid).first()
                )
            except (ValueError, TypeError):
                pass

        if not conversation:
            conversation = Conversation(user_id=user.id)
            session.add(conversation)
            session.commit()
            session.refresh(conversation)

        msg = Message(
            conversation_id=conversation.id,
            role=role,
            content=content,
            source_ip=source_ip,
        )
        session.add(msg)
        session.commit()

        return str(conversation.id)


def log_feedback(message_id: int, feedback: int) -> None:
    """
    Updates the feedback for a specific message in the database.

    Args:
        message_id: The unique ID of the message to update.
        feedback: The feedback value (1 for positive, -1 for negative).
    """
    with SessionLocal() as session:
        session.query(Message).filter(Message.id == message_id).update(
            {"feedback": feedback}
        )
        session.commit()


def load_conversations_for_token(token: str) -> List[Conversation]:
    """
    Retrieves all conversations for a given user token.

    Args:
        token: The user's authentication token.

    Returns:
        A list of Conversation objects, ordered from newest to oldest.
    """
    with SessionLocal() as session:
        user: Optional[User] = session.query(User).filter_by(username=token).first()
        if not user:
            return []
        return (
            session.query(Conversation)
            .filter_by(user_id=user.id)
            .order_by(Conversation.started_at.desc())
            .all()
        )


def load_messages_for_conversation(conversation_id: str) -> List[Dict[str, Any]]:
    """
    Retrieves all messages for a given conversation ID.

    Args:
        conversation_id: The UUID string of the conversation.

    Returns:
        A list of dictionaries, where each dictionary represents a message.
    """
    with SessionLocal() as session:
        try:
            conv_uuid = uuid.UUID(conversation_id)
            messages: List[Message] = (
                session.query(Message)
                .filter_by(conversation_id=conv_uuid)
                .order_by(Message.created_at.asc())
                .all()
            )
            return [
                {
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "feedback": m.feedback,
                }
                for m in messages
            ]
        except (ValueError, TypeError):
            return []


def create_new_conversation(token: str) -> Optional[str]:
    """
    Creates a new, empty conversation for a validated, active user.

    Args:
        token: The user's authentication token.

    Returns:
        The string representation of the new conversation ID, or None if the user is invalid.
    """
    with SessionLocal() as session:
        user: Optional[User] = session.query(User).filter_by(username=token).first()
        if not user or not user.is_active:
            return None

        conversation = Conversation(user_id=user.id)
        session.add(instance=conversation)
        session.commit()
        session.refresh(instance=conversation)

        return str(conversation.id)
