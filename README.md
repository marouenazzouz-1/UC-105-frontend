# UC-105 AI-Recommendations-Church-Commissioners Strategy - Frontend
 
A **Streamlit** single-page chat interface that talks to the `UC-105` backend Azure Function App.
 
---
 
## What it does
 
- Identifies the current user via **Azure Easy Auth** (`X-Ms-Client-Principal-Name` header) when deployed, or falls back to an anonymous ID in local dev.
- Uses the user identity as the `session_id` sent to the backend, so each user's conversation history is isolated.
- On first load, **fetches existing history** from `GET /api/session/{user_id}/history` so the chat is restored across browser refreshes.
- Displays a sidebar with the current user ID, the LLM context window size (K), and the total messages stored in the backend DB.
- The **Clear conversation** button calls `DELETE /api/session/{session_id}` on the backend and resets local state.
---
 
## Folder structure
 
```
.
├── app.py               # Streamlit app — single entry-point
├── Dockerfile           # Container image for Azure Web App for Containers
└── requirements.txt     # Python dependencies
```
 
---
 
## Running locally
 
### Prerequisites
 
- Python 3.11+
- The backend Function App running at `http://localhost:7071` (see [backend README](../backend/README.md))
```bash
pip install -r requirements.txt
 
export BACKEND_URL="http://localhost:7071/api"
export FUNCTION_KEY=""
 
streamlit run app.py
```
 
The app will open at `http://localhost:8501`.
 
---
 
## Environment variables
 
| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_URL` | `http://localhost:7071/api` | Base URL of the Azure Function App |
| `FUNCTION_KEY` | `` | Azure Function host key — leave empty for local dev |
 
In production set these as **App Service environment variables** (portal: Settings → Environment variables, or via the Azure CLI).
 
---
 
## Azure deployment overview
 
The frontend runs as a containerised Streamlit app on **Azure Web App for Containers**. Some high level steps include:
 
- **Container registry** — create an Azure Container Registry (ACR), build the Docker image, and push it.
- **Web App for Containers** — create the Web App, point it at the ACR image.
- **Environment variables** — set `BACKEND_URL` (the Function App URL) and `FUNCTION_KEY` (the backend host key) in App Service → Settings → Environment variables.
- **Easy Auth** — enable Azure AD authentication on the Web App so the `X-Ms-Client-Principal-Name` header is injected automatically. Set the action for unauthenticated requests to redirect to the login page, and restrict access to your organisation's AAD tenant.