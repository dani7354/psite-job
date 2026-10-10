# pylint: disable=unsubscriptable-object
from datetime import datetime
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Message(Base):
    __tablename__ = "Message"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(String(1200), nullable=False)
    date_created: Mapped[datetime] = mapped_column("DateCreated", nullable=False)
    date_sent: Mapped[datetime | None] = mapped_column("DateSent", nullable=True)
    sender_name: Mapped[str] = mapped_column("SenderName", String(255), nullable=False)
    sender_email: Mapped[str] = mapped_column("SenderEmail", String(255), nullable=False)
    sender_ip: Mapped[str] = mapped_column("SenderIp", String(45), nullable=False)


class ProjectUpdate(Base):
    __tablename__ = "ProjectUpdate"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int | None] = mapped_column("ProjectId", ForeignKey("Project.id"))
    updated_at: Mapped[datetime] = mapped_column("UpdatedAt", nullable=False)


class Project(Base):
    __tablename__ = "Project"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1200), nullable=False)
    is_visible: Mapped[bool] = mapped_column("IsVisible", nullable=False)
    order_number: Mapped[int | None] = mapped_column("OrderNumber", nullable=True)
    updates: Mapped[list[ProjectUpdate]] = relationship()
