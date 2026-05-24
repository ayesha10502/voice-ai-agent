# Voice AI Agent

A full-stack application for making outbound AI-powered voice calls through a web interface. Built with FastAPI (backend) and vanilla HTML/JS (frontend), integrated with Vapi for telephony, speech recognition, and AI conversation.

## 🚀 Features

- **5 Pre-built Call Scenarios**: Appointment reminders, lead qualification, customer surveys, payment follow-ups, and event registration
- **Real-time Call Monitoring**: Live status updates with animated waveform visualization
- **Call History Tracking**: View all past calls with status, duration, and AI-generated summaries
- **Personalization**: Add customer names and custom context for each call
- **Webhook Integration**: Real-time event updates from Vapi for accurate call tracking
- **Modern UI**: Dark-themed, responsive interface with smooth animations

## 📋 Architecture

```
voice-ai-agent-task/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI endpoints (calls, scenarios, webhook)
│   │   ├── core/          # Configuration and scenario definitions
│   │   ├── models/        # In-memory call storage
│   │   ├── schemas/       # Pydantic data models
│   │   ├── services/      # Vapi API wrapper
│   │   └── main.py        # FastAPI application entry point
│   ├── requirements.txt   # Python dependencies
│   └── .env.example       # Environment variables template
└── frontend/
    └── index.html         # Single-page application (HTML/CSS/JS)
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **httpx** - Async HTTP client for Vapi API
- **python-dotenv** - Environment configuration

### Frontend
- **Vanilla HTML/CSS/JavaScript** - No frameworks required
- **Modern CSS** - Custom properties, grid layout, animations
- **Fetch API** - For backend communication

### AI/Telephony (via Vapi)
- **Groq (Llama 3.3)** - Large Language Model for conversation
- **Deepgram Nova-2** - Speech-to-Text transcription
- **ElevenLabs** - Text-to-Speech voice synthesis
- **Vapi Telephony** - Phone call infrastructure

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- Vapi API key and phone number ID (sign up at [vapi.ai](https://vapi.ai))

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Configure environment variables:
```bash
cp .env.example .env
```

6. Edit `.env` and add your Vapi credentials:
```env
VAPI_API_KEY=your_vapi_api_key_here
VAPI_PHONE_NUMBER_ID=your_phone_number_id_here
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8001
FRONTEND_URL=http://127.0.0.1:5500

```

### Frontend Setup

The frontend is a single HTML file that can be served in multiple ways:

**Option 1: Simple HTTP Server**
```bash
cd frontend
python -m http.server 5500
```

**Option 2: VS Code Live Server**
- Install the "Live Server" extension
- Right-click `index.html` and select "Open with Live Server"

**Option 3: Any web server**
- Serve the `frontend/index.html` file through your preferred web server

## 🚀 Running the Application

1. Start the backend server:
```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

2. Start the frontend (in a new terminal):
```bash
cd frontend
python -m http.server 5500
```

3. Open your browser and navigate to:
   - Frontend: `http://localhost:5500`
   - API Docs: `http://localhost:8001/docs`

## 📖 Usage

### Making a Call

1. **Enter Phone Number**: Input the recipient's phone number in E.164 format (e.g., `+12025551234`)

2. **Add Customer Name (Optional)**: Enter the customer's first name for personalized greetings

3. **Select a Scenario**: Choose from the available scenarios:
   - 🗓️ **Appointment Reminder** - Healthcare appointment confirmations
   - 🚀 **Lead Qualification** - SaaS sales lead discovery
   - ⭐ **Customer Survey** - NPS and satisfaction surveys
   - 💳 **Payment Follow-Up** - Overdue invoice collections
   - 🎟️ **Event Registration** - Event confirmation and logistics

4. **Add Extra Context (Optional)**: Provide additional instructions for the AI agent

5. **Click "Start Call"**: The AI agent will initiate the call and you can monitor it in real-time

### Monitoring Calls

- **Active Call Card**: Shows live call status, duration, and agent information
- **Waveform Animation**: Visual indicator when the call is in progress
- **Status Badges**: Color-coded status indicators (ringing, in-progress, completed, failed, etc.)
- **End Call Button**: Manually terminate an active call

