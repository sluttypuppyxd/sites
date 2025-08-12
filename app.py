from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import logging
from datetime import datetime
from config import config

# Setup logging
def setup_logging():
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
        handlers=[
            logging.FileHandler('logs/femboyworld.log'),
            logging.StreamHandler()
        ]
    )

# Create Flask app
def create_app(config_name=None):
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app.config.from_object(config[config_name])
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app

app = create_app()

# Setup logging
setup_logging()

# Security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; font-src 'self' https://cdnjs.cloudflare.com;"
    return response

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error(f'Server Error: {error}')
    return render_template('errors/500.html'), 500

@app.errorhandler(413)
def too_large(error):
    flash('File too large. Maximum size is 16MB.')
    return redirect(request.url)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    avatar = db.Column(db.String(200))
    bio = db.Column(db.Text)
    tos_accepted = db.Column(db.Boolean, default=False)  # Terms of Service acceptance
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Following system - simplified relationship
    following = db.relationship(
        'User', secondary='followers',
        primaryjoin='User.id == followers.c.follower_id',
        secondaryjoin='User.id == followers.c.followed_id',
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    media_type = db.Column(db.String(10), nullable=False)  # 'image' or 'video'
    media_path = db.Column(db.String(200), nullable=False)
    tags = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    view_count = db.Column(db.Integer, default=0)  # Track post views
    
    # Relationships
    author = db.relationship('User', backref='user_posts')
    likes = db.relationship('Like', backref='post', lazy=True)
    comments = db.relationship('Comment', backref='post', lazy=True)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='user_likes')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)  # For nested comments
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]))
    
    # Relationships
    author = db.relationship('User', backref='user_comments')

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'like', 'comment', 'follow', 'reply'
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    related_id = db.Column(db.Integer)  # ID of related post, comment, or user
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic'))

class SupportTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 'bug', 'feature', 'account', 'other'
    status = db.Column(db.String(20), default='open')  # 'open', 'in_progress', 'resolved', 'closed'
    priority = db.Column(db.String(20), default='medium')  # 'low', 'medium', 'high', 'urgent'
    admin_response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('support_tickets', lazy='dynamic'))

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reported_type = db.Column(db.String(20), nullable=False)  # 'post', 'user', 'comment'
    reported_id = db.Column(db.Integer, nullable=False)  # ID of reported post, user, or comment
    reason = db.Column(db.String(100), nullable=False)  # 'inappropriate', 'spam', 'harassment', 'copyright', 'other'
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'reviewed', 'resolved', 'dismissed'
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # Admin who reviewed it
    
    # Relationships
    reporter = db.relationship('User', foreign_keys=[reporter_id], backref='reports_filed')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by], backref='reports_reviewed')

# Followers association table
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

# Hashtag model
class Hashtag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    post_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    posts = db.relationship('Post', secondary='post_hashtags', backref='hashtags')

# Post-Hashtag association table
post_hashtags = db.Table('post_hashtags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('hashtag_id', db.Integer, db.ForeignKey('hashtag.id'), primary_key=True)
)

# Mention model
class Mention(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    mentioned_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    post = db.relationship('Post', backref='mentions')
    comment = db.relationship('Comment', backref='mentions')
    mentioned_user = db.relationship('User', backref='mentioned_in')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper functions
def create_notification(user_id, type, title, message, related_id=None):
    """Create a notification for a user"""
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        related_id=related_id
    )
    db.session.add(notification)
    db.session.commit()

def create_like_notification(post, user):
    """Create notification when someone likes a post"""
    if post.user_id != user.id:  # Don't notify yourself
        create_notification(
            post.user_id,
            'like',
            f'{user.username} liked your post',
            f'{user.username} liked your post "{post.title}"',
            post.id
        )

def create_comment_notification(post, user, comment_content):
    """Create notification when someone comments on a post"""
    if post.user_id != user.id:  # Don't notify yourself
        create_notification(
            post.user_id,
            'comment',
            f'{user.username} commented on your post',
            f'{user.username} commented: "{comment_content[:50]}{"..." if len(comment_content) > 50 else ""}"',
            post.id
        )

