# AI Health Coach

A chat app for tracking calories. Tell the coach what you ate. It looks the food up in the USDA FoodData Central database, estimates the portion, adds the calories to today's total and keeps a history by day. Logged foods can be deleted, and the app follows the device's light or dark setting (or a manual toggle).

Live demo: https://cortico-ai-health-coach.vercel.app

The demo runs on free tiers. If the shared Gemini quota is used up, the coach says it is busy until the quota resets.

Stack: FastAPI, Vue 3 (plain JavaScript), SQLite locally and in Docker, Postgres (Neon) when deployed, Google Gemini, USDA FoodData Central.

## Run with Docker

Needs Git, Docker Desktop (running) and two free API keys.

```bash
git clone https://github.com/acntldo/ai-health-coach.git
cd ai-health-coach
cp .env.example .env          # Windows PowerShell: Copy-Item .env.example .env
```

Open `.env` and fill in:

```
GEMINI_API_KEY=       # https://aistudio.google.com
GEMINI_MODELS=gemini-3.5-flash-lite,gemini-3.6-flash
USDA_API_KEY=         # https://fdc.nal.usda.gov/api-key-signup
```

`GEMINI_MODELS` is a list, best choice first. If one model is busy or out of quota, the next one is tried. Google renames models often, so check AI Studio for current Flash or Flash-Lite names.

```bash
docker compose up --build
```

The first build takes a few minutes. When the terminal prints `AI Health Coach is ready`, open http://localhost:5173. API docs are at http://localhost:5173/api/docs.

Stop with `Ctrl+C`, then `docker compose down`. Logged food is kept in a Docker volume. `docker compose down -v` deletes it.

Troubleshooting:
- Without keys the app starts, but the coach answers "unavailable". The backend log lists the missing settings.
- `no such column` in the backend log: an old Docker volume from an earlier version. Run `docker compose down -v` and start again.
- Port 5173 already in use: stop whatever is using it.
- If `docker compose` isn't found, try `docker-compose`.

## Run without Docker

Needs Python 3.13 and Node 22, and the `.env` file from above in the project root.

```bash
# terminal 1
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# terminal 2
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Run backend commands from inside `backend`. If Windows blocks `uvicorn.exe`, the `python -m` form above avoids it.

## Tests

```bash
cd backend
python -m pytest
```

Gemini and USDA are faked in the tests, so no keys are needed and no quota is used.

## Deploy (Vercel)

The repo deploys to Vercel as one project with two services, set up in `vercel.json`: the Vue app at `/` and the FastAPI backend at `/api`. The deployed app uses Neon Postgres.

1. Import the repo in Vercel.
2. Add `GEMINI_API_KEY`, `GEMINI_MODELS` and `USDA_API_KEY` as environment variables, and a Neon Postgres database. The database adds `DATABASE_URL`.
3. Create the tables once: from `backend`, run `python -m app.create_tables` with `DATABASE_URL` set to the database's direct (unpooled) address.
4. Deploy.

## How the coach works

1. Gemini reads the message, the last 10 messages and today's log, and lists any foods the user says they ate. If there is no food, it just replies.
2. Each food is searched in USDA (generic foods only, not branded products).
3. Gemini picks the best match and estimates the portion in grams.
4. The code works out the calories: kcal per 100 g x grams / 100. The model does no arithmetic.
5. Entries and messages are saved. The reply names every assumption it made.

Each entry has a confidence level. High: clear match and the amount was given. Medium: close match, or the portion was assumed. Low: no USDA match, so it is a rough guess. Low entries are labelled "Rough estimate" in the app.

The coach does not set calorie targets, diets or weight goals.

## Limits

- 20 messages per device per day and 200 in total per day (`DEVICE_DAILY_LIMIT`, `GLOBAL_DAILY_LIMIT`). Resets at midnight UTC.
- The free Gemini tier has small quotas. A food message uses two Gemini calls.
- On the live demo, everyone shares one Gemini quota. When it runs out, the coach says it is busy.
- Messages are sent to Google Gemini. On the free tier, Google may use them to improve its models, so don't enter personal information.

## Structure

```
backend/
  main.py             entry file Vercel looks for
  app/
    main.py           app setup
    config.py         settings from .env
    database.py       database connection
    models.py         tables
    create_tables.py  creates the tables on a hosted database
    schemas.py        response and request shapes
    coach.py          the two-step pipeline
    prompts.py        instructions given to Gemini
    gemini.py         Gemini client, model fallback, retries
    usda.py           USDA search
    usage.py          daily limits
    crud.py           queries
    routers/          chat, days, entries, messages
  tests/
frontend/
  src/
    views/            ChatView.vue, HistoryView.vue
    components/
    api.js, device.js, store.js, theme.js
docker-compose.yml
vercel.json
```

## API

Every request except `/api/health` needs an `X-Device-ID` header.

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/chat` | send a message, returns the reply, logged foods and today's total |
| GET | `/api/messages` | saved conversation, last 50 messages |
| GET | `/api/days` | days with food, newest first, with totals |
| GET | `/api/days/{date}` | foods and total for one day |
| DELETE | `/api/entries/{id}` | delete a logged food |
| GET | `/api/health` | health check |

## Choices

- **Calories come from USDA data, calculated in code.** The model only reads the message and picks a match. This keeps the numbers traceable.
- **Model output is validated.** Bad JSON is retried once, then rejected. Values outside sane ranges are not logged.
- **No login.** Each browser creates a random ID and sends it with every request. Anyone who has that ID can see that data.
- **The browser sends its local date**, so a late meal isn't filed under tomorrow's UTC date.
- **Models are a list in settings**, because Google renames and retires them, and the free quota is per model.
- **Chat is saved on the server**, so it survives a refresh.
- **SQLite locally and in Docker, Postgres on Vercel.** Vercel's file system is read-only, so the deployed app needs a hosted database. `DATABASE_URL` picks which one is used.
- **Hash URLs** (`/#/history`), so refreshing a page works on static hosting without extra server rules.

## Assumptions

- Without an amount, the coach assumes one typical serving and says so.
- USDA has gaps, especially for regional dishes (no plain chicken adobo, for example). Those get a low-confidence estimate.
- After a refresh, the chat text is restored but the food chips aren't. The foods are in History.
- Calories are estimates, not measurements. This is not medical advice.

## Feedback on the test

- The instructions are split by role (Back End, Full Stack, Front End), and the AI Software Developer role isn't listed. It wasn't clear whether Docker and tests were required for it.
- The AI project heavily relies on an outside API, which created unexpected bottlenecks. Model names changed while I was building, and I ended up spending a huge chunk of my time just dealing with 429 and 503 errors instead of actually developing the app. Since I only had about eight active hours to dedicate to this, losing so much of that time to free-tier API limits made completing the project quite difficult.
- I also ran into some hurdles getting Docker to work on Windows, as I had to troubleshoot my WSL and virtualization settings. A quick heads-up in the instructions about expected setup time for Windows users would be great so it doesn't eat into their actual coding time.