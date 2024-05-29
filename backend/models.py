from sqlalchemy import Table, Column, Integer, String, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from config import db
import datetime
from flask import current_app as app
import jwt
    
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
    earliest_pickup_time = Column(DateTime, nullable=False)
    latest_pickup_time = Column(DateTime, nullable=False)
    max_group_size = Column(Integer, nullable=False)
    private = Column(Boolean, default=False)
    description = Column(String(500))
    preferred_apps = Column(String(200))

    creator = relationship('User', back_populates='created_rides')
    members = relationship('User', secondary=user_ride_association, back_populates='rides')

    def has_not_happened_yet(self):
        return self.latest_pickup_time > datetime.datetime.now()

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
            "earliestPickupTime": self.earliest_pickup_time.isoformat(),
            "latestPickupTime": self.latest_pickup_time.isoformat(),
            "maxGroupSize": self.max_group_size,
            "private": self.private,
            "description": self.description,
            # "preferredApps": self.preferred_apps,
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
    
    def encode_auth_token(self, username):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=0, hours=1),
                'iat': datetime.datetime.now(datetime.UTC),
                'sub': username
            }
            return jwt.encode(
                payload,
                SECRET_KEY,
                algorithm='HS256'
            )
        except Exception as e:
            return e
    
    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'), algorithms=["HS256"])
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return 'Invalid token. Please log in again.'
            return payload # this returns the username
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


class BlacklistToken(db.Model):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)
    
    @staticmethod
    def check_blacklist(auth_token):
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True  
        else:
            return False
    
with app.app_context():
    SECRET_KEY = app.config['SECRET_KEY']
    db.create_all()
    num = db.session.query(BlacklistToken).delete()
    db.session.commit()
    print(f"Cleared blacklisted_tokens of {num} entries")