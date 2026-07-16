# Setting this up on a Windows laptop (no tech skills needed)

Total time: about 15 minutes. You only do this once.

> **The short version:** do steps 1–3 below, then double-click `run-app.bat`.
> The app opens with a **setup wizard** that walks you through the rest —
> the AI key, your profile, and your writing style — with a guided tour at the
> end. Steps 4–6 below are only needed if you prefer doing it by hand.
> (On a Mac it's the same: install Python, then double-click `run-app.command`.)

## 1. Install Python

1. Go to https://www.python.org/downloads/ and click the big yellow download button.
2. Run the installer. **Important: tick the box that says "Add python.exe to PATH"**
   at the bottom of the first screen, then click "Install Now".

## 2. Get the app

If you got this folder as a zip: unzip it somewhere easy, like `Documents\job-searcher`.
(If you use GitHub: green "Code" button → "Download ZIP".)

## 3. Install the app's pieces

1. Open the folder in File Explorer.
2. Click the address bar at the top, type `cmd`, and press Enter — a black window
   opens already pointed at the right folder.
3. Paste this and press Enter (right-click pastes in cmd):

   ```
   pip install -r requirements.txt
   ```

## 4. Add your AI key (once)

1. Create a free account at https://platform.deepseek.com and top it up with the
   minimum (a few dollars lasts months at this usage — roughly a coffee per year).
2. Create an API key and copy it (it starts with `sk-`).
3. In the app folder, copy the file `.env.example`, rename the copy to `.env`,
   open it with Notepad, and make the first line:

   ```
   DEEPSEEK_API_KEY=sk-paste-your-key-here
   ```

   (If Windows hides file extensions and renaming is fiddly: in File Explorer,
   View → tick "File name extensions".)

## 5. Fill in your profile (the most important 20 minutes)

Copy `config\profile.example.yaml` to `config\profile.yaml`, open it in Notepad,
and replace the example person with you: your real background, the job titles you
want, your dealbreakers, and a list of companies you'd genuinely like to work for.
Honest and specific beats impressive — the AI uses this to judge fit, and it can
only be as honest as this file.

## 6. Teach it your writing style (recommended)

1. Put 20+ examples of your own writing into the `voice\corpus` folder — the easiest
   way is Google Takeout (takeout.google.com → deselect all → tick Mail → export just
   "Sent"), then drop the `.mbox` file in. Plain text files with your messages work too.
2. You'll press the "Learn my writing style" button inside the app (step 7).

## 7. Run it

Double-click `run-app.bat` in the folder (or in that black cmd window type
`python -m agent gui`). Your browser opens the app. Bookmark it.

Daily rhythm, about an hour:
1. Click **Find new jobs**, then **Score jobs** (2 minutes, mostly waiting).
2. Look at the best matches. For 1–3 of them, click **Build my application kit**,
   review it, apply on the company's site, click "I applied ✓".
3. Write 2–5 messages with **Write a message** — the app drafts them in your voice,
   you paste them into LinkedIn/email and send them yourself.
4. When people reply or you have calls, mark it on the **People** page.

That's the whole system. Small, steady, and personal — which is exactly what works.
