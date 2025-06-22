from flask import Blueprint, request, jsonify
from src.models.booking import db, Booking
from src.utils.email_service import EmailService
from datetime import datetime, date, time
import random
import string

booking_bp = Blueprint('booking', __name__)
email_service = EmailService()

def generate_booking_id():
    """Generate a unique booking ID"""
    prefix = "ZGR"
    suffix = ''.join(random.choices(string.digits, k=6))
    return f"{prefix}{suffix}"

def calculate_estimated_price(service_type, vehicle_type, passengers):
    """Calculate estimated price based on service and vehicle type"""
    base_prices = {
        'airport': 75,
        'corporate': 60,
        'event': 90,
        'tour': 120
    }

    vehicle_multipliers = {
        'standard': 1.0,
        'luxury': 1.5,
        'suv': 1.3,
        'van': 1.8,
        'limousine': 2.5
    }

    base_price = base_prices.get(service_type, 75)
    multiplier = vehicle_multipliers.get(vehicle_type, 1.0)

    # Additional charge for large groups
    if passengers and int(passengers) > 6:
        multiplier *= 1.5

    return round(base_price * multiplier, 2)

@booking_bp.route('/bookings', methods=['POST'])
def create_booking():
    """Create a new booking"""
    try:
        data = request.get_json()

        # Validate required fields (مطابقة لحقول HTML)
        required_fields = [
            'service', 'pickup_location', 'dropoff_location',
            'pickup_date', 'pickup_time', 'passengers',
            'first_name', 'last_name', 'email', 'phone'
        ]

        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Parse date and time
        try:
            pickup_date = datetime.strptime(data['pickup_date'], '%Y-%m-%d').date()
            pickup_time = datetime.strptime(data['pickup_time'], '%H:%M').time()
        except ValueError as e:
            return jsonify({'error': f'Invalid date/time format: {str(e)}'}), 400

        # Generate booking ID
        booking_id = generate_booking_id()

        # Calculate estimated price
        estimated_price = calculate_estimated_price(
            data['service'],
            data.get('vehicle_type', 'standard'),
            data['passengers']
        )

        # Create booking object
        booking = Booking(
            booking_id=booking_id,
            service_type=data['service'],
            vehicle_type=data.get('vehicle_type', 'standard'),
            pickup_location=data['pickup_location'],
            dropoff_location=data['dropoff_location'],
            pickup_date=pickup_date,
            pickup_time=pickup_time,
            passengers=int(data['passengers'].replace('+', '')) if '+' in str(data['passengers']) else int(data['passengers']),
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data['phone'],
            special_requests=data.get('special_requests', ''),
            return_trip=data.get('return_trip', False),
            waiting_time=data.get('waiting_time', False),
            meet_greet=data.get('meet_greet', False),
            estimated_price=estimated_price,
            status='pending'
        )

        # Save to database
        db.session.add(booking)
        db.session.commit()

        # Send confirmation emails
        email_service.send_booking_confirmation(booking)
        email_service.send_admin_notification(booking)

        return jsonify({
            'success': True,
            'booking_id': booking_id,
            'estimated_price': estimated_price,
            'message': 'Booking created successfully'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create booking: {str(e)}'}), 500

@booking_bp.route('/bookings/<booking_id>', methods=['GET'])
def get_booking(booking_id):
    """Get a specific booking"""
    try:
        booking = Booking.query.filter_by(booking_id=booking_id).first()

        if not booking:
            return jsonify({'error': 'Booking not found'}), 404

        return jsonify(booking.to_dict())

    except Exception as e:
        return jsonify({'error': f'Failed to fetch booking: {str(e)}'}), 500

@booking_bp.route('/bookings/<booking_id>', methods=['PUT'])
def update_booking(booking_id):
    """Update a booking (admin only)"""
    try:
        booking = Booking.query.filter_by(booking_id=booking_id).first()

        if not booking:
            return jsonify({'error': 'Booking not found'}), 404

        data = request.get_json()

        # Update allowed fields
        updateable_fields = [
            'status', 'final_price', 'admin_notes', 'driver_assigned'
        ]

        for field in updateable_fields:
            if field in data:
                setattr(booking, field, data[field])

        booking.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Booking updated successfully',
            'booking': booking.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update booking: {str(e)}'}), 500

@booking_bp.route('/bookings/<booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    """Delete a booking (admin only)"""
    try:
        booking = Booking.query.filter_by(booking_id=booking_id).first()

        if not booking:
            return jsonify({'error': 'Booking not found'}), 404

        db.session.delete(booking)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Booking deleted successfully'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete booking: {str(e)}'}), 500

@booking_bp.route('/stats', methods=['GET'])
def get_booking_stats():
    """Get booking statistics (admin only)"""
    try:
        total_bookings = Booking.query.count()
        pending_bookings = Booking.query.filter_by(status='pending').count()
        confirmed_bookings = Booking.query.filter_by(status='confirmed').count()
        completed_bookings = Booking.query.filter_by(status='completed').count()

        # Calculate total revenue from completed bookings
        total_revenue = db.session.query(db.func.sum(Booking.final_price)).filter_by(status='completed').scalar() or 0

        return jsonify({
            'total_bookings': total_bookings,
            'pending_bookings': pending_bookings,
            'confirmed_bookings': confirmed_bookings,
            'completed_bookings': completed_bookings,
            'total_revenue': float(total_revenue)
        })

    except Exception as e:
        return jsonify({'error': f'Failed to fetch stats: {str(e)}'}), 500

