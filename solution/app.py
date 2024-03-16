from flask import Flask, request, jsonify
from flask import Flask, request, jsonify, current_app, reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
import uuid
import os

app = Flask(__name__)

@app.route('/api/ping', methods=['GET'])
def send():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run()

# from flask import Flask, request, jsonify, current_app, reqparse
# from flask_sqlalchemy import SQLAlchemy
# from flask_restful import Api, Resource
# from sqlalchemy.exc import IntegrityError
# from sqlalchemy.sql import text
# from werkzeug.security import generate_password_hash, check_password_hash
# from datetime import datetime, timedelta
# import jwt
# import uuid
# import os

# app = Flask(__name__)
# api = Api(app)

# # Configure PostgreSQL connection
# #app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://username:password@localhost:5432/dbname"
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["POSTGRES_CONN"].replace("postgres://", "postgresql://")

# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# # Initialize SQLAlchemy
# db = SQLAlchemy(app)

# # Define Country model
# class Country(db.Model):
#     __tablename__ = 'countries'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100))
#     alpha2 = db.Column(db.String(2), unique=True)
#     alpha3 = db.Column(db.String(3), unique=True)
#     region = db.Column(db.String(50))

# class Token(db.Model):
#     __tablename__ = 'tokens'
#     id = db.Column(db.Integer, primary_key=True)
#     token = db.Column(db.String(500), unique=True, nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     # Add any other fields you need for tokens

#     def __repr__(self):
#         return f'<Token {self.token}>'
    
# # Модель пользователя
# friends = db.Table('friends',
#     db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
#     db.Column('friend_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
#     db.Column('added_at', db.DateTime, default=datetime.utcnow)  # Добавлено поле для хранения времени добавления друга
# )

# class Friendship(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     added_at = db.Column(db.DateTime, default=datetime.utcnow)


# class User(db.Model):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(50), unique=True, nullable=False)
#     password = db.Column(db.String(255), nullable=False)
#     email = db.Column(db.String(100), unique=True, nullable=False)
#     country_code = db.Column(db.String(2), nullable=False)
#     is_public = db.Column(db.Boolean, default=True)
#     phone = db.Column(db.String(15))
#     image = db.Column(db.String(255))
#     last_friends_update = db.Column(db.DateTime, default=datetime.utcnow)

#     # Отношение многие ко многим для друзей
#     friends = db.relationship('User', secondary=friends,
#                               primaryjoin=(friends.c.user_id == id),
#                               secondaryjoin=(friends.c.friend_id == id),
#                               backref=db.backref('friend_of', lazy='dynamic'))

# def get_user_friends(username, offset=0, limit=5):
#     # Retrieve the user
#     user = User.query.filter_by(username=username).first()

#     # Check if the user exists
#     if not user:
#         return jsonify({"reason": "User not found"}), 404

#     # Query friend relationships for the given user
#     friendships = Friendship.query.filter_by(user_id=user.id).order_by(Friendship.added_at.desc()).offset(offset).limit(limit).all()

#     # Extract friend information
#     friends_list = [{
#         "login": friend.friend.username,
#         "addedAt": friend.added_at.isoformat()
#     } for friend in friendships]

#     return friends_list

# # Модель публикации
# class Post(db.Model):
#     id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True, nullable=False)
#     content = db.Column(db.Text, nullable=False)
#     author = db.Column(db.String(50), nullable=False)
#     tags = db.Column(db.ARRAY(db.String), nullable=True)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     likes_count = db.Column(db.Integer, default=0)
#     dislikes_count = db.Column(db.Integer, default=0)

# # Модель реакции пользователя на публикацию
# class Reaction(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     post_id = db.Column(db.String(36), db.ForeignKey('post.id'), nullable=False)
#     reaction_type = db.Column(db.String(10), nullable=False)  # 'like' или 'dislike'

#     # Отношение между пользователем и его реакциями
#     user = db.relationship('User', backref='reactions')
    
