"""
Astra - An Advanced AI Assistant
A Python-based AI framework for intelligent conversations and task automation.
"""

import os
from dotenv import load_dotenv
import openai
from flask import Flask, request, jsonify

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Astra AI Configuration
class AstraConfig:
    MODEL = "gpt-4"
    TEMPERATURE = 0.7
    MAX_TOKENS = 2000
    SYSTEM_PROMPT = """You are Astra, an advanced AI assistant designed to help users with 
    a wide range of tasks including problem-solving, coding, analysis, and creative thinking. 
    You are knowledgeable, helpful, and always strive to provide accurate and thoughtful responses."""

class Astra:
    def __init__(self):
        self.config = AstraConfig()
        self.conversation_history = []
    
    def chat(self, user_message: str) -> str:
        """
        Process a user message and return an AI response.
        
        Args:
            user_message (str): The user's input message
            
        Returns:
            str: Astra's response
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=self.config.MODEL,
                messages=[
                    {"role": "system", "content": self.config.SYSTEM_PROMPT}
                ] + self.conversation_history,
                temperature=self.config.TEMPERATURE,
                max_tokens=self.config.MAX_TOKENS
            )
            
            # Extract response
            assistant_message = response.choices[0].message.content
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
            
        except Exception as e:
            return f"Error: Unable to process your request. {str(e)}"
    
    def reset_conversation(self):
        """Reset conversation history."""
        self.conversation_history = []

# Initialize Astra
astra = Astra()

# Flask Routes
@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint for chat interactions."""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        response = astra.chat(user_message)
        return jsonify({'response': response, 'success': True}), 200
        
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/reset', methods=['POST'])
def reset():
    """Reset conversation history."""
    try:
        astra.reset_conversation()
        return jsonify({'message': 'Conversation reset successfully', 'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'name': 'Astra'}), 200

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, port=5000)
