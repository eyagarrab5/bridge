# THE BRIDGE 2026 — Attendee Portal

Flask + SQLite web app for managing event attendees with QR code generation.

## Features
- Add attendees with name, photo, LinkedIn URL, and category (Masterclass / VIP / Participant)
- Auto-generates a QR code pointing to each attendee's LinkedIn profile
- Live directory with category filtering
- Masterclass showcase with descriptions, key takeaways, and video embeds
- SQLite database — no external DB needed

## Setup

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python app.py
```

Then open http://localhost:5000 in your browser.

## Project structure
```
bridge_app/
├── app.py                  # Flask app, models, routes
├── requirements.txt
├── static/
│   ├── css/style.css       # All styles
│   ├── uploads/            # Uploaded attendee photos
│   └── qrcodes/            # Generated QR code images
└── templates/
    ├── index.html          # Directory + add-attendee form
    └── masterclasses.html  # Full masterclass showcase page
```

## Adding your own Masterclasses
Edit the `seed_masterclasses()` function in `app.py`.  
For video embeds, use YouTube's embed URL format:
`https://www.youtube.com/embed/VIDEO_ID`

## Customising categories
The three default categories are `masterclass`, `vip`, and `participant`.  
To add more, update the radio inputs in `templates/index.html` and add matching CSS classes in `static/css/style.css`.
