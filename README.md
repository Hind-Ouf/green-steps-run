# Green Steps Run

A student charity run where every kilometre plants a tree. Runners log kilometres, sponsors pledge kroner per kilometre, and 50 kr raised equals 1 tree. Built for the Vibe Coding assignment with generative AI.

**Demo:** VibeOff link : https://vibeoff.ai/build/a-student-charity-run-app-where-every-kilometre-a-runner-52e4d821

> **Note on origin:**  AI helped reconstructed this codebase: Claude Code, Gemini, Chatgpt.

## Features
- Event dashboard, leaderboard and faculty team pages (rank, rival gap)
- Organiser-PIN-protected run logging, checked on the server (demo PIN `1234`; set `ORGANIZER_PIN`)
- Printable runner bibs with QR codes. Scanning one opens the run form with the bib prefilled.
- Sponsor pledges (NOK per km, optional cap), a thank-you page that updates as the runner runs, and a downloadable sponsor story PNG
- Milestone story cards (PNG) when a runner reaches 10, 25 or 50 trees
- Weekly recap (last 7 days or this week) with top runner and fastest-growing faculty
- Seeded demo data

## Run locally
Requires Python 3.10+ and Node.js 18+.

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python seed.py
ORGANIZER_PIN=your-private-pin uvicorn app:app --reload --port 8001   # demo default is 1234

# Frontend (new terminal)
cd frontend
npm install
npm run dev        # open http://localhost:5173
```

API docs: http://localhost:8001/docs. The frontend uses `VITE_API_URL` if set, otherwise `http://localhost:8001/api`. See `frontend/.env.example` for configuration. For printed QR bibs used at a real event, set `VITE_PUBLIC_APP_URL` to the deployed frontend URL and rebuild the frontend. QR codes generated with a localhost URL will only work on the same computer.

## How AI was used

the first version was built with an AI app builder. The code in this repository was then reviewed by a second AI, which found six bugs by reading the code (the QR link not opening the run form, a dead thank-you link, a weekly recap using different tree and money rules from the rest of the app, a milestone pop-up that repeated after every run, a pledge form that failed by default for the second event, and a sponsor card that counted kilometres from other events). Five were fixed and the dependencies were pinned.

## Testing
Tick these off after running the app yourself:
- [ ] `python seed.py` runs and the backend starts
- [ ] A wrong PIN is rejected, the right PIN records the run
- [ ] A run for an unknown bib shows "Runner bib not found"
- [ ] Opening `/?bib=1003` shows the "Log a run" form with bib 1003 filled in
- [ ] Creating a pledge shows the thank-you page, and `/thanks/<id>` reopens it after a reload
- [ ] Pledging for event 2 works without clearing the runner field
- [ ] The milestone card appears only when a new milestone (10, 25, 50) is reached
- [ ] The weekly recap trees and kroner agree with the leaderboard
- [ ] Print bibs shows QR codes and prints two per row
- [ ] On a phone, scan a printed QR code and confirm it opens the deployed app with the correct bib prefilled

## Limitations and next steps
- An event-wide pledge's maximum is applied per runner, not as a total across the event.
- The recap counts every pledge, including ones made after the run.
- The PIN is one shared organiser PIN, with no per-runner login and no rate limiting.
- No real payments (a Vipps link per sponsor would be the next step), and distances are typed in, not imported from Strava or a watch.
- SQLite is fine for a demo; a hosted database would be needed for a live event.

## Data and privacy
All names are made up. No keys or personal data are stored. Never commit a real PIN or `.env` file.

## Licence
MIT, see `LICENSE`. Replace `[Your Name]` with your name.



