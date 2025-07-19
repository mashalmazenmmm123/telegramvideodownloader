"""
Database models for the Telegram Video Downloader Bot
User management, rate limiting, and premium features
"""

import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=True, index=True)  # Telegram user ID
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    user_type = Column(String, default='normal')  # normal, premium, admin
    is_banned = Column(Boolean, default=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # Rate limiting fields
    daily_downloads = Column(Integer, default=0)
    last_download_date = Column(DateTime, default=datetime.utcnow)
    last_download_time = Column(DateTime, nullable=True)
    
    # Premium fields
    premium_until = Column(DateTime, nullable=True)
    added_by_admin = Column(String, nullable=True)  # Admin user_id who granted premium
    
    # Relationships
    downloads = relationship("Download", back_populates="user")
    
    def is_premium(self):
        """Check if user has active premium subscription"""
        if self.user_type == 'admin':
            return True
        if self.premium_until and self.premium_until > datetime.utcnow():
            return True
        return False
    
    def is_admin(self):
        """Check if user is admin"""
        return self.user_type == 'admin'
    
    def can_download(self):
        """Check if user can download based on rate limits"""
        if self.is_banned:
            return False, "You are banned from using this bot."
        
        if self.is_admin():
            return True, "Admin access"
        
        # Reset daily count if it's a new day
        today = datetime.utcnow().date()
        if self.last_download_date.date() != today:
            self.daily_downloads = 0
            self.last_download_date = datetime.utcnow()
        
        if self.is_premium():
            # Premium users get unlimited downloads
            return True, "Premium access"
        
        # Normal user rate limiting
        if self.daily_downloads >= 10:
            return False, "Daily limit reached (10 downloads). Upgrade to premium for unlimited downloads."
        
        # Check 3-minute cooldown after first download
        if self.last_download_time and self.daily_downloads > 0:
            time_since_last = datetime.utcnow() - self.last_download_time
            if time_since_last < timedelta(minutes=3):
                remaining = timedelta(minutes=3) - time_since_last
                minutes, seconds = divmod(remaining.total_seconds(), 60)
                return False, f"Please wait {int(minutes)}m {int(seconds)}s before next download."
        
        return True, "Download allowed"
    
    def record_download(self):
        """Record a successful download"""
        self.daily_downloads += 1
        self.last_download_time = datetime.utcnow()
        self.last_active = datetime.utcnow()


class Download(Base):
    __tablename__ = 'downloads'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.user_id'))
    url = Column(Text)
    title = Column(String, nullable=True)
    file_size = Column(Float, nullable=True)  # in MB
    download_type = Column(String)  # 'platform' or 'direct'
    status = Column(String)  # 'success', 'failed', 'too_large'
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="downloads")


class AdminLog(Base):
    __tablename__ = 'admin_logs'
    
    id = Column(Integer, primary_key=True)
    admin_user_id = Column(String)
    action = Column(String)  # 'add_admin', 'remove_admin', 'grant_premium', 'ban_user', etc.
    target_user_id = Column(String, nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass

def init_db():
    """Initialize database and create tables"""
    create_tables()
    print("Database initialized successfully")