#     # Отношение между публикацией и ее реакциями
#     post = db.relationship('Post', backref='reactions')
# # Create tables
# with app.app_context():
#     db.create_all()

# @app.route('/api/ping', methods=['GET'])
# def send():
#     return jsonify({"status": "ok"}), 200
# # Country resource
# class CountryResource(Resource):
#     def get(self, alpha2=None):
#         if alpha2:
#             country = Country.query.filter_by(alpha2=alpha2).first()
#             if country:
#                 return jsonify({
#                     "name": country.name,
#                     "alpha2": country.alpha2,
#                     "alpha3": country.alpha3,
#                     "region": country.region
#                 })
#             else:
#                 return jsonify({"error": "Country not found"}), 404
#         else:
#             region = request.args.get('region')
#             if region:
#                 countries = Country.query.filter_by(region=region).all()
#             else:
#                 countries = Country.query.all()

#             country_list = []
#             for country in countries:
#                 country_list.append({
#                     "name": country.name,
#                     "alpha2": country.alpha2,
#                     "alpha3": country.alpha3,
#                     "region": country.region
#                 })

#             return jsonify(country_list)

# api.add_resource(CountryResource, '/api/countries', '/countries/<string:alpha2>')

# # User registration endpoint
# class RegisterResource(Resource):
#     def post(self):
#         data = request.get_json()
#         username = data.get('login')
#         password = data.get('password')
#         email = data.get('email')
#         country_code = data.get('countryCode')
#         is_public = data.get('isPublic', True)
#         phone = data.get('phone')
#         image = data.get('image')

#         # Validate the input
#         if not all([username, password, email, country_code]):
#             return jsonify({"error": "Username, password, email, and countryCode are required"}), 400

#         hashed_password = generate_password_hash(password, method='bcrypt')

#         new_user = User(username=username, password=hashed_password, email=email, country_code=country_code,
#                         is_public=is_public, phone=phone, image=image)

#         try:
#             db.session.add(new_user)
#             db.session.commit()
#             return jsonify({
#                 "profile": {
#                     "login": new_user.username,
#                     "email": new_user.email,
#                     "countryCode": new_user.country_code,
#                     "isPublic": new_user.is_public,
#                     "phone": new_user.phone,
#                     "image": new_user.image
#                 }
#             }), 201
#         except IntegrityError:
#             db.session.rollback()
#             return jsonify({"error": "User with this username or email already exists"}), 409

# api.add_resource(RegisterResource, '/api/auth/register')

# # Authentication endpoint
# class SignInResource(Resource):
#     def post(self):
#         data = request.get_json()
#         username = data.get('login')
#         password = data.get('password')

#         user = User.query.filter_by(username=username).first()

#         if user and check_password_hash(user.password, password):
#             # Check if the user already has an active token
#             existing_token = Token.query.filter_by(user_id=user.id).first()
#             if existing_token:
#                 return jsonify({"error": "Token already issued for this user"}), 400

#             # Generate JWT token
#             token_payload = {
#                 'user_id': user.id,
#                 'exp': datetime.utcnow() + timedelta(hours=1)
#             }
#             jwt_token = jwt.encode(token_payload, os.environ.get('RANDOM_SECRET'), algorithm='HS256')

#             # Save token to the database
#             new_token = Token(token=jwt_token.decode('utf-8'), user_id=user.id)
#             db.session.add(new_token)
#             db.session.commit()

#             return jsonify({"token": jwt_token.decode('utf-8')}), 200
#         else:
#             return jsonify({"error": "Invalid credentials"}), 401

# # existing code
# api.add_resource(SignInResource, '/api/auth/sign-in')
# # Profile resource
# class ProfileResource(Resource):
#     def get(self, login):
#         # Получаем токен из заголовка Authorization
#         token = request.headers.get('Authorization')

#         # Проверяем наличие токена (в реальном приложении проверяйте его валидность)
#         if not token:
#             return jsonify({"reason": "Missing or invalid token"}), 401

#         # Получаем профиль пользователя
#         user = User.query.filter_by(username=login).first()

