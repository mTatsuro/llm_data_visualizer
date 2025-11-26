# LLM based Visualization App – Top 100 SaaS Companies (2025)

This is a small full-stack project that lets users create data visualizations
(pie charts, scatter plots, tables, etc.) over the **Top 100 SaaS Companies 2025**
dataset using natural language prompts powered by the ChatGPT API.

## Tech stack

- **Backend**: Python, FastAPI, Pandas, OpenAI SDK
- **Frontend**: React + Vite, Recharts

The dataset `top_100_saas_companies_2025.csv` is included under `backend/`.

---

## Prerequisites

- Python 3.10+
- Node.js 18+ (with npm or yarn)
- An OpenAI API key with access to `gpt-5.1` (or adjust the model in
  `backend/llm_planner.py`)

Set your API key in the environment:

```bash
export OPENAI_API_KEY="sk-..."
```

---

## Running the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run FastAPI with uvicorn
uvicorn main:app --reload --port 8000
```

The backend will:
- Load the SaaS CSV into memory with Pandas
- Expose `/api/visualize` to turn a natural language prompt into a
  visualization spec & data via the ChatGPT API

You can test the health check at: `http://localhost:8000/health`

---

## Running the frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

By default Vite runs on `http://localhost:5173` and proxies `/api` requests
to the backend running at `http://localhost:8000`.

Open `http://localhost:5173` in your browser.

---

## Example prompts

New visualizations:

- `Create a pie chart representing industry breakdown`
- `Create a scatter plot of founded year and valuation`
- `Create a table to see which investors appear most frequently`
- `Give me the best representation of data if I want to understand the correlation of ARR and Valuation`

Tweaks (after selecting a visualization card):

- `Change the color of the chart to light blue`
- `Make the header row of the table bold`
- `Sort industries by number of companies descending`

The backend uses a small JSON "viz spec" language (groupby/select/filter/sort
+ encodings) and asks the ChatGPT model to generate that spec for each prompt.
Then it executes the spec with Pandas and returns chart-ready data to the
React frontend.
