# SyllabusToCalendar

Turn a course syllabus PDF into Google Calendar events.

Give it a syllabus → it pulls out every dated item (exams, homework deadlines,
lectures) using `pdfplumber` + Gemini → you review the list in your browser →
the events are added to your Google Calendar as all-day events.

## How it works

1. **Extraction** — `core/data_extraction.py`
   Opens the PDF with `pdfplumber`, reads tables (falling back to raw text
   lines on pages without tables), and keeps only rows that look like schedule
   entries (dates, month names, "due", "exam", "homework").
2. **Parsing** — `core/data_parsing.py`
   Sends the filtered text plus the term year to Gemini with a Pydantic
   response schema and gets back structured JSON:
   ```json
   {"events": [{"title": "Midterm 1", "event_date": "2026-10-07"}, ...]}
   ```
   The year is supplied by you because syllabi usually write dates like
   `17-Aug` with no year, and Gemini would otherwise guess one.
3. **Calendar upload** — `core/calendar_integration.py`
   Runs the Google OAuth flow in your browser, then inserts each event into
   your primary calendar via the Google Calendar API.

`app.py` wraps all three in a small Flask site: upload → review → add.

## Project structure

```
SyllabusToCalendar/
├── app.py                         # Flask web app (upload / review / add)
├── templates/
│   └── index.html                 # the single page the web app renders
├── core/
│   ├── main.py                    # CLI / debug entry point
│   ├── data_extraction.py         # PDF → candidate schedule lines
│   ├── data_parsing.py            # lines → structured events (Gemini)
│   ├── calendar_integration.py    # events → Google Calendar (OAuth)
│   └── credentials.example.json   # template for your OAuth client file
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.11+
- A Gemini API key — https://aistudio.google.com/apikey
- A Google Cloud OAuth client (Desktop app) with the Calendar API enabled

## Setup

```bash
git clone https://github.com/aayush0000001/SyllabusToCalendar.git
cd SyllabusToCalendar
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

### 1. Gemini API key

```bash
# Windows (PowerShell)
$env:GEMINI_API_KEY = "your-key-here"

# macOS / Linux
export GEMINI_API_KEY="your-key-here"
```

### 2. Flask secret key

The web app stores the extracted events in a signed session cookie, which
needs a secret key. Generate one:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Create a file named `.env` in the project root containing:

```
FLASK_SECRET_KEY=paste_the_generated_key_here
```

### 3. Google Calendar OAuth

1. Go to https://console.cloud.google.com and create (or pick) a project.
2. ☰ menu (top left) → **APIs & Services → Library** → enable
   **Google Calendar API**.
3. **APIs & Services → OAuth consent screen → Audience** → add your Gmail as
   a test user.
4. **APIs & Services → Credentials → Create Credentials → OAuth client ID →
   Desktop app** → download the JSON.
5. Save it as `core/credentials.json` (see `core/credentials.example.json`
   for the expected shape).

`.env`, `core/credentials.json`, `token.json`, and `client_secret_*.json`
are git-ignored — never commit them.

## Usage

### Web app

From the project root:

```bash
python app.py
```

Open http://127.0.0.1:5000, choose your syllabus PDF, enter the year of the
term, and click **Extract events**. Review the table, then click
**Add to Google Calendar**. A Google sign-in window opens; once you approve,
the events are inserted.

> The sign-in window opens on the machine running `app.py`, so for now the
> web app is meant to be used from the same computer. Phone support needs
> the web-based OAuth flow (see Status).

### CLI (for debugging)

Drop your syllabus PDF into `core/`, set the filename and `class_year` in
`core/main.py`, then run from the project root:

```bash
python -m core.main
```

It prints each event as it's added and writes two debug files to the
directory you ran it from:

- `raw_output.txt` — the filtered rows/lines pulled from the PDF
- `output.txt` — the structured events JSON returned by Gemini

Sample PDFs and `.txt` outputs are git-ignored.

## Status

- [x] PDF table/text extraction with schedule filtering
- [x] Gemini structured extraction of event titles + dates
- [x] Google Calendar upload with OAuth
- [x] Flask web app: upload → review → add
- [ ] Edit events in the browser before uploading
- [ ] Web-based OAuth flow so it works from a phone
- [ ] Duplicate detection on re-runs
- [ ] Token caching so you don't sign in every time

## Notes

- Events are created as **all-day** events; times in the syllabus are
  ignored.
- If Gemini returns a non-ISO date (e.g. `"TBD"`), `date.fromisoformat`
  raises and stops the run.
- Test with a small syllabus first — every run inserts all events again, and
  there's no duplicate detection yet.