#         # Проверяем существование пользователя и доступ к профилю
#         if not user or (not user.is_public and token != user.token):
#             return jsonify({"reason": "Profile not found or access denied"}), 403

#         # Возвращаем профиль пользователя
#         return jsonify({
#             "login": user.username,
#             "email": user.email,
#             "countryCode": user.country_code,
#             "isPublic": user.is_public,
#             "phone": user.phone,
#             "image": user.image
#         })

# api.add_resource(ProfileResource, '/api/profiles/<string:login>')

# # Me Profile resource
# class MeProfileResource(Resource):
#     def get(self):
#         # Получаем токен из заголовка Authorization
#         token = request.headers.get('Authorization')

#         # Проверяем наличие токена (в реальном приложении проверяйте его валидность)
#         if not token:
#             return jsonify({"reason": "Missing or invalid token"}), 401

#         # Проверяем срок действия токена
#         if not self.is_valid_token(token):
#             return jsonify({"reason": "Token has expired"}), 401

#         # Получаем профиль пользователя
#         user = User.query.filter_by(token=token).first()

#         # Проверяем существование пользователя
#         if not user:
#             return jsonify({"reason": "User not found"}), 404

#         # Возвращаем профиль пользователя
#         return jsonify({
#             "login": user.username,
#             "email": user.email,
#             "countryCode": user.country_code,
#             "isPublic": user.is_public,
#             "phone": user.phone,
#             "image": user.image
#         })

#     def patch(self):
#         # Получаем токен из заголовка Authorization
#         token = request.headers.get('Authorization')

#         # Проверяем наличие токена (в реальном приложении проверяйте его валидность)
#         if not token:
#             return jsonify({"reason": "Missing or invalid token"}), 401

#         # Проверяем срок действия токена
#         if not self.is_valid_token(token):
#             return jsonify({"reason": "Token has expired"}), 401

#         # Получаем пользователя по токену
#         user = User.query.filter_by(token=token).first()

#         # Проверяем существование пользователя
#         if not user:
#             return jsonify({"reason": "User not found"}), 404

#         # Получаем данные из тела запроса
#         data = request.get_json()

#         # Validate data format and requirements
#         try:
#             self.validate_data(data)
#         except ValueError as e:
#             return jsonify({"reason": str(e)}), 400

#         # Update user profile
#         user = self.update_user_profile(user, data)

#         try:
#             # Save changes to the database
#             db.session.commit()

#             return jsonify({
#                 "login": user.username,
#                 "email": user.email,
#                 "countryCode": user.country_code,
#                 "isPublic": user.is_public,
#                 "phone": user.phone,
#                 "image": user.image
#             }), 200
#         except IntegrityError:
#             db.session.rollback()
#             return jsonify({"reason": "User with this data already exists"}), 409
#         except Exception as e:
#             db.session.rollback()
#             return jsonify({"reason": str(e)}), 500

#     def is_valid_token(self, token):
#         # Implement token expiration logic
#         try:
#             payload = jwt.decode(token.split(' ')[1], current_app.config['SECRET_KEY'], algorithms=['HS256'])
#             expiration_time = payload.get('exp', 0)
#             current_time = datetime.utcnow().timestamp()
#             return expiration_time > current_time
#         except jwt.ExpiredSignatureError:
#             return False
#         except jwt.InvalidTokenError:
#             return False

# api.add_resource(MeProfileResource, '/api/me/profile')

# # # Update Password resource
# class UpdatePasswordResource(Resource):
#     def patch(self):
#         # Получаем токен из заголовка Authorization
#         token = request.headers.get('Authorization')

#         # Проверяем наличие токена (в реальном приложении проверяйте его валидность)
#         if not token:
#             return jsonify({"reason": "Missing or invalid token"}), 401

#         # Получаем пользователя по токену
#         user = User.query.filter_by(token=token).first()

#         # Проверяем существование пользователя
#         if not user:
#             return jsonify({"reason": "User not found"}), 404

