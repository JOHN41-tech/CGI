# Voyager — AI Learning Studio

An AI-powered learning assistant for building personalized roadmaps, getting step-by-step guidance, and practicing with quizzes.

## Project Structure

```
AI AGENT/
├── backend/                 # Backend code
│   ├── api/                # API integrations
│   │   └── gemma.py  # Google Gemma client via the Gemini Developer API
│   ├── core/               # Core business logic
│   │   ├── roadmap.py     # Roadmap parsing
│   │   └── session.py     # Session management
│   └── utils/              # Utilities
│       ├── database.py    # Database operations
│       └── quiz_generator.py  # Quiz generation
│
├── frontend/               # Frontend code
│   ├── static/            # Static assets
│   │   ├── style.css     # Base styles
│   │   ├── refresh.css   # Responsive Voyager visual system
│   │   └── script.js     # JavaScript
│   └── templates/         # HTML templates
│       └── index.html    # Main page
│
├── app.py                 # Flask application entry point
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose configuration
├── requirements.txt       # Python dependencies
├── .env                   # Local-only environment variables (gitignored)
├── .env.example          # Environment template
├── .dockerignore         # Docker ignore rules
├── .gitignore            # Git ignore rules
└── venv/                 # Virtual environment
```

## Features

- 💬 Interactive AI chat
- 📝 Auto-generated quizzes
- 📌 Note-taking system
- 📊 Progress tracking
- 🗄️ SQLite database persistence
- 🎨 Responsive Voyager learning studio UI
- 🧭 Career-path assessment and topic suggestions

## Local Development

### Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Gemma API keys:**
   - Copy `.env.example` to `.env`
   - Add your Google AI Studio/Gemini API keys as a comma-separated list:
     ```
     GEMMA_API_KEYS=key_one,key_two,key_three
     ```
   - Keep `.env` private. The backend rotates across configured keys and tries another key when Google reports an authentication, quota, or transient service error.
   - The default model is `gemma-4-26b-a4b-it`; set `GEMMA_MODEL` to change it.

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Open browser:**
   Navigate to http://localhost:5000

## Docker Deployment

### Using Docker Compose (Recommended)

1. **Set environment variables:**
   ```bash
   export GEMMA_API_KEYS=key_one,key_two,key_three
   ```

2. **Build and run:**
   ```bash
   docker-compose up -d
   ```

3. **Access the application:**
   Navigate to http://localhost:5000

4. **Stop the application:**
   ```bash
   docker-compose down
   ```

### Using Docker directly

1. **Build the image:**
   ```bash
   docker build -t ai-learning-assistant .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     -p 5000:5000 \
     -e GEMMA_API_KEYS=key_one,key_two,key_three \
     -v $(pwd)/learning_assistant.db:/app/learning_assistant.db \
     --name ai-learning-assistant \
     ai-learning-assistant
   ```

3. **View logs:**
   ```bash
   docker logs -f ai-learning-assistant
   ```

4. **Stop the container:**
   ```bash
   docker stop ai-learning-assistant
   docker rm ai-learning-assistant
   ```

## Environment Variables

- `GEMMA_API_KEYS` - Comma-separated Google Gemini API keys (required; use server-side only)
- `GEMMA_MODEL` - Gemma model ID (default: `gemma-4-26b-a4b-it`)
- `GEMMA_API_TIMEOUT` - Request timeout in seconds (default: `90`)
- `PORT` - Port to run the application (default: 5000)
- `HOST` - Host to bind to (default: 0.0.0.0)
- `FLASK_ENV` - Environment mode: development/production (default: development)
- `SECRET_KEY` - Flask secret key for sessions (auto-generated if not set)

## Deployment to Cloud

### Deploy to Railway/Render/Fly.io

1. Push code to GitHub
2. Connect repository to platform
3. Set environment variable: `GEMMA_API_KEYS`
4. Deploy!

### Deploy to AWS/GCP/Azure

1. Build Docker image
2. Push to container registry
3. Deploy to container service (ECS, Cloud Run, Container Apps)
4. Set environment variables
5. Configure load balancer/ingress

## Technologies

- **Backend:** Flask, SQLite, Python
- **Frontend:** HTML, CSS, JavaScript
- **AI:** Google Gemma via the Gemini Developer API
- **Deployment:** Docker, Docker Compose

## License

MIT
