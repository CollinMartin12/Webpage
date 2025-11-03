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
    description: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    profile_picture: Mapped[Optional[str]] = mapped_column(String(512), nullabel = True)

    city_id: Mapped[int] = mapped_column(ForeignKey("city.id"), index=True)
    neightborhood_id = Mapped[int] = mapped_column(ForeignKey{"neightborhood_id"}, nullable = True)

    city: Mapped[Optional["City"]] = relationship()
    neighborhood: Mapped[Optional["Neighborhood"]] = relationship()

    interests: Mapped[List["Interest"]] = relationship(secondary=user_interest, lazy="selectin")

    following: Mapped[List["User"]] = relationship(
        "User",
        secondary=user_follow,
        primaryjoin=id == user_follow.c.follower_id,
        secondaryjoin=id == user_follow.c.followed_id,
        backref="followers",
        lazy="selectin",
    )

    trip_posts: Mapped[List["TripPost"]] = relationship(back_populates="author")
    trip_comments: Mapped[List["TripComment"]] = relationship(back_populates="author")

    trip_participations: Mapped[List["TripParticipant"]] = relationship(back_populates="user")
    meetups_hosted: Mapped[List["Meetup"]] = relationship(back_populates="host")
    meetups_joined: Mapped[List["Meetup"]] = relationship(
        secondary=meetup_participant, back_populates="participants", lazy="selectin"
    )
    
        # DMs
    conversations: Mapped[List["Conversation"]] = relationship(
        secondary=conversation_participant, back_populates="participants", lazy="selectin"
    )
    direct_messages_sent: Mapped[List["DirectMessage"]] = relationship(back_populates="sender")



class Trip(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    creator: Mapped["User"] = relationship(back_populates="trips_created")

    # DESTINATIONS
    departure_city_id: Mapped[Optional[int]] = mapped_column(ForeignKey("city.id"), nullable=True, index=True)
    departure_neighborhood_id: Mapped[Optional[int]] = mapped_column(ForeignKey("neighborhood.id"), nullable=True, index=True)
    destination_city_id: Mapped[Optional[int]] = mapped_column(ForeignKey("city.id"), nullable=False, index=True)
    destination_neighborhood_id: Mapped[Optional[int]] = mapped_column(ForeignKey("neighborhood.id"), nullable=True, index=True)
    
    departure_city: Mapped[Optional["City"]] = relationship(foreign_keys=[departure_city_id])
    departure_neighborhood: Mapped[Optional["Neighborhood"]] = relationship(foreign_keys=[departure_neighborhood_id])
    destination_city: Mapped[Optional["City"]] = relationship(foreign_keys=[destination_city_id])
    destination_neighborhood: Mapped[Optional["Neighborhood"]] = relationship(foreign_keys=[destination_neighborhood_id])

    # TIMING
    definite_date: Mapped[Optional[dt.date]] = mapped_column(Date, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(TripStatus, default="PLANNING", index=True)
    status_time: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=dt.datetime.utcnow, index=True)


    budget: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    description: Mapped[str] = mapped_column(Text)  # longer than 512 in practice
    restaurant_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)


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

