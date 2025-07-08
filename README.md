# MessageCraft - AI-Powered Messaging & Differentiation Platform

A comprehensive SaaS platform that uses AI agents to generate complete messaging playbooks for businesses, including value propositions, taglines, and ready-to-use marketing content.

## Features

- **AI-Powered Discovery**: 6 specialized agents analyze your business
- **Competitor Analysis**: Understand market positioning and find gaps
- **Complete Playbook**: Get messaging framework with ready-to-use content
- **Strategic Positioning**: Discover unique angles and differentiation
- **Instant Results**: Generate playbooks in 2-3 minutes
- **PDF Export**: Download branded playbooks

## Tech Stack

### Backend
- Python 3.11+
- FastAPI
- CrewAI (AI Agents)
- OpenAI GPT-4
- Supabase (Database)
- Stripe (Payments)
- ReportLab (PDF Generation)

### Frontend
- React 18
- Tailwind CSS
- React Router
- React Query
- Framer Motion
- React Hook Form

## Setup Instructions

### Backend Setup

1. Clone the repository:
```bash
cd messagecraft
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` with your actual values:
- `OPENAI_API_KEY`: Your OpenAI API key
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon key
- `STRIPE_SECRET_KEY`: Your Stripe secret key
- `STRIPE_WEBHOOK_SECRET`: Your Stripe webhook secret

5. Set up the database:
   - Create a Supabase project
   - Run the SQL schema provided in the code comments

6. Start the backend server:
```bash
uvicorn enhanced_api:app --reload
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create environment variables:
```bash
touch .env
```

Add the following:
```
VITE_API_URL=http://localhost:8000
VITE_STRIPE_PUBLIC_KEY=your_stripe_public_key
```

4. Start the development server:
```bash
npm run start
```

The frontend will be available at `http://localhost:3000`

## Project Structure

```
messagecraft/
├── backend/
│   ├── messaging_agents.py    # AI agents implementation
│   ├── enhanced_api.py        # FastAPI application
│   ├── database.py           # Database operations
│   ├── payment.py            # Stripe integration
│   ├── pdf_generator.py      # PDF generation
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── pages/           # React pages
│   │   ├── components/      # Reusable components
│   │   ├── contexts/        # React contexts
│   │   ├── utils/           # Utility functions
│   │   └── App.jsx          # Main app component
│   ├── package.json         # Node dependencies
│   └── tailwind.config.js   # Tailwind configuration
└── README.md
```

## API Endpoints

- `POST /api/v1/generate-playbook` - Generate new messaging playbook
- `GET /api/v1/playbook-status/{session_id}` - Check generation status
- `GET /api/v1/playbook/{id}` - Get playbook details
- `GET /api/v1/download-playbook/{id}` - Download PDF
- `GET /api/v1/user/playbooks` - Get user's playbooks
- `POST /api/v1/create-checkout` - Create Stripe checkout session
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration

## Development

### Running Tests
```bash
# Backend tests
pytest

# Frontend tests
npm test
```

### Linting
```bash
# Backend
flake8 .

# Frontend
npm run lint
```

## Deployment

### Docker
```bash
docker-compose up -d
```

### Production Checklist
- [ ] Set production environment variables
- [ ] Configure CORS for your domain
- [ ] Set up SSL certificates
- [ ] Configure Stripe webhooks
- [ ] Set up monitoring (Sentry, etc.)
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline

## License

This project is proprietary software. All rights reserved.

## Support

For support, email support@messagecraft.com