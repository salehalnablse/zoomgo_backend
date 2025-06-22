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
