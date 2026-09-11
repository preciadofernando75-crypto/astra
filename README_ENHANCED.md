# Astra - Advanced AI Assistant (Enhanced Version 2.0)

**Astra** is a comprehensive AI assistant framework built with Flask, featuring authentication, file processing, multiple AI personas, database storage, logging, and analytics.

## 🚀 Features

### Core AI Capabilities
- ✅ Multi-model support (GPT-4, GPT-3.5, and extensible)
- ✅ Specialized AI personas (General, Code, Creative, Science, Business)
- ✅ Conversation history and memory management
- ✅ Context-aware responses

### Authentication & Security
- ✅ User registration and login with JWT tokens
- ✅ API key management
- ✅ Role-based access control (Admin, User, Guest)
- ✅ Password hashing with Werkzeug
- ✅ Token expiration and refresh

### File Processing
- ✅ PDF extraction and processing
- ✅ CSV file handling
- ✅ Code file analysis (Python, JavaScript, Java, C++, Go, Rust, etc.)
- ✅ Plain text file processing
- ✅ File embeddings for RAG (Retrieval-Augmented Generation)

### Database Features
- ✅ PostgreSQL/SQLite support
- ✅ User management
- ✅ Conversation history storage
- ✅ Message logging
- ✅ File management
- ✅ API call logging

### Analytics & Monitoring
- ✅ API request logging
- ✅ Usage statistics and analytics
- ✅ Performance monitoring
- ✅ Error tracking
- ✅ Token usage tracking
- ✅ Response time monitoring

### Deployment
- ✅ Docker support
- ✅ Docker Compose setup
- ✅ Gunicorn production server
- ✅ Environment-based configuration

### Testing
- ✅ Unit tests for authentication
- ✅ Integration tests
- ✅ Test database setup

## 📋 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Conversations
- `GET /api/conversations` - Get all conversations
- `POST /api/conversations` - Create new conversation
- `POST /api/conversations/<id>/chat` - Send message in conversation

### Files
- `POST /api/files/upload` - Upload and process file

### Personas
- `GET /api/personas` - List available personas

### Analytics
- `GET /api/analytics/usage` - Get usage statistics

### Admin
- `GET /api/admin/users` - Get all users (admin only)

### Health
- `GET /health` - Health check

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, SQLite is default)
- OpenAI API key

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/preciadofernando75-crypto/astra.git
   cd astra
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements-enhanced.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example.enhanced .env
   # Edit .env with your settings, especially OPENAI_API_KEY
   ```

5. **Initialize database:**
   ```bash
   python
   >>> from astra_enhanced import app
   >>> from database import db, init_db
   >>> init_db(app)
   >>> exit()
   ```

6. **Run the application:**
   ```bash
   python astra_enhanced.py
   ```

### Docker Setup

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   ```
   http://localhost:5000
   ```

## 📚 Usage Examples

### 1. Register User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure_password"
  }'
```

### 3. Create Conversation
```bash
curl -X POST http://localhost:5000/api/conversations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "Python Help",
    "model": "gpt-4",
    "persona": "code"
  }'
```

### 4. Send Message
```bash
curl -X POST http://localhost:5000/api/conversations/1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "How do I read a JSON file in Python?"
  }'
```

### 5. Upload File
```bash
curl -X POST http://localhost:5000/api/files/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@myfile.pdf"
```

### 6. Get Usage Stats
```bash
curl -X GET "http://localhost:5000/api/analytics/usage?days=30" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🎭 AI Personas

1. **General** - Versatile assistant for any topic
2. **Code** - Expert in programming and software development
3. **Creative** - Specialized in creative writing and storytelling
4. **Science** - Expert in scientific and technical topics
5. **Business** - Specialized in business strategy and analysis

## 📊 Database Schema

### Users Table
- user_id, username, email, password_hash, api_key, role, created_at, updated_at

### Conversations Table
- id, user_id, title, model, persona, created_at, updated_at

### Messages Table
- id, conversation_id, role, content, tokens_used, created_at

### UploadedFiles Table
- id, user_id, filename, file_path, file_type, file_size, embedding, created_at

### APILogs Table
- id, user_id, endpoint, method, status_code, response_time, tokens_used, error_message, created_at

## 🔒 Security Considerations

- Always use HTTPS in production
- Store SECRET_KEY securely (use environment variables)
- Rotate API keys regularly
- Implement rate limiting
- Validate all user inputs
- Keep dependencies updated
- Use strong passwords

## 📈 Performance Monitoring

View metrics in real-time:
- API call logs: `tail -f astra.log`
- Database queries
- Token usage per user
- Average response times
- Error rates and types

## 🧪 Testing

Run tests:
```bash
python -m pytest tests/
```

Run specific test:
```bash
python -m pytest tests/test_auth.py
```

## 🚀 Future Enhancements

- [ ] Frontend web UI (React/Vue)
- [ ] CLI tool
- [ ] Voice/Audio support
- [ ] Advanced RAG with vector databases
- [ ] Fine-tuning capabilities
- [ ] Multi-language support
- [ ] Webhook integrations
- [ ] Batch processing
- [ ] Custom model fine-tuning
- [ ] Real-time streaming responses

## 📄 License

MIT License - See LICENSE file for details

## 👤 Author

Created by [preciadofernando75-crypto](https://github.com/preciadofernando75-crypto)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/preciadofernando75-crypto/astra/issues)
- Email: preciadofernando75@gmail.com
