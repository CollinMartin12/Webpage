from ast import Str
import datetime
from typing import List, Optional
from datetime import date as date_type, time as time_type
from sqlalchemy import String, DateTime, ForeignKey, Date, Integer, Float, Boolean, Time, Enum, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import flask_login


from . import db

TripStatus = Enum("Planning", "Happening", "Done", "Canceled", name="trip_status")
TripType = Enum("Breakfast", "lunch", "dinner", "Brunch", name="trip_type")
# RestaurantType = Enum("Italian", "Chinese", "Asian", "American", "Pastry")

class TripType(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))

# Association table for many-to-many relationship between Trip and RestaurantType
trip_restaurant_type = Table('trip_restaurant_type', db.metadata,
    Column('trip_id', Integer, ForeignKey('trip.id')),
    Column('restaurant_type_id', Integer, ForeignKey('restaurant_type.id'))
)

class RestaurantType(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    
class Neighborhood(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256))

class City(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256), unique=True)

class Interest(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    interest: Mapped[str] = mapped_column(String(128), index=True)
    user: Mapped["User"] = relationship(back_populates="interests")

class FollowingAssociation(db.Model):
    follower_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    followed_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)


class Trip_participants(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trip.id"))
    trip: Mapped["Trip"] = relationship(back_populates="participants")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship()
    editing_permissions: Mapped[bool] = mapped_column(Boolean)


class User(flask_login.UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(128), unique=True)
    name: Mapped[str] = mapped_column(String(64))
    password: Mapped[str] = mapped_column(String(256))
    description: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    profile_picture: Mapped[Optional[str]] = mapped_column(String(512), nullable = True)

    city_id: Mapped[Optional[int]] = mapped_column(ForeignKey("city.id"), nullable=True, index=True)
    neighborhood_id: Mapped[Optional[int]] = mapped_column(ForeignKey("neighborhood.id"), nullable=True)

    city: Mapped[Optional["City"]] = relationship()
    neighborhood: Mapped[Optional["Neighborhood"]] = relationship()

    interests: Mapped[List["Interest"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    following: Mapped[List["User"]] = relationship(
        secondary=FollowingAssociation.__table__,
        primaryjoin=FollowingAssociation.follower_id == id,
        secondaryjoin=FollowingAssociation.followed_id == id,
        back_populates="followers",
    )
    followers: Mapped[List["User"]] = relationship(
        secondary=FollowingAssociation.__table__,
        primaryjoin=FollowingAssociation.followed_id == id,
        secondaryjoin=FollowingAssociation.follower_id == id,
        back_populates="following",
    )

    # trips
    trips_created: Mapped[List["Trip"]] = relationship(back_populates="creator")
    trip_comments: Mapped[List["TripComment"]] = relationship(back_populates="author")
    trip_participations: Mapped[List["Trip_participants"]] = relationship(back_populates="user")  # assuming Model exists

    meetups: Mapped[List["Meetups"]] = relationship(back_populates="user")

    # # DMS
    # conversations: Mapped[List["Conversation"]] = relationship(
    #     secondary=conversation_participant, back_populates="participants", lazy="selectin"
    # )
    # direct_messages_sent: Mapped[List["DirectMessage"]] = relationship(back_populates="sender")


class Trip(db.Model):
    # CONFIGURATIONS
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
    start_date: Mapped[Optional[date_type]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date_type]] = mapped_column(Date, nullable=True)
    definite_date: Mapped[Optional[date_type]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(TripStatus, default="PLANNING", index=True)

    status_time: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    status = mapped_column(TripStatus, default="Planning", index=True)

    # DETAILS
    budget: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    description: Mapped[str] = mapped_column(String(256))  # longer than 512 in practice
    restaurant_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    picture: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)


    trip_type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("trip_type.id"), nullable=True, index=True)
    trip_type: Mapped[Optional["TripType"]] = relationship()
    restaurant_types: Mapped[List["RestaurantType"]] = relationship(secondary="trip_restaurant_type", lazy="selectin")


    # Capacity
    max_participants: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_open: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    # Relations
    participants: Mapped[List["Trip_participants"]] = relationship(back_populates="trip", cascade="all, delete-orphan")
    meetups: Mapped[List["Meetups"]] = relationship(back_populates="trip", cascade="all, delete-orphan")
    comments: Mapped[List["TripComment"]] = relationship(back_populates="trip", order_by="TripComment.created_at.desc()", cascade="all, delete-orphan")

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=datetime.datetime.utcnow, index=True)



MeetupStatus = Enum("PLANNING", "HAPPENING", "DONE", name="meetup_status")

class Meetups(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trip.id"), index=True)
    trip: Mapped[Trip] = relationship(back_populates="meetups")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    user: Mapped[User] = relationship(back_populates="meetups")

    content: Mapped[str] = mapped_column(String(512))
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    location: Mapped[str] = mapped_column(String(128))

    city_id: Mapped[int] = mapped_column(ForeignKey("city.id"), index=True)
    city: Mapped[City] = relationship()

    date: Mapped[date_type] = mapped_column(Date)
    time: Mapped[datetime.time] = mapped_column(Time)
    status: Mapped[str] = mapped_column(MeetupStatus, index=True)

# class Message(db.Model):
#     id: Mapped[int] = mapped_column(primary_key=True)
#     post_id: Mapped[int] = mapped_column(ForeignKey("post.id"))
#     post: Mapped["Post"] = relationship(back_populates="messages")
#     user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
#     user: Mapped["User"] = relationship(back_populates="messages")
#     content: Mapped[str] = mapped_column(String(512))
#     timestamp: Mapped[datetime.datetime] = mapped_column(
#         DateTime(timezone=True), server_default=func.now()
#     )


# Rename this
class TripComment(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trip.id"), index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    content: Mapped[str] = mapped_column(String(1000))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    trip: Mapped["Trip"] = relationship(back_populates="comments")
    author: Mapped[User] = relationship(back_populates="trip_comments")

    
