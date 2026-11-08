from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.users.models import User


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="PLN", nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    owner: Mapped["User"] = relationship(back_populates="groups")
    participants: Mapped[list["Participant"]] = relationship(back_populates="group")
    bills: Mapped[list["Bill"]] = relationship(back_populates="group")


class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)

    group: Mapped["Group"] = relationship(back_populates="participants")
    bills_paid: Mapped[list["Bill"]] = relationship(back_populates="paid_by")


class Bill(Base):
    __tablename__ = "bills"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    amount_grosze: Mapped[int] = mapped_column(Integer, nullable=False)
    paid_at: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    paid_by_participant_id: Mapped[int] = mapped_column(
        ForeignKey("participants.id"),
        nullable=False,
    )

    group: Mapped["Group"] = relationship(back_populates="bills")
    paid_by: Mapped["Participant"] = relationship(back_populates="bills_paid")
