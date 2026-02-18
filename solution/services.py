from models import db, User, Friendship, Post, Reaction
from datetime import datetime, timezone, timedelta
import jwt
import uuid

class AuthService:
    """Сервис авторизации и аутентификации"""
    
    @staticmethod
    def generate_token(user_id, secret_key):
        """
        Генерация JWT токена
        Время жизни: 24 часа
        """
        payload = {
            'user_id': user_id,
            'exp': datetime.now(timezone.utc) + timedelta(hours=24)
        }
        return jwt.encode(payload, secret_key, algorithm='HS256')
    
    @staticmethod
    def create_user(login, password_hash, email, country_code, is_public, phone=None, image=None):
        """Создание нового пользователя"""
        user = User(
            login=login,
            password_hash=password_hash,
            email=email,
            country_code=country_code,
            is_public=is_public,
            phone=phone,
            image=image
        )
        db.session.add(user)
        db.session.commit()
        return user

class FriendService:
    """Сервис управления друзьями"""
    
    @staticmethod
    def add_friend(user_id, friend_id):
        """
        Добавить друга (односторонняя связь)
        user_id добавляет friend_id в друзья
        """
        # Проверка на дубликат
        existing = Friendship.query.filter_by(
            user_id=user_id,
            friend_id=friend_id
        ).first()
        
        if existing:
            return existing
        
        friendship = Friendship(user_id=user_id, friend_id=friend_id)
        db.session.add(friendship)
        db.session.commit()
        return friendship
    
    @staticmethod
    def remove_friend(user_id, friend_id):
        """Удалить друга"""
        friendship = Friendship.query.filter_by(
            user_id=user_id,
            friend_id=friend_id
        ).first()
        
        if friendship:
            db.session.delete(friendship)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_friends(user_id, limit=5, offset=0):
        """
        Получить список друзей с пагинацией
        Сортировка: по дате добавления (desc)
        """
        friendships = Friendship.query.filter_by(user_id=user_id)\
            .order_by(Friendship.added_at.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()
        
        return [{
            'login': f.friend.login,
            'addedAt': f.added_at.isoformat()
        } for f in friendships]
    
    @staticmethod
    def is_friend(user_id, friend_id):
        """Проверка: является ли friend_id другом для user_id"""
        friendship = Friendship.query.filter_by(
            user_id=user_id,
            friend_id=friend_id
        ).first()
        return friendship is not None

class PostService:
    """Сервис управления публикациями"""
    
    @staticmethod
    def create_post(author_id, content, tags):
        """Создать новый пост"""
        post = Post(
            id=str(uuid.uuid4()),
            content=content,
            author_id=author_id,
            tags=tags or []
        )
        db.session.add(post)
        db.session.commit()
        return post
    
    @staticmethod
    def has_access_to_post(viewer, post):
        """
        Проверка доступа к посту:
        1. Свой пост
        2. Публичный профиль автора
        3. Автор добавил зрителя в друзья
        """
        author = post.author
        
        # Свой пост
        if viewer.id == author.id:
            return True
        
        # Публичный профиль автора
        if author.is_public:
            return True
        
        # Автор добавил зрителя в друзья
        return FriendService.is_friend(author.id, viewer.id)
    
    @staticmethod
    def has_access_to_profile(viewer, profile_owner):
        """
        Проверка доступа к профилю:
        1. Свой профиль
        2. Публичный профиль
        3. Владелец добавил зрителя в друзья
        """
        if viewer.id == profile_owner.id:
            return True
        
        if profile_owner.is_public:
            return True
        
        return FriendService.is_friend(profile_owner.id, viewer.id)
    
    @staticmethod
    def update_reaction(user_id, post_id, reaction_type):
        """
        Добавить или обновить реакцию (like/dislike)
        Последняя реакция пользователя сохраняется
        """
        reaction = Reaction.query.filter_by(
            user_id=user_id,
            post_id=post_id
        ).first()
        
        if reaction:
            reaction.reaction_type = reaction_type
        else:
            reaction = Reaction(
                user_id=user_id,
                post_id=post_id,
                reaction_type=reaction_type
            )
            db.session.add(reaction)
        
        db.session.commit()
        
        # Пересчитать счётчики
        PostService.recalculate_reactions(post_id)
    
    @staticmethod
    def recalculate_reactions(post_id):
        """Пересчитать количество лайков и дизлайков"""
        post = Post.query.get(post_id)
        if not post:
            return
        
        likes = Reaction.query.filter_by(
            post_id=post_id,
            reaction_type='like'
        ).count()
        
        dislikes = Reaction.query.filter_by(
            post_id=post_id,
            reaction_type='dislike'
        ).count()
        
        post.likes_count = likes
        post.dislikes_count = dislikes
        db.session.commit()
    
    @staticmethod
    def get_feed(user_id, limit=5, offset=0):
        """
        Получить ленту постов пользователя
        Только свои посты
        """
        posts = Post.query.filter_by(author_id=user_id)\
            .order_by(Post.created_at.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()
        
        return [post.to_dict() for post in posts]
    
    @staticmethod
    def get_user_feed(viewer, target_login, limit=5, offset=0):
        """
        Получить ленту другого пользователя
        С проверкой доступа
        """
        target_user = User.query.filter_by(login=target_login).first()
        if not target_user:
            return None
        
        # Проверка доступа к профилю
        if not PostService.has_access_to_profile(viewer, target_user):
            return None
        
        posts = Post.query.filter_by(author_id=target_user.id)\
            .order_by(Post.created_at.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()
        
        return [post.to_dict() for post in posts]
