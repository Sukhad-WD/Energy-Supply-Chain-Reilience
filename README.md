# Energy Supply Chain Resilience

An AI-assisted energy supply-chain decision-support prototype. It analyzes energy-related news, estimates disruption risk, models an impact scenario, and ranks alternative suppliers. Its score and scenario impacts are heuristic planning estimates, not validated forecasts.

## Deploy the API to Render

1. Push this repository to GitHub.
2. In Render, choose **New + → Blueprint** and select this repository. Render reads `render.yaml` and creates the API service.
3. In the Render service environment settings, set `GEMINI_API_KEY` to your Gemini API key. Never put the key in GitHub or a `VITE_` variable.
4. Deploy. Check `https://<your-render-service>.onrender.com/`; it should return `Agent 3 Running Successfully`.
5. Keep the deployed API URL for the frontend setup below.

The free Render service may sleep when idle; its first request after sleeping can take longer. Generated PDFs are stored on the service filesystem, which is ephemeral on free hosting.

## Deploy the frontend to Vercel

1. In Vercel, import this GitHub repository.
2. Set **Root Directory** to `frontend`.
3. Vercel detects Vite. Use `npm run build` as the build command and `dist` as the output directory.
4. Add the environment variable `VITE_API_BASE_URL` with the Render API origin, for example `https://<your-render-service>.onrender.com`. Do not add a trailing slash.
5. Deploy and copy the Vercel site origin, for example `https://<your-project>.vercel.app`.

Back in Render, set `FRONTEND_ORIGINS` to that exact Vercel origin (no trailing slash), save, and redeploy the API. For a Vercel preview deployment, add its origin to the comma-separated list only if that preview needs API access.

## Run locally

1. Install the packages in `requirements.txt`.
2. Copy `.env.example` to `.env` and set `GEMINI_API_KEY`.
3. Run the API from the project root with `uvicorn app:app --reload`.
4. Copy `frontend/.env.example` to `frontend/.env` if you need a non-default local API address.
5. In `frontend`, run `npm install` and `npm run dev`.

## Deployment notes

- `GEMINI_API_KEY` is a backend-only secret. Keep it in Render's environment settings.
- Supplier records in `data/suppliers.json` are demo data; verify their values and units before using recommendations operationally.
- RSS availability, AI event extraction, and fixed scenario assumptions affect the results. Validate the pipeline against historical events before describing its risk score as predictive.
- The backend provides generated PDFs through `/download/<filename>`. Files may disappear when the hosting instance restarts or redeploys.
