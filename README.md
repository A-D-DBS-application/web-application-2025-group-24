Project A&D – DBS

GroundLink (Group 24)

Description

GroundLink is a discreet online platform that connects landowners and real estate developers outside the public market. The platform enables landowners to offer building land anonymously while allowing only verified developers to view listings and respond. By avoiding public listing websites, GroundLink reduces price inflation, competition and unwanted visibility, creating a fair and efficient off‑market transaction channel.

Vision

To enable fair and discreet land transactions by bringing landowners and developers together in a trusted closed environment. GroundLink aims to reduce market friction, remove unnecessary intermediaries and unlock hidden land supply.

Core problem

Developers want to acquire building land early (before public listings increase price/competition). Landowners often prefer to sell quietly without exposure, agents or social pressure. GroundLink provides a closed, verified environment to match supply and demand discreetly.

Solution

GroundLink provides a closed online platform where Landowners can anonymously list their land off market Only verified real estate developers can log in view listings and contact sellers

This creates a discreet and efficient channel between buyers and sellers without public visibility intermediaries or unnecessary complexity.

MVP scope (what we built)
The MVP is designed to validate one key question:

Are landowners willing to offer their land through a discreet online platform outside the public market

To answer this the MVP focuses on two core features
- Landowners: create anonymous/off‑market listings (location, size, price) and upload images.
- Developers: register/login, browse vetted listings and express interest.

Why this MVP is valuable

The MVP is low complexity and high validation value — it lets us quickly test whether landowners will use a discreet online channel and whether developers find off‑market leads valuable.

Links & demo

- Kanban board (Miro): https://miro.com/app/board/uXjVJwfM1RM=/
- UI prototype (Lovable): https://lovable.dev/projects/032f86ea-8bd2-4d3b-b60b-ba8dcca7a68c?permissionView=main
- Figma: https://www.figma.com/make/JyE2BWxF58h0nvDnAwRvb4/Discreet-Land-Sale-Platform?node-id=0-4&p=f&t=TuZWftnpnDQQe63a-0
- Live application (Render): https://group-24-4myd.onrender.com/
- Demo video (YouTube): https://www.youtube.com/watch?v=5l8xzvWOSDg
- Supabase project dashboard: https://supabase.com/dashboard/project/gdgxsgbgppresinempzk/database/schemas

Quick install & run (cross‑platform)

Prerequisites: Python 3.10+, Git (optional), Supabase account (optional).

1) Clone (optional):

```bash
git clone https://github.com/ambervrschldn/group-24.git
cd group-24
```

2) Create & activate virtual environment

macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

Windows PowerShell:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Windows cmd.exe:
```cmd
python -m venv venv
.\venv\Scripts\activate.bat
```

3) Install dependencies:
```bash
pip install -r requirements.txt
```

4) Create a `.env` in the project root with (example):
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-or-service-key
SECRET_KEY=replace-with-a-random-secret
```

5) Run the app:
```bash
python app.py
```

Default URL: http://127.0.0.1:5000

Notes: on Windows you can use `py app.py`. For production, use a WSGI server (Gunicorn/uWSGI) or a managed host.

Repository structure (high level)

```
app.py
templates/
static/
requirements.txt
README.md
```

Authors: GroundLink — Group 24 (A&D DBS course)
Other Information:
This project was developed as part of the A&D DBS course.
The focus is on validating a real world problem using a minimal but functional web application.


