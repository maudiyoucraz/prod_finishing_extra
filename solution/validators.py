import re
from functools import wraps
from flask import request, jsonify
import jwt

def validate_password(password):
    """
    Валидация пароля:
    - Длина: 6-100 символов
    - Минимум одна строчная буква (a-z)
    - Минимум одна заглавная буква (A-Z)
    - Минимум одна цифра
    """
    if not password or len(password) < 6 or len(password) > 100:
        return False
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    return has_lower and has_upper and has_digit

def validate_login(login):
    """
    Валидация логина:
    - Длина: 1-30 символов
    - Только буквы (a-z, A-Z), цифры (0-9) и дефис (-)
    """
    if not login or len(login) < 1 or len(login) > 30:
        return False
    return bool(re.match(r'^[a-zA-Z0-9-]+$', login))

def validate_email(email):
    """
    Валидация email:
    - Длина: 1-50 символов
    """
    return email and 1 <= len(email) <= 50

def validate_phone(phone):
    """
    Валидация телефона:
    - Опционально
    - Формат: +[цифры]
    - Длина: до 20 символов
    """
    if not phone:
        return True  # Опциональное поле
    if len(phone) > 20:
        return False
    return bool(re.match(r'^\+\d+$', phone))

def validate_image(image):
    """
    Валидация URL изображения:
    - Опционально
    - Длина: 1-200 символов
    """
    if not image:
        return True  # Опциональное поле
    return 1 <= len(image) <= 200

def require_auth(f):
    """
    Декоратор для защиты эндпоинтов.
    Проверяет Bearer токен в заголовке Authorization.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        from app import app
        from models import User
        
        # Получаем токен из заголовка
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"reason": "Missing or invalid authorization header"}), 401
        
        try:
            # Извлекаем токен (формат: "Bearer <token>")
            token = auth_header.split(' ')[1]
            
            # Декодируем JWT
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            
            # Получаем пользователя
            current_user = User.query.get(payload['user_id'])
            if not current_user:
                return jsonify({"reason": "User not found"}), 401
            
        except jwt.ExpiredSignatureError:
            return jsonify({"reason": "Token has expired"}), 401
        except (jwt.InvalidTokenError, KeyError, IndexError):
            return jsonify({"reason": "Invalid token"}), 401
        
        # Передаём current_user в декорированную функцию
        return f(current_user, *args, **kwargs)
    
    return decorated
