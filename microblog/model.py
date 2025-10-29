import datetime
from typing import List, Optional
from datetime import date
from sqlalchemy import String, DateTime, ForeignKey, Date, Integer, Float, Boolean, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import flask_login

from . import db


class User(flask_login.UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(128), unique=True)
    name: Mapped[str] = mapped_column(String(64))
    password: Mapped[str] = mapped_column(String(256))
    posts: Mapped[List["Post"]] = relationship(back_populates="user")
    description: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    messages: Mapped[List["Message"]] = relationship(back_populates="user")
    trips: Mapped[List["Trip"]] = relationship(back_populates="user")
    meetups: Mapped[List["Meetups"]] = relationship(back_populates="user")


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="posts")
    text: Mapped[str] = mapped_column(String(512))
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    trip_id: Mapped[int] = mapped_column(ForeignKey("trip.id"))
    trip: Mapped["Trip"] = relationship(back_populates="posts")
    messages: Mapped[List["Message"]] = relationship(back_populates="post")
    # response_to_id: Mapped[Optional[int]] = mapped_column(ForeignKey("post.id"))
    # response_to: Mapped["Post"] = relationship(
    #     back_populates="responses", remote_side=[id]
    # )


class Trip(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="trips")
    departure: Mapped[str] = mapped_column(String(128))
    destination: Mapped[str] = mapped_column(String(128))
    possible_dates: Mapped[datetime.date] = mapped_column(Date)
    budget: Mapped[int] = mapped_column(Float)
    text: Mapped[str] = mapped_column(String(29))
    type_of_trip: Mapped[str] = mapped_column(String(128))
    max_participants: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(128))
    posts: Mapped[List["Post"]] = relationship(back_populates="trip")
    trip_participants: Mapped[List["Trip_participants"]] = relationship(back_populates="trip")
    meetups: Mapped[List["Meetups"]] = relationship(back_populates="trip")

    # responses: Mapped[List["Post"]] = relationship(
    #     back_populates="response_to", remote_side=[response_to_id]
    # )

class Message(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"))
    post: Mapped["Post"] = relationship(back_populates="messages")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="messages")
    content: Mapped[str] = mapped_column(String(512))
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

class Trip_participants(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trip.id"))
    trip: Mapped["Trip"] = relationship(back_populates="trip_participants")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    editing_permissions: Mapped[bool] = mapped_column(Boolean)

class Meetups(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trip.id"))
    trip: Mapped["Trip"] = relationship(back_populates="meetups")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="meetups")
    content: Mapped[str] = mapped_column(String(512))
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    location: Mapped[str] = mapped_column(String(128))
    date: Mapped[datetime.date] = mapped_column(Date)
    time: Mapped[datetime.time] = mapped_column(Time)
    status: Mapped[str] = mapped_column(String(128))