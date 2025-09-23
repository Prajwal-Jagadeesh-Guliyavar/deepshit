from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import User, MedicalReport
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
from werkzeug.utils import secure_filename
from datetime import timedelta

# Create blueprints
auth_bp = Blueprint('auth', __name__)
reports_bp = Blueprint('reports', __name__)
jwt = JWTManager()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password') or not data.get('name') or not data.get('date_of_birth') or not data.get('gender'):
        return jsonify({'error': 'Name, email, password, date of birth, and gender are required'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400

    user = User(
        name=data['name'],
        email=data['email'],
        date_of_birth=data['date_of_birth'],
        gender=data['gender']
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': 'User registered successfully',
        'user_id': user.user_id
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401

    access_token = create_access_token(
        identity=user.user_id,
        expires_delta=timedelta(days=7)
    )

    return jsonify({
        'access_token': access_token,
        'user_id': user.user_id,
        'email': user.email
    }), 200

@reports_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_report():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        # Create upload directory if it doesn't exist
        upload_folder = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        # Create report record
        current_user_id = get_jwt_identity()
        report = MedicalReport(
            user_id=current_user_id,
            original_filename=filename,
            file_path=file_path,
            processing_status='pending'
        )

        db.session.add(report)
        db.session.commit()

        # Trigger Celery task for processing
        from app.tasks import process_medical_report
        process_medical_report.delay(report.report_id)

        return jsonify({
            'message': 'File uploaded successfully',
            'report_id': report.report_id,
            'status': 'processing_started'
        }), 202

    return jsonify({'error': 'Invalid file type. Only PDF, and DOCX files are allowed.'}), 400

@reports_bp.route('/reports', methods=['GET'])
@jwt_required()
def get_reports():
    current_user_id = get_jwt_identity()
    reports = MedicalReport.query.filter_by(user_id=current_user_id).all()

    reports_data = []
    for report in reports:
        reports_data.append({
            'report_id': report.report_id,
            'original_filename': report.original_filename,
            'upload_timestamp': report.upload_timestamp.isoformat(),
            'processing_status': report.processing_status,
            'simplified_summary': report.simplified_summary,
            'extracted_features': report.extracted_features
        })

    return jsonify({'reports': reports_data}), 200

@reports_bp.route('/reports/<int:report_id>', methods=['GET'])
@jwt_required()
def get_report(report_id):
    current_user_id = get_jwt_identity()
    report = MedicalReport.query.filter_by(
        report_id=report_id,
        user_id=current_user_id
    ).first()

    if not report:
        return jsonify({'error': 'Report not found'}), 404

    return jsonify({
        'report_id': report.report_id,
        'original_filename': report.original_filename,
        'upload_timestamp': report.upload_timestamp.isoformat(),
        'processing_status': report.processing_status,
        'simplified_summary': report.simplified_summary,
        'extracted_features': report.extracted_features
    }), 200