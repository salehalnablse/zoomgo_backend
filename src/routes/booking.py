from flask import Blueprint, request, jsonify
from src.models.booking import db, Booking
from src.utils.email_service import EmailService
from datetime import datetime
import random
import string

booking_bp = Blueprint('booking', __name__)
email_service = EmailService()

def generate_booking_id():
    """Generate a unique booking ID"""
    prefix = "ZGR"
    suffix = ''.join(random.choices(string.digits, k=6))
    return f"{prefix}{suffix}"

@booking_bp.route('/bookings', methods=['POST'])
def create_booking():
    """Create a new booking (minimal version)"""
    try:
        data = request.get_json()

        # الحقول المطلوبة فقط حسب الواجهة الأمامية
        required_fields = [
            'service', 'pickup_location', 'dropoff_location',
            'pickup_date', 'pickup_time', 'passengers',
            'first_name', 'email', 'phone'
        ]
        
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # تحويل التاريخ والوقت
        try:
            pickup_date = datetime.strptime(data['pickup_date'], '%Y-%m-%d').date()
            pickup_time = datetime.strptime(data['pickup_time'], '%H:%M').time()
        except ValueError as e:
            return jsonify({'error': f'Invalid date/time format: {str(e)}'}), 400

        # إنشاء رقم حجز عشوائي
        booking_id = generate_booking_id()

        # إنشاء الحجز
        booking = Booking(
            booking_id=booking_id,
            service_type=data['service'],
            pickup_location=data['pickup_location'],
            dropoff_location=data['dropoff_location'],
            pickup_date=pickup_date,
            pickup_time=pickup_time,
            passengers=int(data['passengers'].replace('+', '')) if '+' in str(data['passengers']) else int(data['passengers']),
            first_name=data['first_name'],
            email=data['email'],
            phone=data['phone'],
            special_requests=data.get('special_requests', ''),
            status='pending'
        )

        db.session.add(booking)
        db.session.commit()

        # إرسال إيميلات تأكيد
        email_service.send_booking_confirmation(booking)
        email_service.send_admin_notification(booking)

        return jsonify({
            'success': True,
            'booking_id': booking_id,
            'message': 'Booking created successfully'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create booking: {str(e)}'}), 500

@booking_bp.route('/bookings', methods=['GET'])
def get_bookings():
    """Get all bookings (admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        
        query = Booking.query
        if status:
            query = query.filter(Booking.status == status)
        
        bookings = query.order_by(Booking.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'bookings': [booking.to_dict() for booking in bookings.items],
            'total': bookings.total,
            'pages': bookings.pages,
            'current_page': page
        })
    except Exception as e:
        return jsonify({'error': f'Failed to fetch bookings: {str(e)}'}), 500

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
        updateable_fields = ['status', 'admin_notes', 'driver_assigned']

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

        return jsonify({
            'total_bookings': total_bookings,
            'pending_bookings': pending_bookings,
            'confirmed_bookings': confirmed_bookings,
            'completed_bookings': completed_bookings
        })
    except Exception as e:
        return jsonify({'error': f'Failed to fetch stats: {str(e)}'}), 500
