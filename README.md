# SyllabusToCalendar

Turn a course syllabus PDF into Google Calendar events.

Give it a syllabus → it pulls out every dated item (exams, homework deadlines,
lectures) using `pdfplumber` + Gemini → the events are added to your Google
Calendar as all-day events.

## How it works

1. **Extraction** — `core/data_extraction.py`
   Opens the PDF with `pdfplumber`, reads tables (falling back to raw text
   lines), and keeps only rows that look like schedule entries (dates, month
   names, "due", "exam", "homework").
2. **Parsing** — `core/data_parsing.py`
   Sends the filtered text to Gemini with a Pydantic response schema and gets
   back structured JSON:
   ```json
   {"events": [{"title": "Midterm 1", "event_date": "2026-10-07"}, ...]}
   ```
3. **Calendar upload** — `core/calendar_integration.py`
   Runs the Google OAuth flow in your browser, then inserts each event into
   your primary calendar via the Google Calendar API.

## Project structure

```
SyllabusToCalendar/
├── core/
│   ├── main.py                    # CLI / debug entry point
│   ├── data_extraction.py         # PDF → candidate schedule lines
│   ├── data_parsing.py            # lines → structured events (Gemini)
│   ├── calendar_integration.py    # events → Google Calendar (OAuth)
│   └── credentials.example.json   # template for your OAuth client file
├── app.py                         # web backend        (in progress)
├── templates/
│   └── index.html                 # upload page        (in progress)
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

### Gemini API key

```bash
# Windows (PowerShell)
$env:GEMINI_API_KEY = "your-key-here"

# macOS / Linux
export GEMINI_API_KEY="your-key-here"
```

### Google Calendar OAuth

1. Go to https://console.cloud.google.com and create (or pick) a project.
2. **3bars on rop left→APIs & Services** → Library** → enable **Google Calendar API**.
3. APIS & Services→**OAuth consent screen** → Audience → add your Gmail as a test user.
4. APIS & Services→**Credentials → Create Credentials → OAuth client ID → Desktop app** →
   download the JSON.
5. Save it as `core/credentials.json` (use `core/credentials.example.json`
   as a reference for the expected shape).

`core/credentials.json`, `token.json`, and `client_secret_*.json` are
git-ignored — never commit them.

## Usage (CLI)

Drop your syllabus PDF into `core/`, set the filename in `core/main.py`
(`syllabus = "CSCI2073.pdf"`), then run from inside `core/`:

```bash
cd core
python main.py
```

A browser window opens for Google sign-in and consent; once you approve,
the events are inserted and each one is printed as it's added.

Debug outputs written to `core/`:

- `raw_output.txt` — the filtered rows/lines pulled from the PDF
- `output.txt` — the structured events JSON returned by Gemini

Sample PDFs and `.txt` outputs are git-ignored.

## Status

- [x] PDF table/text extraction with schedule filtering
- [x] Gemini structured extraction of event titles + dates
- [x] Google Calendar upload with OAuth
- [ ] Web app (`app.py` + `templates/index.html`) so it can be used from a
      phone or any browser — **in progress**
- [ ] Review/edit events before uploading
- [ ] Duplicate detection on re-runs

## Notes

- Events are created as **all-day** events. If Gemini returns a non-ISO date
  (e.g. `"TBD"`), `date.fromisoformat` will raise and stop the run.
- The OAuth flow runs every time; there's no token caching yet.