# Green Steps Run

A prototype charity run app for student associations. Runners log kilometres, sponsors make pledges per kilometre, and the app estimates how many trees those pledges could fund at 50 NOK per tree. It was built with generative AI for a Vibe Coding assignment.

**VibeOff showcase and video:** [View Green Steps Run on VibeOff](https://vibeoff.ai/build/a-student-charity-run-app-where-every-kilometre-a-runner-52e4d821)

> **AI use:** The first version was built with an AI app builder. I then used AI to review and improve the code.

## Features

- Event dashboard with a runner leaderboard and faculty team pages
- Run logging protected by an organiser PIN checked by the backend
- Printable runner bibs with QR codes that open the run form with the bib number filled in
- Sponsor pledges per kilometre, with an optional maximum amount
- A thank-you page that updates as kilometres are logged
- Downloadable sponsor and milestone story cards
- Weekly recap with distance and estimated impact
- Seed data for trying the prototype

## Run locally

Requires Python 3.10+ and Node.js 18+.

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python seed.py
ORGANIZER_PIN=your-private-pin uvicorn app:app --reload --port 8001

# Frontend, in a second terminal
cd frontend
npm install
npm run dev
```

Open the frontend at http://localhost:5173. The API documentation is at http://localhost:8001/docs.

The frontend uses `VITE_API_URL` if set; otherwise it connects to `http://localhost:8001/api`. See `frontend/.env.example` for configuration. QR codes use the current browser address unless `VITE_PUBLIC_APP_URL` is set. For a deployed app, set that variable to the public frontend URL and rebuild the frontend.

**Demo data warning:** `python seed.py` resets the database and replaces its contents with sample data. Use it only when you want to reset the demo.

## How AI was used

I used generative AI to build the first version, review the code, and make improvements. An AI code review identified six issues, including QR links, thank-you links, milestone behaviour, event selection, and calculations. Five were fixed, and the dependencies were pinned. The review also helped identify limitations in the recap calculations, which are listed below.

## Testing

The frontend production build completed successfully. The checklist below is for additional manual checks; mark an item complete only after running it yourself.

- [ ] `python seed.py` runs and the backend starts
- [ ] A wrong PIN is rejected, and the correct PIN records a run
- [ ] An unknown bib number shows an error
- [ ] Opening `/?bib=1003` opens the run form with bib 1003 filled in
- [ ] Creating a pledge opens the thank-you page, and `/thanks/<id>` works after reloading
- [ ] Pledging for the second event works
- [ ] A milestone card appears when a runner reaches a new 10, 25, or 50 tree milestone
- [ ] Print bibs shows QR codes and prints correctly
- [ ] A printed QR code opens the deployed app with the correct bib number

## Limitations and next steps

- This is a prototype. It does not collect payments or verify logged distances.
- The app estimates tree impact from pledges; it does not confirm that money was collected or trees were planted.
- An event-wide pledge's maximum is applied separately to each runner, rather than once across the whole event.
- The weekly recap includes pledges made after a run and does not apply pledge maximums. Its totals may therefore differ from the leaderboard.
- Run logging uses one shared organiser PIN. There are no individual accounts or rate limits.
- Distances are entered manually; they are not imported from Strava or a running watch.
- SQLite is suitable for this demo. A live event would need a hosted database and additional safeguards.

## Data and privacy

The included runner names are made up. Do not use real personal data or commit passwords, PINs, API keys, or `.env` files.

## Licence

MIT. See `LICENSE`.
