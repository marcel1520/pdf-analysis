from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Interactions(Base):
    __tablename__ = "user_interactions"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(Integer, index=True)
    type = Column(String(50), nullable=True)
    prompt = Column(Text, nullable=True)
    response = Column(Text, nullable=True)
    text = Column(Text, nullable=True)
    timestamp = Column(DateTime, server_default=func.now())
