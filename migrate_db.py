#!/usr/bin/env python3
"""
Database Migration Script for FemboyWorld
This script helps migrate existing databases to include new features.
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Migrate the existing database to include new features"""
    
    db_path = 'instance/femboyworld.db'
    
    if not os.path.exists(db_path):
        print("Database not found. Creating new database...")
        return
    
    print("Starting database migration...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Checking and updating database schema...")
        
        # Always check and add view_count column to posts table if it doesn't exist
        try:
            cursor.execute("ALTER TABLE post ADD COLUMN view_count INTEGER DEFAULT 0")
            print("✓ Added view_count column to posts table")
        except sqlite3.OperationalError:
            print("✓ view_count column already exists")
        
        # Check if comment table exists, if not create it
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='comment'")
        if not cursor.fetchone():
            print("Creating new tables...")
            
            # Create comments table
            cursor.execute("""
                CREATE TABLE comment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    post_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    parent_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES user (id),
                    FOREIGN KEY (post_id) REFERENCES post (id),
                    FOREIGN KEY (parent_id) REFERENCES comment (id)
                )
            """)
            print("✓ Created comments table")
        else:
            print("✓ Comments table already exists")
        
        # Create notifications table
        cursor.execute("""
            CREATE TABLE notification (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type VARCHAR(50) NOT NULL,
                title VARCHAR(200) NOT NULL,
                message TEXT NOT NULL,
                related_id INTEGER,
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        """)
        print("✓ Created notifications table")
        
        # Create followers table
        cursor.execute("""
            CREATE TABLE followers (
                follower_id INTEGER NOT NULL,
                followed_id INTEGER NOT NULL,
                PRIMARY KEY (follower_id, followed_id),
                FOREIGN KEY (follower_id) REFERENCES user (id),
                FOREIGN KEY (followed_id) REFERENCES user (id)
            )
        """)
        print("✓ Created followers table")
        
        # Create support tickets table
        cursor.execute("""
            CREATE TABLE support_ticket (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subject VARCHAR(200) NOT NULL,
                message TEXT NOT NULL,
                category VARCHAR(50) NOT NULL,
                status VARCHAR(20) DEFAULT 'open',
                priority VARCHAR(20) DEFAULT 'medium',
                admin_response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        """)
        print("✓ Created support tickets table")
        
        # Create reports table
        cursor.execute("""
            CREATE TABLE report (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reporter_id INTEGER NOT NULL,
                reported_type VARCHAR(20) NOT NULL,
                reported_id INTEGER NOT NULL,
                reason VARCHAR(100) NOT NULL,
                description TEXT,
                status VARCHAR(20) DEFAULT 'pending',
                admin_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TIMESTAMP,
                reviewed_by INTEGER,
                FOREIGN KEY (reporter_id) REFERENCES user (id),
                FOREIGN KEY (reviewed_by) REFERENCES user (id)
            )
        """)
        print("✓ Created reports table")
        
        # Create hashtags table
        cursor.execute("""
            CREATE TABLE hashtag (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) UNIQUE NOT NULL,
                post_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Created hashtags table")
        
        # Create post-hashtags association table
        cursor.execute("""
            CREATE TABLE post_hashtags (
                post_id INTEGER NOT NULL,
                hashtag_id INTEGER NOT NULL,
                PRIMARY KEY (post_id, hashtag_id),
                FOREIGN KEY (post_id) REFERENCES post (id),
                FOREIGN KEY (hashtag_id) REFERENCES hashtag (id)
            )
        """)
        print("✓ Created post-hashtags association table")
        
        # Create mentions table
        cursor.execute("""
            CREATE TABLE mention (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                comment_id INTEGER,
                mentioned_user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES post (id),
                FOREIGN KEY (comment_id) REFERENCES comment (id),
                FOREIGN KEY (mentioned_user_id) REFERENCES user (id)
            )
        """)
        print("✓ Created mentions table")
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_comment_post_id ON comment(post_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_comment_user_id ON comment(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notification_user_id ON notification(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notification_is_read ON notification(is_read)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_followers_follower ON followers(follower_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_followers_followed ON followers(followed_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_support_ticket_user_id ON support_ticket(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_support_ticket_status ON support_ticket(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_report_reporter_id ON report(reporter_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_report_status ON report(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_report_type_id ON report(reported_type, reported_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_hashtag_name ON hashtag(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_hashtag_post_count ON hashtag(post_count)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_post_hashtags_post ON post_hashtags(post_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_post_hashtags_hashtag ON post_hashtags(hashtag_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mention_post_id ON mention(post_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mention_user_id ON mention(mentioned_user_id)")
        print("✓ Created performance indexes")
        
        # Commit changes
        conn.commit()
        print("\n🎉 Database migration completed successfully!")
        print("New features available:")
        print("  • Comments and replies system")
        print("  • User following system")
        print("  • Notifications for likes, comments, and follows")
        print("  • Post view counting")
        print("  • Enhanced search with filters and pagination")
        print("  • Support ticket system")
        print("  • Content reporting system")
        print("  • Hashtag system with trending hashtags")
        print("  • User mentions with notifications")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