### Call History

- View all past calls in the history section
- Each entry shows phone number, scenario, agent, status, and timestamp
- Status chips provide quick visual feedback on call outcomes

## 🔌 API Endpoints

### Calls
- `POST /api/calls` - Initiate an outbound call
- `GET /api/calls/{call_id}` - Get call status
- `DELETE /api/calls/{call_id}` - End an active call
- `GET /api/calls` - List all calls

### Scenarios
- `GET /api/scenarios` - List all available scenarios
- `GET /api/scenarios/{scenario_id}` - Get scenario details

### Webhook
- `POST /api/webhook/vapi` - Receive Vapi webhook events

### Health
- `GET /health` - Health check endpoint
- `GET /` - API root with links to docs

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `VAPI_API_KEY` | Your Vapi API key | Yes |
| `VAPI_PHONE_NUMBER_ID` | Your Vapi phone number ID | Yes |
| `APP_ENV` | Environment (development/production) | No |
| `APP_HOST` | Backend host address | No |
| `APP_PORT` | Backend port | No |
| `FRONTEND_URL` | Frontend URL for CORS | No |
| `WEBHOOK_BASE_URL` | Public URL for webhooks (ngrok for local) | No |

### Webhook Setup (Optional)

For real-time webhook events during local development:

1. Install ngrok: `https://ngrok.com/download`
2. Start ngrok: `ngrok http 8000`
3. Copy the HTTPS URL from ngrok
4. Set `WEBHOOK_BASE_URL` in `.env` to the ngrok URL
5. Configure the serverUrl in your Vapi dashboard to point to `{WEBHOOK_BASE_URL}/api/webhook/vapi`

## 📝 Scenarios

Each scenario includes:
- **Agent Persona**: Distinct personality and role
- **First Message**: Opening line when call connects
- **System Prompt**: Detailed instructions for the AI agent
- **Conversation Flow**: Structured dialogue guidelines

### Adding Custom Scenarios

Edit `backend/app/core/scenarios.py` to add new scenarios:

```python
SCENARIOS: dict[str, dict[str, Any]] = {
    "your_scenario_id": {
        "id": "your_scenario_id",
        "name": "Your Scenario Name",
        "description": "Brief description of what this scenario does",
        "icon": "🎯",
        "agent": {
            "name": "Agent Name",
            "persona": "Agent personality description",
        },
        "firstMessage": "First thing the agent says",
        "systemPrompt": "Detailed instructions for the AI agent...",
    },
    # ... existing scenarios
}
```

## 🔒 Security Considerations

- Never commit `.env` files with real API keys
- Use environment variables for all sensitive configuration
- In production, replace the in-memory call store with a proper database (PostgreSQL/Redis)
- Implement authentication for the API endpoints in production
- Use HTTPS for all communications in production

## 🐛 Troubleshooting

### Backend Issues

**"VAPI_API_KEY is not configured"**
- Ensure `.env` file exists in the backend directory
- Verify the API key is set correctly

**"Connection refused" errors**
- Check that the backend server is running on the correct port
- Verify the frontend API URL matches the backend port

### Frontend Issues

**"Could not reach backend" toast**
- Ensure the backend server is running
- Check the API URL in `frontend/index.html` (line 586)
- Verify CORS settings in `backend/app/main.py`

**Calls not initiating**
- Verify Vapi API credentials are valid
- Check that the phone number ID is correct
- Ensure phone number is in E.164 format (+country_code number)

## 🚀 Deployment

### Backend Deployment

1. Set environment variables in your hosting platform
2. Install dependencies: `pip install -r requirements.txt`
3. Run with production server: `uvicorn app.main:app --host 0.0.0.0 --port 8001`
4. Configure `WEBHOOK_BASE_URL` to your public domain
5. Update Vapi dashboard with your webhook URL

### Frontend Deployment

1. Upload `frontend/index.html` to any static hosting service
2. Update `FRONTEND_URL` in backend `.env` to your production domain
3. Update the API URL in `index.html` to point to your production backend

Built with ❤️ using FastAPI, Vapi, and modern web technologies.