#         # Получаем данные из тела запроса
#         data = request.get_json()
#         old_password = data.get('oldPassword')
#         new_password = data.get('newPassword')

#         # Проверяем, что переданы старый и новый пароли
#         if not old_password or not new_password:
#             return jsonify({"reason": "Old and new passwords are required"}), 400

#         # Проверяем совпадение старого пароля
#         if not check_password_hash(user.password, old_password):
#             return jsonify({"reason": "Incorrect old password"}), 401

#         # Обновляем пароль
#         user.password = generate_password_hash(new_password, method='bcrypt')

#         try:
#             # Деактивируем все ранее выписанные токены
#             user.token = None

#             # Сохраняем изменения
#             db.session.commit()

#             return jsonify({"status": "Password updated successfully"}), 200
#         except Exception as e:
#             db.session.rollback()
#             return jsonify({"reason": str(e)}), 500

# api.add_resource(UpdatePasswordResource, '/api/me/updatePassword')

# class FriendsAddResource(Resource):
#     def post(self):
#         # Получаем токен из заголовка Authorization
#         token = request.headers.get('Authorization')

#         # Проверяем наличие токена
#         if not token:
#             return jsonify({"reason": "Missing or invalid token"}), 401

#         # Проверяем срок действия токена
#         if not self.is_valid_token(token):
#             return jsonify({"reason": "Token has expired"}), 401

#         # Получаем пользователя, добавляющего в друзья
#         user = User.query.filter_by(token=token).first()

#         # Проверяем существование пользователя
#         if not user:
#             return jsonify({"reason": "User not found"}), 404

#         # Получаем данные из тела запроса
#         data = request.get_json()
#         friend_login = data.get('login')

#         # Проверяем, что передан логин друга
#         if not friend_login:
#             return jsonify({"reason": "Friend's login is required"}), 400

#         # Проверяем, что пользователь не пытается добавить самого себя в друзья
#         if user.username == friend_login:
#             return jsonify({"status": "ok"}), 200

#         # Получаем пользователя, которого добавляем в друзья
#         friend = User.query.filter_by(username=friend_login).first()

#         # Проверяем существование друга
#         if not friend:
#             return jsonify({"reason": "Friend not found"}), 404

#         # Проверяем, что пользователь еще не добавлен в друзья
#         if self.are_friends(user, friend):
#             return jsonify({"status": "ok"}), 200

#         # Добавляем пользователя в друзья
#         user.friends.append(friend)

#         try:
#             # Сохраняем изменения
#             db.session.commit()
#             return jsonify({"status": "ok"}), 200
#         except Exception as e:
#             db.session.rollback()
#             return jsonify({"reason": str(e)}), 500

#     def is_valid_token(self, token):
#         # Implement token expiration logic
#         try:
#             payload = jwt.decode(token.split(' ')[1], current_app.config['SECRET_KEY'], algorithms=['HS256'])
#             expiration_time = payload.get('exp', 0)
#             current_time = datetime.utcnow().timestamp()
#             return expiration_time > current_time
#         except jwt.ExpiredSignatureError:
#             return False
#         except jwt.InvalidTokenError:
#             return False

#     def are_friends(self, user, friend):
#         # Check if user and friend are already friends
#         return friend in user.friends or user in friend.friends

# api.add_resource(FriendsAddResource, '/api/friends/add')

# class FriendsRemoveResource(Resource):
#     def post(self):
#         # Получаем токен из заголовка Authorization
#         token = request.headers.get('Authorization')

#         # Проверяем наличие токена (в реальном приложении проверяйте его валидность)
#         if not token or not self.is_valid_token(token):
#             return jsonify({"reason": "Missing or invalid token"}), 401

#         # Получаем пользователя, удаляющего друга
#         user = User.query.filter_by(token=token).first()

#         # Проверяем существование пользователя
#         if not user:
#             return jsonify({"reason": "User not found"}), 404

#         # Получаем данные из тела запроса
#         data = request.get_json()
#         friend_login = data.get('login')

