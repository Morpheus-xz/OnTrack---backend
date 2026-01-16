# OnTrack Backend

## Overview

OnTrack Backend powers the AI-driven career navigation platform, OnTrack. It handles authentication validation, career intelligence logic, AI-driven roadmap generation, and serves secure APIs to the frontend. The system is designed to be state-driven, deterministic, and safeguarded from AI hallucinations by constraining outputs to real market roles.

## Features & Functionality

- **FastAPI-based REST API**
- **AI Career Engine:**
  - Maps users to valid career roles from the database.
  - Identifies current vs missing skills.
  - Generates a structured 12-week learning roadmap.
- **Constrained AI Output:**
  - Limits AI to predefined career roles, avoiding free-form guessing.
- **AI Career Coach:**
  - Provides context-aware responses based on user state and learning plans.
- **GitHub & LeetCode Integration:**
  - Fetches user profile data to support skill evaluation.
- **Supabase Integration:**
  - Stores user state, career results, and recommended resources.
- **Production-ready Deployment:**
  - Fully deployed on Render.

## Tech Stack

- Python
- FastAPI
- OpenAI API
- Supabase (PostgreSQL + Auth)
- Render (Deployment)
- Uvicorn
- OAuth (via Supabase)

## Prerequisites & Setup

### Requirements

- Python 3.10+
- Supabase project (URL + anon key)
- OpenAI API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Morpheus-xz/OnTrack---backend.git
   ```
2. Navigate to the project:
   ```bash
   cd ontrack-backend
   ```
3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Environment Variables

Create a `.env` file with the following variables:

```dotenv
OPENAI_API_KEY=your_openai_key
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_key
```

### Run Locally

Use Uvicorn to run the application:

```bash
uvicorn main:app --reload
```

## API Overview

| Endpoint                      | Method | Description                            |
|-------------------------------|--------|----------------------------------------|
| `/run-ai/{user_id}`           | POST   | Runs career AI and generates roadmap.  |
| `/coach/{user_id}`            | POST   | Provides AI career coach responses.    |
| `/github-stats/{username}`    | GET    | Fetches GitHub stats.                  |
| `/leetcode-stats/{username}`  | GET    | Fetches LeetCode stats.                |

## Contribution Guidelines

- Keep AI logic deterministic and constrained.
- Avoid introducing free-form AI career generation.
- Follow existing schema contracts with Supabase.
- Use clear, typed API responses.

## Deployment

- Hosted on [Render](https://render.com/).
- Uses production environment variables.
- CORS configured for frontend domains.