def create_follow_notification(followed_user, follower):
    """Create notification when someone follows a user"""
    create_notification(
        followed_user.id,
        'follow',
        f'{follower.username} started following you',
        f'{follower.username} started following you',
        follower.id
    )

def process_hashtags(text):
    """Extract hashtags from text and return list of hashtag names"""
    import re
    hashtags = re.findall(r'#(\w+)', text)
    return [tag.lower() for tag in hashtags]

def process_mentions(text):
    """Extract mentions from text and return list of usernames"""
    import re
    mentions = re.findall(r'@(\w+)', text)
    return mentions

def create_hashtag_if_not_exists(hashtag_name):
    """Create a hashtag if it doesn't exist, or return existing one"""
    hashtag = Hashtag.query.filter_by(name=hashtag_name.lower()).first()
    if not hashtag:
        hashtag = Hashtag(name=hashtag_name.lower())
        db.session.add(hashtag)
        db.session.commit()
    return hashtag

def link_hashtags_to_post(post, hashtag_names):
    """Link hashtags to a post"""
    for hashtag_name in hashtag_names:
        hashtag = create_hashtag_if_not_exists(hashtag_name)
        if hashtag not in post.hashtags:
            post.hashtags.append(hashtag)
            hashtag.post_count += 1
    db.session.commit()

def create_mentions_for_post(post, mention_usernames, comment_id=None):
    """Create mention records for a post or comment"""
    for username in mention_usernames:
        user = User.query.filter_by(username=username).first()
        if user and user.id != post.user_id:  # Don't mention the post author
            mention = Mention(
                post_id=post.id,
                comment_id=comment_id,
                mentioned_user_id=user.id
            )
            db.session.add(mention)
            
            # Create notification for mentioned user
            create_notification(
                user.id,
                'mention',
                f'You were mentioned in a post by {post.author.username}',
                f'{post.author.username} mentioned you in their post "{post.title}"',
                post.id
            )
    db.session.commit()