#         # Проверяем, что передан логин друга
#         if not friend_login:
#             return jsonify({"reason": "Friend's login is required"}), 400

#         # Получаем пользователя, которого удаляем из друзей
#         friend = User.query.filter_by(username=friend_login).first()

#         # Проверяем существование друга
#         if not friend:
#             return jsonify({"reason": "Friend not found"}), 404

#         # Проверяем, что пользователь и друг являются друзьями
#         if not self.are_friends(user, friend):
#             return jsonify({"status": "ok"}), 200

#         # Удаляем друга из списка друзей
#         user.friends.remove(friend)

#         try:
#             # Сохраняем изменения
#             db.session.commit()
#             return jsonify({"status": "ok"}), 200
#         except Exception as e:
#             db.session.rollback()
#             return jsonify({"reason": str(e)}), 500

#     def is_valid_token(self, token):
#         try:
#             jwt.decode(token.split(' ')[1], current_app.config['SECRET_KEY'], algorithms=['HS256'])
#             return True
#         except jwt.ExpiredSignatureError:
#             return False
#         except jwt.InvalidTokenError:
#             return False

#     def are_friends(self, user, friend):
#         # Check if user and friend are friends
#         return friend in user.friends and user in friend.friends

# api.add_resource(FriendsRemoveResource, '/api/friends/remove')

# class FriendsListResource(Resource):
#     def get(self):
#         # Получаем токен из заголовка Authorization
#         token = request.headers.get('Authorization')

#         # Проверяем наличие токена (в реальном приложении проверяйте его валидность)
#         if not token or not self.is_valid_token(token):
#             return jsonify({"reason": "Missing or invalid token"}), 401

#         # Получаем пользователя
#         user = User.query.filter_by(token=token).first()

#         # Проверяем существование пользователя
#         if not user:
#             return jsonify({"reason": "User not found"}), 404

#         # Получаем параметры пагинации
#         parser = reqparse.RequestParser()
#         parser.add_argument('offset', type=int, default=0)
#         parser.add_argument('limit', type=int, default=5)  # Обновлено значение по умолчанию
#         args = parser.parse_args()

#         # Получаем порцию друзей в соответствии с пагинацией
#         friends = user.friends.order_by(User.last_friends_update.desc()).offset(args['offset']).limit(args['limit']).all()

#         # Возвращаем список друзей
#         friends_list = [{
#             "login": friend.username,
#             "addedAt": friend.last_friends_update.isoformat()  # Преобразуем дату в формат ISO
#         } for friend in friends]

#         return jsonify(friends_list)

#     def is_valid_token(self, token):
#         try:
#             jwt.decode(token.split(' ')[1], current_app.config['SECRET_KEY'], algorithms=['HS256'])
#             return True
#         except jwt.ExpiredSignatureError:
#             return False
#         except jwt.InvalidTokenError:
#             return False

# api.add_resource(FriendsListResource, '/api/friends')

# class NewPostResource(Resource):
#     def post(self):
#         # Получаем токен из заголовка Authorization
#         token = request.headers.get('Authorization')

#         # Проверяем наличие токена (в реальном приложении проверяйте его валидность)
#         if not token or not self.is_valid_token(token):
#             return jsonify({"reason": "Missing or invalid token"}), 401

#         # Получаем пользователя, выполняющего запрос
#         user = User.query.filter_by(token=token).first()

#         # Проверяем существование пользователя
#         if not user:
#             return jsonify({"reason": "User not found"}), 404

#         # Получаем данные из тела запроса
#         data = request.get_json()

#         # Создаем новую публикацию
#         post = Post(
#             content=data.get("content"),
#             tags=data.get("tags"),
#             author=user.username,
#             created_at=datetime.utcnow(),
#             likes_count=0,
#             dislikes_count=0
#         )

#         # Сохраняем публикацию в базу данных
#         db.session.add(post)
#         db.session.commit()

