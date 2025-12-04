from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, Text
from sqlalchemy.orm import Mapped, sessionmaker, mapped_column, declarative_base, relationship

from db.database import Base

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)

    # relationships
    rags = relationship("Rag_Table", back_populates="user")

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username='{self.username}')>"



class Rag_Table(Base):
    __tablename__ = "rag_table"

    rag_id: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    rag_name: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False)
    key: Mapped[str] = mapped_column(String, nullable=False)
    documents: Mapped[str] = mapped_column(Text)


    # RELATIONSHIP 
    user = relationship("User", back_populates="rags")

    def __repr__(self):
        return f"<Rag_Table(rag_id={self.rag_id}, rag_name='{self.rag_name}')>"