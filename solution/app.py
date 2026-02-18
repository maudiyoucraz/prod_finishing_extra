from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from models import db, Country, User
from services import AuthService
from validators import (
    validate_login, validate_password, validate_email,
    validate_phone, validate_image, require_auth
)
import os

app = Flask(__name__)

# ============================================
# CONFIGURATION
# ============================================

# PostgreSQL connection
postgres_conn = os.environ.get('POSTGRES_CONN', '')
if postgres_conn and postgres_conn.startswith('postgres://'):
    postgres_conn = postgres_conn.replace('postgres://', 'postgresql://', 1)

if not postgres_conn:
    username = os.environ.get('POSTGRES_USERNAME', 'postgres')
    password = os.environ.get('POSTGRES_PASSWORD', 'postgres')
    host = os.environ.get('POSTGRES_HOST', 'localhost')
    port = os.environ.get('POSTGRES_PORT', '5432')
    database = os.environ.get('POSTGRES_DATABASE', 'postgres')
    postgres_conn = f'postgresql://{username}:{password}@{host}:{port}/{database}'

app.config['SQLALCHEMY_DATABASE_URI'] = postgres_conn
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('RANDOM_SECRET', 'dev-secret-key-change-in-production')

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# ============================================
# ROUTES - Step 1: PING
# ============================================

@app.route('/api/ping', methods=['GET'])
def ping():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200

# ============================================
# ROUTES - Step 1: COUNTRIES
# ============================================

@app.route('/api/countries', methods=['GET'])
def get_countries():
    """Get list of countries with optional region filtering"""
    try:
        regions = request.args.getlist('region')
        valid_regions = ['Europe', 'Africa', 'Americas', 'Oceania', 'Asia']
        
        if regions:
            for region in regions:
                if region and region not in valid_regions:
                    return jsonify({"reason": "Invalid region specified"}), 400
        
        if regions:
            countries = Country.query.filter(Country.region.in_(regions)).order_by(Country.alpha2).all()
        else:
            countries = Country.query.order_by(Country.alpha2).all()
        
        result = []
        for country in countries:
            country_data = {
                "name": country.name,
                "alpha2": country.alpha2,
                "alpha3": country.alpha3
            }
            if country.region:
                country_data["region"] = country.region
            result.append(country_data)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"reason": f"Error retrieving countries: {str(e)}"}), 500

@app.route('/api/countries/<string:alpha2>', methods=['GET'])
def get_country(alpha2):
    """Get a single country by alpha2 code"""
    try:
        country = Country.query.filter_by(alpha2=alpha2).first()
        if not country:
            return jsonify({"reason": "Country not found"}), 404
        
        country_data = {
            "name": country.name,
            "alpha2": country.alpha2,
            "alpha3": country.alpha3
        }
        if country.region:
            country_data["region"] = country.region
        
        return jsonify(country_data), 200
    except Exception as e:
        return jsonify({"reason": f"Error retrieving country: {str(e)}"}), 500

# ============================================
# ROUTES - Step 2: REGISTER
# ============================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data:
        return jsonify({"reason": "Invalid request body"}), 400
    
    login = data.get('login')
    password = data.get('password')
    email = data.get('email')
    country_code = data.get('countryCode')
    is_public = data.get('isPublic', True)
    phone = data.get('phone')
    image = data.get('image')
    
    # Validate required fields
    if not all([login, password, email, country_code is not None]):
        return jsonify({"reason": "Missing required fields"}), 400
    
    if not validate_login(login):
        return jsonify({"reason": "Invalid login format"}), 400
    
    if not validate_password(password):
        return jsonify({"reason": "Password does not meet requirements"}), 400
    
    if not validate_email(email):
        return jsonify({"reason": "Invalid email format"}), 400
    
    if phone and not validate_phone(phone):
        return jsonify({"reason": "Invalid phone format"}), 400
    
    if image and not validate_image(image):
        return jsonify({"reason": "Invalid image URL"}), 400
    
    # Validate country exists
    country = Country.query.filter_by(alpha2=country_code).first()
    if not country:
        return jsonify({"reason": "Country not found"}), 400
    
    password_hash = generate_password_hash(password)
    
    try:
        user = AuthService.create_user(
            login=login,
            password_hash=password_hash,
            email=email,
            country_code=country_code,
            is_public=is_public,
            phone=phone,
            image=image
        )
        return jsonify({"profile": user.to_dict(include_private=True)}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"reason": "User with this login, email, or phone already exists"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"reason": f"Registration failed: {str(e)}"}), 500

# ============================================
# ROUTES - Step 3: SIGN-IN
# ============================================

