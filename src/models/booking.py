from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.String(20), unique=True, nullable=False)
    
    # Service details
    service_type = db.Column(db.String(50), nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False, default='standard')
    
    # Trip details
    pickup_location = db.Column(db.String(200), nullable=False)
    dropoff_location = db.Column(db.String(200), nullable=False)
    pickup_date = db.Column(db.Date, nullable=False)
    pickup_time = db.Column(db.Time, nullable=False)
    passengers = db.Column(db.Integer, nullable=False)
    
    # Customer information
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    
    # Additional options
    special_requests = db.Column(db.Text)
    return_trip = db.Column(db.Boolean, default=False)
    waiting_time = db.Column(db.Boolean, default=False)
    meet_greet = db.Column(db.Boolean, default=False)
    
    # Booking status and metadata
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, completed, cancelled
    estimated_price = db.Column(db.Float)
    final_price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Admin notes
    admin_notes = db.Column(db.Text)
    driver_assigned = db.Column(db.String(100))

    def __repr__(self):
        return f'<Booking {self.booking_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'service_type': self.service_type,
            'vehicle_type': self.vehicle_type,
            'pickup_location': self.pickup_location,
            'dropoff_location': self.dropoff_location,
            'pickup_date': self.pickup_date.isoformat() if self.pickup_date else None,
            'pickup_time': self.pickup_time.strftime('%H:%M') if self.pickup_time else None,
            'passengers': self.passengers,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'special_requests': self.special_requests,
            'return_trip': self.return_trip,
            'waiting_time': self.waiting_time,
            'meet_greet': self.meet_greet,
            'status': self.status,
            'estimated_price': self.estimated_price,
            'final_price': self.final_price,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'admin_notes': self.admin_notes,
            'driver_assigned': self.driver_assigned
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

