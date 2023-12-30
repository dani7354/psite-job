from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship
from sqlalchemy.sql.schema import Column, ForeignKey


class Base(DeclarativeBase):
    pass


class Message(Base):
    __tablename__ = "Message"
    id: Mapped[int] = Column(Integer, primary_key=True)
    subject: Mapped[str] = Column(String(255), nullable=False)
    body: Mapped[str] = Column(String(1200), nullable=False)
    date_created: Mapped[datetime] = Column("DateCreated", DateTime, nullable=False)
    date_sent: Mapped[datetime] = Column("DateSent", DateTime, nullable=True)
    sender_name: Mapped[str] = Column("SenderName", String(255), nullable=False)
    sender_email: Mapped[str] = Column("SenderEmail", String(255), nullable=False)
    sender_ip: Mapped[str] = Column("SenderIp", String(45), nullable=False)


class ProjectUpdate(Base):
    __tablename__ = "ProjectUpdate"
    id: Mapped[int] = Column(Integer, primary_key=True)
    project_id: Mapped[int] = Column("ProjectId", Integer, ForeignKey("Project.id"))
    updated_at: Mapped[datetime] = Column("UpdatedAt", DateTime, nullable=False)


class Project(Base):
    __tablename__ = "Project"
    id: Mapped[int] = Column(Integer, primary_key=True)
    title: Mapped[str] = Column(String(255), nullable=False)
    url: Mapped[str] = Column(String(255), nullable=False)
    description: Mapped[str] = Column(String(1200), nullable=False)
    is_visible: Mapped[bool] = Column("IsVisible", Boolean, nullable=False)
    order_number: Mapped[int] = Column("OrderNumber", Integer, nullable=True)
    updates: Mapped[list[ProjectUpdate]] = relationship()
