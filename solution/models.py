from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class Country(db.Model):
    """Модель страны"""
    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    alpha2 = db.Column(db.String(2))
    alpha3 = db.Column(db.String(3))
    region = db.Column(db.String(50))

class User(db.Model):
    """Модель пользователя"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    country_code = db.Column(db.String(2), nullable=False)
    is_public = db.Column(db.Boolean, default=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    image = db.Column(db.String(200), nullable=True)
    
    def to_dict(self, include_private=False):
        """Сериализация пользователя в JSON"""
        data = {
            'login': self.login,
            'countryCode': self.country_code,
            'isPublic': self.is_public
        }
        if include_private:
            data['email'] = self.email
        if self.phone:
            data['phone'] = self.phone
        if self.image:
            data['image'] = self.image
        return data

class Friendship(db.Model):
    """Модель дружбы (односторонняя связь)"""
    __tablename__ = 'friendships'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Отношения
    user = db.relationship('User', foreign_keys=[user_id], backref='friendships')
    friend = db.relationship('User', foreign_keys=[friend_id])
    
    # Уникальность связи
    __table_args__ = (
        db.UniqueConstraint('user_id', 'friend_id', name='unique_friendship'),
    )

class Post(db.Model):
    """Модель публикации"""
    __tablename__ = 'posts'
    id = db.Column(db.String(100), primary_key=True)
    content = db.Column(db.String(1000), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tags = db.Column(db.JSON, default=list, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    likes_count = db.Column(db.Integer, default=0, nullable=False)
    dislikes_count = db.Column(db.Integer, default=0, nullable=False)
    
    # Отношения
    author = db.relationship('User', backref='posts')
    
    def to_dict(self):
        """Сериализация поста в JSON"""
        return {
            'id': self.id,
            'content': self.content,
            'author': self.author.login,
            'tags': self.tags or [],
            'createdAt': self.created_at.isoformat(),
            'likesCount': self.likes_count,
            'dislikesCount': self.dislikes_count
        }

class Reaction(db.Model):
    """Модель реакции на пост (лайк/дизлайк)"""
    __tablename__ = 'reactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.String(100), db.ForeignKey('posts.id'), nullable=False)
    reaction_type = db.Column(db.String(10), nullable=False)  # 'like' или 'dislike'
    
    # Один пользователь - одна реакция на пост
    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_reaction'),
    )