@app.route('/api/auth/sign-in', methods=['POST'])
def sign_in():
    """Authenticate user and return JWT token"""
    data = request.get_json()
    
    if not data:
        return jsonify({"reason": "Invalid request body"}), 400
    
    login = data.get('login')
    password = data.get('password')
    
    if not all([login, password]):
        return jsonify({"reason": "Missing login or password"}), 400
    
    user = User.query.filter_by(login=login).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"reason": "Invalid login or password"}), 401
    
    token = AuthService.generate_token(user.id, app.config['SECRET_KEY'])
    
    return jsonify({"token": token}), 200

# ============================================
# ROUTES - Step 4: PROFILE (preview)
# ============================================

@app.route('/api/me/profile', methods=['GET'])
@require_auth
def get_me_profile(current_user):
    """Get own profile (requires authentication)"""
    return jsonify({"profile": current_user.to_dict(include_private=True)}), 200

@app.route('/api/me/profile', methods=['PATCH'])
@require_auth
def update_me_profile(current_user):
    """Update own profile (requires authentication)"""
    data = request.get_json()
    
    if not data:
        # Пустой запрос - ничего не меняем, возвращаем профиль
        return jsonify({"profile": current_user.to_dict(include_private=True)}), 200
    
    # Получаем поля для обновления
    country_code = data.get('countryCode')
    is_public = data.get('isPublic')
    phone = data.get('phone')
    image = data.get('image')
    
    # Валидация countryCode
    if country_code is not None:
        if not validate_email(country_code):  # Проверка длины
            return jsonify({"reason": "Invalid country code format"}), 400
        country = Country.query.filter_by(alpha2=country_code).first()
        if not country:
            return jsonify({"reason": "Country not found"}), 400
        current_user.country_code = country_code
    
    # Валидация и обновление isPublic
    if is_public is not None:
        current_user.is_public = is_public
    
    # Валидация и обновление phone
    if phone is not None:
        if not validate_phone(phone):
            return jsonify({"reason": "Invalid phone format"}), 400
        # Проверка уникальности (если phone не пустой)
        if phone:
            existing = User.query.filter(User.phone == phone, User.id != current_user.id).first()
            if existing:
                return jsonify({"reason": "Phone number already in use"}), 409
        current_user.phone = phone if phone else None
    
    # Валидация и обновление image
    if image is not None:
        if not validate_image(image):
            return jsonify({"reason": "Invalid image URL"}), 400
        current_user.image = image if image else None
    
    try:
        db.session.commit()
        return jsonify({"profile": current_user.to_dict(include_private=True)}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"reason": "Phone number already in use"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"reason": f"Update failed: {str(e)}"}), 500

# ============================================
# ROUTES - Step 5: GET PROFILE BY LOGIN
# ============================================

@app.route('/api/profiles/<string:login>', methods=['GET'])
@require_auth
def get_profile(current_user, login):
    """Get profile by login (requires authentication)"""
    # Найти пользователя
    target_user = User.query.filter_by(login=login).first()
    
    if not target_user:
        return jsonify({"reason": "User not found"}), 403
    
    # Проверить доступ к профилю
    from services import PostService
    if not PostService.has_access_to_profile(current_user, target_user):
        return jsonify({"reason": "Access denied to this profile"}), 403
    
    # Возвращаем профиль (без email, если это не свой профиль)
    include_private = (current_user.id == target_user.id)
    return jsonify({"profile": target_user.to_dict(include_private=include_private)}), 200

# ============================================
# ROUTES - Step 6: UPDATE PASSWORD
# ============================================

@app.route('/api/me/updatePassword', methods=['POST'])
@require_auth
def update_password(current_user):
    """Update password (requires authentication)"""
    data = request.get_json()
    
    if not data:
        return jsonify({"reason": "Invalid request body"}), 400
    
    old_password = data.get('oldPassword')
    new_password = data.get('newPassword')
    
    if not all([old_password, new_password]):
        return jsonify({"reason": "Missing oldPassword or newPassword"}), 400
    
    # Проверка старого пароля
    if not check_password_hash(current_user.password_hash, old_password):
        return jsonify({"reason": "Old password is incorrect"}), 403
    
    # Валидация нового пароля
    if not validate_password(new_password):
        return jsonify({"reason": "New password does not meet requirements"}), 400
    
    # Обновление пароля
    current_user.password_hash = generate_password_hash(new_password)
    
    try:
        db.session.commit()
        # ВАЖНО: В реальном приложении здесь нужно инвалидировать все старые токены
        # Но т.к. мы используем JWT без хранения в БД, это сложно реализовать
        # Можно добавить поле user.password_changed_at и проверять его в middleware
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"reason": f"Password update failed: {str(e)}"}), 500

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    server_address = os.environ.get('SERVER_ADDRESS', '0.0.0.0:8080')
    server_port = os.environ.get('SERVER_PORT', '8080')
    
    if ':' in server_address:
        host, port = server_address.rsplit(':', 1)
        port = int(port)
    else:
        host = '0.0.0.0'
        port = int(server_port)
    
    app.run(host=host, port=port)