# Helper function to check if user has accepted ToS
def tos_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.tos_accepted:
            return redirect(url_for('tos'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Routes
@app.route('/')
def home():
    section = request.args.get('section', 'for_you')
    
    if section == 'following' and current_user.is_authenticated:
        # Show posts from users the current user follows
        following_ids = [user.id for user in current_user.following]
        if following_ids:
            posts = Post.query.filter(Post.user_id.in_(following_ids)).order_by(Post.created_at.desc()).limit(20).all()
        else:
            posts = []
            flash('Follow some users to see their posts here!')
    elif section == 'trending':
        # Show trending posts (most liked in last 7 days)
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        posts = db.session.query(Post).join(Like).filter(
            Post.created_at >= week_ago
        ).group_by(Post.id).order_by(
            db.func.count(Like.id).desc()
        ).limit(20).all()
    else:
        # Default: Show recent posts from all users (For You page)
        posts = Post.query.order_by(Post.created_at.desc()).limit(20).all()
    
    # Get liked posts for current user if authenticated
    liked_posts = set()
    if current_user.is_authenticated:
        liked_posts = {like.post_id for like in current_user.user_likes}
    
    return render_template('home.html', posts=posts, liked_posts=liked_posts, section=section)

@app.route('/tos', methods=['GET', 'POST'])
@login_required
def tos():
    if current_user.tos_accepted:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        if request.form.get('accept_tos'):
            current_user.tos_accepted = True
            db.session.commit()
            flash('Thank you for accepting the Terms of Service!')
            return redirect(url_for('home'))
        else:
            flash('You must accept the Terms of Service to continue.')
    
    return render_template('tos.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        user = User(
            username=username, 
            email=email, 
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            # Redirect to ToS if not accepted, otherwise to home
            if not user.tos_accepted:
                return redirect(url_for('tos'))
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/upload', methods=['GET', 'POST'])
@tos_required
def upload():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        tags = request.form['tags']
        
        if 'media' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['media']
        
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            
            # Determine media type
            file_ext = filename.lower().split('.')[-1]
            
            if file_ext in ['jpg', 'jpeg', 'png', 'gif']:
                media_type = 'image'
            elif file_ext in ['mp4', 'avi', 'mov', 'wmv']:
                media_type = 'video'
            else:
                flash('Unsupported file type')
                return redirect(request.url)
            
            try:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            except Exception as e:
                flash('Error saving file. Please try again.')
                return redirect(request.url)
            
            post = Post(
                title=title,
                description=description,
                media_type=media_type,
                media_path=filename,
                tags=tags,
                user_id=current_user.id
            )
            db.session.add(post)
            db.session.commit()
            
            # Process hashtags and mentions
            if description:
                hashtags = process_hashtags(description)
                mentions = process_mentions(description)
                
                if hashtags:
                    link_hashtags_to_post(post, hashtags)
                
                if mentions:
                    create_mentions_for_post(post, mentions)
            
            flash('Post uploaded successfully!')
            return redirect(url_for('home'))
    
    return render_template('upload.html')

@app.route('/post/<int:post_id>')
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # Increment view count
    post.view_count += 1
    db.session.commit()
    
    # Get liked posts for current user if authenticated
    liked_posts = set()
    if current_user.is_authenticated:
        liked_posts = {like.post_id for like in current_user.user_likes}
    
    return render_template('view_post.html', post=post, liked_posts=liked_posts)

@app.route('/comment/<int:post_id>', methods=['POST'])
@tos_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form.get('content', '').strip()
    
    if not content:
        flash('Comment cannot be empty')
        return redirect(url_for('view_post', post_id=post_id))
    
    comment = Comment(
        content=content,
        user_id=current_user.id,
        post_id=post_id
    )
    
    db.session.add(comment)
    db.session.commit()
    
    # Process mentions in comment
    mentions = process_mentions(content)
    if mentions:
        create_mentions_for_post(post, mentions, comment.id)
    
    # Create notification for the post author
    create_comment_notification(post, current_user, content)
    
    flash('Comment added successfully!')
    return redirect(url_for('view_post', post_id=post_id))

@app.route('/comment/<int:comment_id>/reply', methods=['POST'])
@tos_required
def reply_to_comment(comment_id):
    parent_comment = Comment.query.get_or_404(comment_id)
    content = request.form.get('content', '').strip()
    
    if not content:
        flash('Reply cannot be empty')
        return redirect(url_for('view_post', post_id=parent_comment.post_id))
    
    reply = Comment(
        content=content,
        user_id=current_user.id,
        post_id=parent_comment.post_id,
        parent_id=comment_id
    )
    
    db.session.add(reply)
    db.session.commit()
    
    flash('Reply added successfully!')
    return redirect(url_for('view_post', post_id=parent_comment.post_id))

@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
@tos_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    # Only allow comment author or post author to delete
    if comment.user_id != current_user.id and comment.post.author.id != current_user.id:
        flash('You cannot delete this comment')
        return redirect(url_for('view_post', post_id=comment.post_id))
    
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    
    flash('Comment deleted successfully!')
    return redirect(url_for('view_post', post_id=post_id))

@app.route('/follow/<username>', methods=['POST'])
@tos_required
def follow_user(username):
    user_to_follow = User.query.filter_by(username=username).first_or_404()
    
    if user_to_follow.id == current_user.id:
        flash('You cannot follow yourself')
        return redirect(url_for('profile', username=username))
    
    if current_user.following.filter_by(id=user_to_follow.id).first():
        # Unfollow
        current_user.following.remove(user_to_follow)
        db.session.commit()
        return jsonify({'following': False, 'count': user_to_follow.followers.count()})
    else:
        # Follow
        current_user.following.append(user_to_follow)
        db.session.commit()
        
        # Create notification for the followed user
        create_follow_notification(user_to_follow, current_user)
        
        return jsonify({'following': True, 'count': user_to_follow.followers.count()})

@app.route('/following')
@tos_required
def following_feed():
    # Get posts from users the current user follows
    following_ids = [user.id for user in current_user.following]
    posts = Post.query.filter(Post.user_id.in_(following_ids)).order_by(Post.created_at.desc()).limit(20).all()
    
    # Get liked posts for current user
    liked_posts = {like.post_id for like in current_user.user_likes}
    
    return render_template('home.html', posts=posts, liked_posts=liked_posts, section='following')

@app.route('/trending')
def trending():
    # Get posts with most likes in the last 7 days
    from datetime import timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    posts = db.session.query(Post).join(Like).filter(
        Post.created_at >= week_ago
    ).group_by(Post.id).order_by(
        db.func.count(Like.id).desc()
    ).limit(20).all()
    
    # Get liked posts for current user if authenticated
    liked_posts = set()
    if current_user.is_authenticated:
        liked_posts = {like.post_id for like in current_user.user_likes}
    
    return render_template('home.html', posts=posts, liked_posts=liked_posts, section='trending')

@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
    
    # Get liked posts for current user if authenticated
    liked_posts = set()
    is_following = False
    if current_user.is_authenticated:
        liked_posts = {like.post_id for like in current_user.user_likes}
        is_following = current_user.following.filter_by(id=user.id).first() is not None
    
    return render_template('profile.html', user=user, posts=posts, liked_posts=liked_posts, is_following=is_following)

@app.route('/like/<int:post_id>', methods=['POST'])
@tos_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    existing_like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        return jsonify({'liked': False, 'count': len(post.likes)})
    else:
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
        
        # Create notification for the post author
        create_like_notification(post, current_user)
        
        return jsonify({'liked': True, 'count': len(post.likes)})

@app.route('/hashtag/<hashtag_name>')
def hashtag_posts(hashtag_name):
    """Show all posts with a specific hashtag"""
    hashtag = Hashtag.query.filter_by(name=hashtag_name.lower()).first_or_404()
    posts = hashtag.posts.order_by(Post.created_at.desc()).all()
    
    # Get liked posts for current user if authenticated
    liked_posts = set()
    if current_user.is_authenticated:
        liked_posts = {like.post_id for like in current_user.user_likes}
    
    return render_template('hashtag.html', hashtag=hashtag, posts=posts, liked_posts=liked_posts)

@app.route('/trending-hashtags')
def trending_hashtags():
    """Show trending hashtags based on post count"""
    hashtags = Hashtag.query.order_by(Hashtag.post_count.desc()).limit(20).all()
    return render_template('trending_hashtags.html', hashtags=hashtags)

@app.route('/search')
def search():
    """Enhanced search with hashtag and mention support"""
    query = request.args.get('q', '')
    if not query:
        return render_template('search.html', posts=[], hashtags=[], users=[])
    
    # Search posts by title, description, or hashtags
    posts = Post.query.filter(
        db.or_(
            Post.title.contains(query),
            Post.description.contains(query)
        )
    ).order_by(Post.created_at.desc()).limit(20).all()
    
    # Search hashtags
    hashtags = Hashtag.query.filter(Hashtag.name.contains(query.lower())).limit(10).all()
    
    # Search users
    users = User.query.filter(User.username.contains(query)).limit(10).all()
    
    # Get liked posts for current user if authenticated
    liked_posts = set()
    if current_user.is_authenticated:
        liked_posts = {like.post_id for like in current_user.user_likes}
    
    return render_template('search.html', posts=posts, hashtags=hashtags, users=users, 
                         liked_posts=liked_posts, query=query)

@app.route('/notifications')
@tos_required
def notifications():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    notifications = current_user.notifications.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('notifications.html', notifications=notifications)

@app.route('/notifications/mark-read/<int:notification_id>', methods=['POST'])
@tos_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/notifications/mark-all-read', methods=['POST'])
@tos_required
def mark_all_notifications_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    
    flash('All notifications marked as read!')
    return redirect(url_for('notifications'))

# Support and Reporting Routes
@app.route('/support', methods=['GET', 'POST'])
@tos_required
def support():
    if request.method == 'POST':
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        category = request.form.get('category', 'other')
        priority = request.form.get('priority', 'medium')
        
        if not subject or not message:
            flash('Please fill in all required fields')
            return redirect(url_for('support'))
        
        ticket = SupportTicket(
            user_id=current_user.id,
            subject=subject,
            message=message,
            category=category,
            priority=priority
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        flash('Support ticket submitted successfully! We will respond within 24-48 hours.')
        return redirect(url_for('support'))
    
    # Get user's existing tickets
    tickets = current_user.support_tickets.order_by(SupportTicket.created_at.desc()).all()
    
    return render_template('support.html', tickets=tickets)

@app.route('/support/ticket/<int:ticket_id>')
@tos_required
def view_ticket(ticket_id):
    ticket = SupportTicket.query.get_or_404(ticket_id)
    
    # Ensure user can only view their own tickets
    if ticket.user_id != current_user.id:
        flash('You can only view your own support tickets')
        return redirect(url_for('support'))
    
    return render_template('view_ticket.html', ticket=ticket)

@app.route('/report', methods=['GET', 'POST'])
@tos_required
def report_content():
    if request.method == 'POST':
        reported_type = request.form.get('reported_type', '').strip()
        reported_id = request.form.get('reported_id', '').strip()
        reason = request.form.get('reason', '').strip()
        description = request.form.get('description', '').strip()
        
        if not reported_type or not reported_id or not reason:
            flash('Please fill in all required fields')
            return redirect(url_for('report_content'))
        
        try:
            reported_id = int(reported_id)
        except ValueError:
            flash('Invalid reported content ID')
            return redirect(url_for('report_content'))
        
        # Check if content exists
        if reported_type == 'post':
            content = Post.query.get(reported_id)
        elif reported_type == 'user':
            content = User.query.get(reported_id)
        elif reported_type == 'comment':
            content = Comment.query.get(reported_id)
        else:
            flash('Invalid content type')
            return redirect(url_for('report_content'))
        
        if not content:
            flash('Reported content not found')
            return redirect(url_for('report_content'))
        
        # Check if user already reported this content
        existing_report = Report.query.filter_by(
            reporter_id=current_user.id,
            reported_type=reported_type,
            reported_id=reported_id
        ).first()
        
        if existing_report:
            flash('You have already reported this content')
            return redirect(url_for('report_content'))
        
        report = Report(
            reporter_id=current_user.id,
            reported_type=reported_type,
            reported_id=reported_id,
            reason=reason,
            description=description
        )
        
        db.session.add(report)
        db.session.commit()
        
        flash('Report submitted successfully. Our moderation team will review it within 24 hours.')
        return redirect(url_for('home'))
    
    # Get report parameters from query string
    reported_type = request.args.get('type', '')
    reported_id = request.args.get('id', '')
    
    return render_template('report.html', reported_type=reported_type, reported_id=reported_id)

@app.route('/report/post/<int:post_id>')
@tos_required
def report_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('report.html', reported_type='post', reported_id=post_id, post=post)

@app.route('/report/user/<username>')
@tos_required
def report_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('report.html', reported_type='user', reported_id=user.id, user=user)

@app.route('/report/comment/<int:comment_id>')
@tos_required
def report_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    return render_template('report.html', reported_type='comment', reported_id=comment_id, comment=comment)

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    # Only run in development mode
    if app.config.get('DEBUG', False):
        with app.app_context():
            # Create tables if they don't exist
            db.create_all()
            app.logger.info("Development server started")
        app.run(debug=True)
    else:
        app.logger.info("Production mode - use gunicorn to start server")
