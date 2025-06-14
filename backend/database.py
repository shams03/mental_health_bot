import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        # self.conn = psycopg2.connect(
        #     dbname=os.getenv('DB_NAME'),
        #     user=os.getenv('DB_USER'),
        #     password=os.getenv('DB_PASSWORD'),
        #     host=os.getenv('DB_HOST'),
        #     port=os.getenv('DB_PORT')
        # )
        db_url = os.getenv('DATABASE_URL')  # Ensure you have DATABASE_URL in your .env file

        if not db_url:
            raise ValueError("DATABASE_URL environment variable is not set")

        # Connect to the database using the connection string
        self.conn = psycopg2.connect(db_url)
        self.create_tables()

    def create_tables(self):
        with self.conn.cursor() as cur:
            # Create users table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    is_premium BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create conversations table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    user_message TEXT NOT NULL,
                    bot_response TEXT NOT NULL,
                    user_mood VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.conn.commit()

    def get_user(self, user_id):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return cur.fetchone()

    def create_user(self, username, email, password_hash):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id",
                (username, email, password_hash)
            )
            user_id = cur.fetchone()[0]
            self.conn.commit()
            return user_id

    def create_conversation(self, user_id, user_message, bot_response, user_mood):
        with self.conn.cursor() as cur:
            cur.execute(
                """INSERT INTO conversations 
                   (user_id, user_message, bot_response, user_mood) 
                   VALUES (%s, %s, %s, %s) 
                   RETURNING id""",
                (user_id, user_message, bot_response, user_mood)
            )
            conversation_id = cur.fetchone()[0]
            self.conn.commit()
            return conversation_id

    def get_conversations(self, user_id):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """SELECT * FROM conversations 
                   WHERE user_id = %s 
                   ORDER BY created_at DESC""",
                (user_id,)
            )
            return cur.fetchall()

    def get_message_count(self, user_id, hours):
        with self.conn.cursor() as cur:
            cur.execute(
                """SELECT COUNT(*) FROM conversations 
                   WHERE user_id = %s 
                   AND created_at > %s""",
                (user_id, datetime.now() - timedelta(hours=hours))
            )
            return cur.fetchone()[0]

    def get_daily_stats(self, user_id, days):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """SELECT 
                       DATE(created_at) as date,
                       COUNT(*) as message_count,
                       STRING_AGG(DISTINCT user_mood, ', ') as moods
                   FROM conversations 
                   WHERE user_id = %s 
                   AND created_at > %s
                   GROUP BY DATE(created_at)
                   ORDER BY date DESC""",
                (user_id, datetime.now() - timedelta(days=days))
            )
            return cur.fetchall()

    def close(self):
        self.conn.close()

# Create a singleton instance
db = Database() 