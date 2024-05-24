from sqlalchemy import Table, Column, Integer, String, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from config import db
from datetime import datetime

user_ride_association = Table('user_ride_association', db.Model.metadata,
    Column('user_id', Integer, ForeignKey('user.user_id'), primary_key=True),
    Column('ride_id', Integer, ForeignKey('ride.ride_id'), primary_key=True)
)

class Ride(db.Model): 
    __tablename__ = 'ride'
    ride_id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    pickup_longitude = Column(Float, nullable=False)
    pickup_latitude = Column(Float, nullable=False)
    destination_longitude = Column(Float, nullable=False)
    destination_latitude = Column(Float, nullable=False)
    pickup_threshold = Column(Float, nullable=False)
    destination_threshold = Column(Float, nullable=False)
    earliest_arrival_time = Column(DateTime, nullable=False)
    latest_arrival_time = Column(DateTime, nullable=False)
    max_group_size = Column(Integer, nullable=False)
    private = Column(Boolean, default=False)
    description = Column(String(500))
    preferred_apps = Column(String(200))

    creator = relationship('User', back_populates='created_rides')
    members = relationship('User', secondary=user_ride_association, back_populates='rides')

    def has_not_happened_yet(self):
        return self.latest_arrival_time > datetime.now()

    def to_json(self):
        return {
            "rideId": self.ride_id,
            "creatorId": self.creator_id,
            "pickupLongitude": self.pickup_longitude,
            "pickupLatitude": self.pickup_latitude,
            "destinationLongitude": self.destination_longitude,
            "destinationLatitude": self.destination_latitude,
            "pickupThreshold": self.pickup_threshold,
            "destinationThreshold": self.destination_threshold,
            "earliestArrivalTime": self.earliest_arrival_time.isoformat(),
            "latestArrivalTime": self.latest_arrival_time.isoformat(),
            "maxGroupSize": self.max_group_size,
            "private": self.private,
            "description": self.description,
            "preferredApps": self.preferred_apps,
            "members": [member.user_id for member in self.members]
        }

class User(db.Model):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(80), nullable=False)
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    phone_number = Column(String(12), unique=True, nullable=False)
    latitude = Column(Float, nullable = True)
    longitude = Column(Float, nullable = True)

    created_rides = relationship('Ride', back_populates='creator')
    rides = relationship('Ride', secondary=user_ride_association, back_populates='members')

    def to_json(self):
        return {
            "userId": self.user_id,
            "username": self.username,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "email": self.email,
            "phoneNumber": self.phone_number,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "rides": [ride.to_json() for ride in self.rides]
        }
    