#         # Возвращаем информацию о созданной публикации
#         response_data = {
#             "id": str(post.id),
#             "content": post.content,
#             "author": post.author,
#             "tags": post.tags,
#             "createdAt": post.created_at.isoformat(),
#             "likesCount": post.likes_count,
#             "dislikesCount": post.dislikes_count
#         }

#         return jsonify(response_data), 200

#     def is_valid_token(self, token):
#         try:
#             jwt.decode(token.split(' ')[1], current_app.config['SECRET_KEY'], algorithms=['HS256'])
#             return True
#         except jwt.ExpiredSignatureError:
#             return False
#         except jwt.InvalidTokenError:
#             return False

# # Ресурс для обработки запроса на получение публикации по ID
# class PostResource(Resource):
#     def get(self, post_id):
#         # Получаем токен из заголовка Authorization
#         token = request.headers.get('Authorization')

#         # Проверяем наличие токена (в реальном приложении проверяйте его валидность)
#         if not token or not self.is_valid_token(token):
#             return jsonify({"reason": "Missing or invalid token"}), 401

#         # Получаем пользователя, выполняющего запрос
#         user = User.query.filter_by(token=token).first()

#         # Проверяем существование пользователя
#         if not user:
#             return jsonify({"reason": "User not found"}), 404

#         # Получаем публикацию из базы данных
#         post = Post.query.get(post_id)

#         # Проверяем существование публикации
#         if not post:
#             return jsonify({"reason": "Post not found"}), 404

#         # Проверяем доступ пользователя к публикации (логика доступа может быть изменена)
#         if user.username != post.author and user.username not in get_user_friends(post.author):
#             return jsonify({"reason": "Access denied"}), 403

#         # Возвращаем информацию о публикации
#         response_data = {
#             "id": str(post.id),
#             "content": post.content,
#             "author": post.author,
#             "tags": post.tags,
#             "createdAt": post.created_at.isoformat(),
#             "likesCount": post.likes_count,
#             "dislikesCount": post.dislikes_count
#         }

#         return jsonify(response_data), 200

#     def is_valid_token(self, token):
#         try:
#             jwt.decode(token.split(' ')[1], current_app.config['SECRET_KEY'], algorithms=['HS256'])
#             return True
#         except jwt.ExpiredSignatureError:
#             return False
#         except jwt.InvalidTokenError:
#             return False

# # Ресурс для обработки запросов на получение своей ленты и ленты другого пользователя
# class FeedResource(Resource):
#     def get(self, feed_type):
#         # Получаем токен из заголовка Authorization
#         token = request.headers.get('Authorization')

#         # Проверяем наличие токена (в реальном приложении проверяйте его валидность)
#         if not token or not self.is_valid_token(token):
#             return jsonify({"reason": "Missing or invalid token"}), 401

#         # Получаем пользователя, выполняющего запрос
#         user = User.query.filter_by(token=token).first()

#         # Проверяем существование пользователя
#         if not user:
#             return jsonify({"reason": "User not found"}), 404

#         # Определяем, какой тип ленты запрашивается
#         if feed_type == 'my':
#             # Получаем свою ленту с использованием пагинации
#             parser = reqparse.RequestParser()
#             parser.add_argument('offset', type=int, default=0)
#             parser.add_argument('limit', type=int, default=5)
#             args = parser.parse_args()

#             posts = Post.query.filter_by(author=user.username).order_by(Post.created_at.desc()).offset(args['offset']).limit(args['limit']).all()

#         elif feed_type != user.username and user.username not in get_user_friends(feed_type):
#             # Проверяем, что пользователь имеет доступ к ленте другого пользователя
#             return jsonify({"reason": "Access denied"}), 403

#         else:
#             # Получаем ленту другого пользователя с использованием пагинации
#             parser = reqparse.RequestParser()
#             parser.add_argument('offset', type=int, default=0)
#             parser.add_argument('limit', type=int, default=5)
#             args = parser.parse_args()

#             posts = Post.query.filter_by(author=feed_type).order_by(Post.created_at.desc()).offset(args['offset']).limit(args['limit']).all()

