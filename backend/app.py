from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from ai_chat import AIChat
from database import db
import os
from dotenv import load_dotenv
import asyncio
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
CORS(app)

# Constants
FREE_TIER_MESSAGE_LIMIT = 20
MESSAGE_LIMIT_WINDOW = 4  # hours

def async_route(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapped

def check_message_limit(user_id):
    user = db.get_user(user_id)
    if not user:
        return False
    
    if user['is_premium']:
        return True
    
    message_count = db.get_message_count(user_id, MESSAGE_LIMIT_WINDOW)
    return message_count < FREE_TIER_MESSAGE_LIMIT

@app.route('/api/messages', methods=['POST'])
@async_route
async def create_message():
    try:
        data = request.json
        user_id = data.get('user_id')
        content = data.get('content')
        model = data.get('model', 'openai')  # Default to OpenAI if not specified
        print(f"Received message from user {user_id}: {content}")
        
        if not check_message_limit(user_id):
            return jsonify({
                'error': 'Message limit reached. Please upgrade to premium for unlimited messages.'
            }), 403
    
    # Get AI response and mood analysis based on selected model
  
        if model.lower() == 'gemini':
            response = await AIChat.get_gemini_response(content)
        else:
            response = await AIChat.get_openai_response(content)
        
        bot_response = response['response']
        user_mood = response['mood']
    except Exception as e:
        print(f"Error getting AI response: {str(e)}")
        bot_response = "I apologize, but I'm having trouble processing your message right now. Please try again later."
        user_mood = "unknown"
    
    # Create conversation entry
    try:
        conversation_id = db.create_conversation(
            user_id=user_id,
            user_message=content,
            bot_response=bot_response,
            user_mood=user_mood
        )
    
        return jsonify({
        'conversation': {
            'id': conversation_id,
            'user_message': content,
            'bot_response': bot_response,
            'user_mood': user_mood,
                'created_at': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/conversations/<int:user_id>', methods=['GET'])
def get_conversations(user_id):
    try:
        conversations = db.get_conversations(user_id)
        return jsonify([{
            'id': conv['id'],
            'user_message': conv['user_message'],
            'bot_response': conv['bot_response'],
            'user_mood': conv['user_mood'],
            'created_at': conv['created_at']
        } for conv in conversations])
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500 

@app.route('/api/stats/<int:user_id>', methods=['GET'])
def get_stats(user_id):
    try:
        days = request.args.get('days', default=30, type=int)
        stats = db.get_daily_stats(user_id, days)
        return jsonify([{
            'date': stat['date'],
            'message_count': stat['message_count'],
            'moods': stat['moods'].split(', ')
        } for stat in stats])
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/create_user', methods=['POST'])
def create_user():
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        password_hash = generate_password_hash(password)
        user_id =  db.create_user(username, email, password_hash)
        return jsonify({
            'message': 'User created successfully',
            'user_id': user_id
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 