#         # Возвращаем список публикаций
#         posts_list = [{
#             "id": str(post.id),
#             "content": post.content,
#             "author": post.author,
#             "tags": post.tags,
#             "createdAt": post.created_at.isoformat(),
#             "likesCount": post.likes_count,
#             "dislikesCount": post.dislikes_count
#         } for post in posts]

#         return jsonify(posts_list), 200

#     def is_valid_token(self, token):
#         try:
#             jwt.decode(token.split(' ')[1], current_app.config['SECRET_KEY'], algorithms=['HS256'])
#             return True
#         except jwt.ExpiredSignatureError:
#             return False
#         except jwt.InvalidTokenError:
#             return False

# # Ресурс для обработки запросов на лайк и дизлайк публикации
# class ReactionResource(Resource):
#     def post(self, reaction_type, post_id):
#         # Получаем токен из заголовка Authorization
#         token = request.headers.get('Authorization')

#         # Проверяем наличие токена (в реальном приложении проверяйте его валидность)
#         if not token or not self.is_valid_token(token):
#             return jsonify({"reason": "Missing or invalid token"}), 401

#         # Получаем пользователя, выполняющего запрос
#         user = User.query.filter_by(token=token).first()

#         # Проверяем существование пользователя
#         if not user:
#             return jsonify({"reason": "User not found"}), 404

#         # Получаем публикацию из базы данных
#         post = Post.query.get(post_id)

#         # Проверяем существование публикации
#         if not post:
#             return jsonify({"reason": "Post not found"}), 404

#         # Проверяем доступ пользователя к публикации (логика доступа может быть изменена)
#         if user.username != post.author and user.username not in get_user_friends(post.author):
#             return jsonify({"reason": "Access denied"}), 403

#         # Выполняем логику лайка или дизлайка
#         if reaction_type == 'like':
#             user_reaction = Reaction.query.filter_by(user_id=user.id, post_id=post.id).first()
#             if user_reaction:
#                 user_reaction.reaction_type = 'like'
#             else:
#                 user_reaction = Reaction(user_id=user.id, post_id=post.id, reaction_type='like')
#                 db.session.add(user_reaction)
#             post.likes_count = Reaction.query.filter_by(post_id=post.id, reaction_type='like').count()

#         elif reaction_type == 'dislike':
#             user_reaction = Reaction.query.filter_by(user_id=user.id, post_id=post.id).first()
#             if user_reaction:
#                 user_reaction.reaction_type = 'dislike'
#             else:
#                 user_reaction = Reaction(user_id=user.id, post_id=post.id, reaction_type='dislike')
#                 db.session.add(user_reaction)
#             post.dislikes_count = Reaction.query.filter_by(post_id=post.id, reaction_type='dislike').count()

#         db.session.commit()

#         # Возвращаем обновленную информацию о публикации
#         response_data = {
#             "id": str(post.id),
#             "content": post.content,
#             "author": post.author,
#             "tags": post.tags,
#             "createdAt": post.created_at.isoformat(),
#             "likesCount": post.likes_count,
#             "dislikesCount": post.dislikes_count
#         }

#         return jsonify(response_data), 200

#     def is_valid_token(self, token):
#         try:
#             jwt.decode(token.split(' ')[1], current_app.config['SECRET_KEY'], algorithms=['HS256'])
#             return True
#         except jwt.ExpiredSignatureError:
#             return False
#         except jwt.InvalidTokenError:
#             return False

# # Добавляем ресурсы к приложению
# api.add_resource(NewPostResource, '/api/posts/new')
# api.add_resource(PostResource, '/api/posts/<post_id>')
# api.add_resource(FeedResource, '/api/posts/feed/<feed_type>')
# api.add_resource(ReactionResource, '/api/posts/<reaction_type>/<post_id>')

# existing code
# if __name__ == '__main__':
#     app.run(host=os.environ.get('SERVER_ADDRESS', '0.0.0.0'), port=int(os.environ.get('SERVER_PORT', 8080)))

if __name__ == "__main__":
    app.run()