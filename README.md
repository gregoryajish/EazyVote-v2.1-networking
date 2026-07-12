# EazyVote v2.0 (Vimalagiri Customization)

> **A secure, multi-post desktop election management system built for Vimalagiri Public School, Kothamangalam — Academic Session 2026–2027**

---

## Overview

**EazyVote** is a secure, fast, and visually polished voting application designed for conducting internal student council elections within educational institutions. It runs entirely on-site using local hardware, connecting to a local MySQL database to record and retrieve votes in real time. 

Version 2.0 is custom-tailored for **Vimalagiri Public School** and supports a highly scaled-up election structure. It includes a brand-new multi-page ballot system, external theme configuration, robust kiosk lockdown controls, and a **dual-database offline failover architecture** to ensure a smooth, tamper-proof, and resilient voting experience.

---

## What's New in v2.0 (Changes from Previous Version)

Compared to the previous version (deployed for St. George Public School), v2.0 brings the following upgrades:

*   🏛️ **School & Session Migration** — Migrated branding and logic for **Vimalagiri Public School, Kothamangalam** for the **2026–27 academic session**.
*   🗄️ **Database Rebranding** — Upgraded the MySQL schema to use database `vimalagiri2026` (instead of `george`).
*   📈 **Massive Candidate & Post Scale-Up** — Expanded from **2 posts** to **8 posts** (Head Boy, Head Girl, Sports Boy, Sports Girl, Arts Boy, Arts Girl, Discipline Boy, and Discipline Girl) and from **6 candidates** to **16 candidates** (2 candidates per post).
*   🗳️ **Multi-Page Ballot Navigation** — Split the ballot into **4 pages** (2 posts per page) to handle the increased number of posts. A dynamic "Next" button guides voters through screens, finishing with a "Finish" button on the final page.
*   ⚙️ **External Configuration System** — Introduced `start_screen_config.json` to configure the school name, academic year, logo/button paths, color themes, and Terms/About text without touching the source code.
*   🛠️ **In-App Branding Editor** — Right-clicking the splash screen launches a secure admin form to modify branding details and swap image assets on the fly.
*   🔌 **Network Resilience & Dual-DB Failover** — 
    *   **Primary DB:** Primary transactions operate on a centralized **MySQL database** hosted on the local network.
    *   **Fallback Cache:** A local embedded **SQLite cache** (`local_voting.db`) serves as an offline database.
    *   **Auto-Failover:** If the network goes down or the MySQL server is unreachable at startup, the kiosk automatically switches to **Offline Mode**, allowing voting to continue uninterrupted using the SQLite database.
*   🔄 **Automatic Vote Syncing & Recovery** — 
    *   Offline votes are recorded immediately in the local SQLite database and queued in an `offline_votes` table.
    *   During application startup or when administrators reset/loop the screen, the application pings the MySQL database and attempts to reconnect.
    *   Once a stable connection is re-established, all cached offline votes are batch-uploaded to the central MySQL server, and the local SQLite cache is mirrored to match the latest live tallies.
*   📝 **Robust Error Logging** — Database errors and connection timeouts are logged with timestamps to `db_error.log` for easy troubleshooting.
*   🔒 **Kiosk Lockdown & Access Control** — 
    *   Locks the voter interface in fullscreen kiosk mode (`-fullscreen True`) and overrides close events.
    *   The "Quit" button is disabled by default on completion; administrators can press `u` or `U` to silently unlock it.
    *   To safely terminate the app, administrators can use the shortcut `<Control-Shift-Q>` (or `<Control-Shift-q>`) and enter the secure PIN (`9744`).
*   📂 **Project Reorganization** — Renamed the main ballot app to `vimalagiri.py` (with spec `vimalagiri.spec`), cleaned up redundant legacy background files (removed `table.jpg`), and added Photoshop project config files (`.psxprj`).

---

## Features

- 🗳️ **Interactive Multi-Page Ballot** — A sleek, distraction-free photo ballot. Voters select one candidate per post across 4 pages.
- 📊 **Real-Time Results Viewer** — An admin dashboard that pulls live tallies from the MySQL database (or SQLite cache in offline mode) and presents them in a structured table.
- 🔌 **Resilient Offline Voting** — Handles network instability gracefully. The app automatically caches votes locally and synchronizes them to the MySQL server as soon as the network returns.
- 🔒 **One-Vote-Per-Post Enforcement** — Clickable photo-buttons are immediately disabled after a vote is cast to prevent double voting.
- 🗄️ **Dual Database Architecture** — Integrates MySQL Server (local network) and SQLite (local cache) with automatic data synchronization.
- 📋 **CSV Results Export** — Generates a timestamped `results.csv` automatically whenever results are requested.
- 🎨 **Fully Customizable Themes** — Customize backgrounds, accents, logos, and terms via the configuration menu.
- ⚙️ **Quick Reset & Setup** — Scripts to initialize databases (`sqltable.py`) or reset vote tallies to zero (`reset.py`) in one click.

---

## Project Structure

```
Vimalagiri 2026-27(net)/
│
├── vimalagiri.py           # Main voting kiosk application (with network failover & sync)
├── result.py               # Results viewer & CSV generator (with network failover)
├── sqltable.py             # Database initializer (Creates MySQL & SQLite tables and seeds candidates)
├── reset.py                # Database reset utility (Clears MySQL & SQLite votes, keeps candidates)
│
├── Candidates/             # Candidate profile pictures
│   ├── candidate1.jpg      # Lious Basil Joshy
│   ├── candidate2.jpg      # Daniel Saji
│   ├── candidate3.jpg      # Meera P V
│   ├── ...                 
│   ├── candidate16.jpg     # Dilsha Nasrin
│   └── cover.jpg           # Fallback/default image
│
├── Photoshop Config Files/ # Design source projects (.psxprj)
│   ├── resstrtscrn.psxprj  
│   ├── startscreen.psxprj  
│   └── table.psxprj        
│
├── Fonts/                  # Custom application fonts
├── Legal/                  # Product documentation and license agreements
├── Deployement/            # Built executable installers & resources
├── build/                  # PyInstaller build artifacts
├── dist/                   # Compiled standalone executables (.exe)
│
├── start_screen_config.json# Dynamic splash screen configuration
├── continuebtn.jpg         # "Continue" button image asset
├── finishbtn.jpg           # "Finish" button image asset
├── nextbtn.jpg             # "Next" button image asset
├── quitbtn.jpg             # "Quit" button image asset
├── generbtn.jpg            # "Generate Results" button image asset
├── startscreen.jpg         # Voting app splash screen background
├── resstrtscrn.jpg         # Results viewer splash screen background
├── logo.ico                # Application launcher icon
├── vimalagirilogo.png      # High-res Vimalagiri School Logo
├── vimalagirilogo.jpeg     # Fallback Vimalagiri School Logo
├── local_voting.db         # Local SQLite cache database for offline resilience
├── db_error.log            # MySQL connection error log file
├── results.csv             # Auto-generated CSV reports
└── data.dat                # App data file
```

---

## Candidates List

| Serial No. | Name                 | Class | Post             |
|:----------:|----------------------|:-----:|------------------|
| **1**      | Lious Basil Joshy    | XII A | Head Boy         |
| **2**      | Daniel Saji          | XI A  | Head Boy         |
| **3**      | Meera P V            | XII C | Head Girl        |
| **4**      | Aida Jojo            | XI B  | Head Girl        |
| **5**      | Noha Binil           | XII A | Sports Boy       |
| **6**      | Abhinav Krishna P    | XI A  | Sports Boy       |
| **7**      | Abhinaya Suresh      | XII B | Sports Girl      |
| **8**      | Delna Mariya Jaison  | XI B  | Sports Girl      |
| **9**      | Naveen T.S           | XII A | Arts Boy         |
| **10**     | Chris Ullas          | XI B  | Arts Boy         |
| **11**     | Krishnanandha P.S    | XII B | Arts Girl        |
| **12**     | Aagna Maria Sabu     | XI B  | Arts Girl        |
| **13**     | Adith Anuraj         | XII A | Discipline Boy   |
| **14**     | Geevarghese Basil    | XI A  | Discipline Boy   |
| **15**     | Annmaria Ashly       | XII B | Discipline Girl  |
| **16**     | Dilsha Nasrin        | XI B  | Discipline Girl  |

---

## Tech Stack

| Component      | Technology                                    |
|----------------|-----------------------------------------------|
| Language       | Python 3                                      |
| GUI Framework  | Tkinter (with custom ttk extensions)          |
| Image Handling | Pillow (PIL)                                  |
| Primary Database | MySQL Server (via `mysql-connector-python`)   |
| Failover Database| SQLite (`sqlite3`)                            |
| Configuration  | JSON (`start_screen_config.json`)             |
| Packaging      | PyInstaller (`.spec` specs + standalone `.exe`)|

---

## Prerequisites

Before running the scripts from source, ensure you have the following installed:

- **Python 3.8+**
- **MySQL Server** (running locally or accessible on the network)
- Required Python modules:
  ```bash
  pip install mysql-connector-python Pillow
  ```

> ⚙️ **Default MySQL Credentials:** `user=root`, `password=1234`, `host=localhost`
> If your MySQL password or host differs, adjust it on the configuration form inside the app (right-click the splash screen) or in the `start_screen_config.json` configuration file.

---

## Setup & Usage

### Step 1 — Initialize the Databases
Run this **once** on the machine to spin up the MySQL schema, candidates table, and initialize the local SQLite database:
```bash
python sqltable.py
```
This generates the tables in both the MySQL server and creates the `local_voting.db` local cache file.

### Step 2 — Run the Voting Kiosk
Start the main voter-facing kiosk terminal:
```bash
python vimalagiri.py
```
- The application will test its connection to MySQL. If MySQL is unreachable, it logs the exception to `db_error.log` and launches in **Offline Mode** using the SQLite cache.
- Click **Continue** to proceed (Right-click to modify DB connection and layout settings).
- Cast votes across the 4 election pages.
- On the confirmation screen, the **Quit** button is locked. Admin must press `u` or `U` on the keyboard to unlock it, allowing a click to loop back to the splash screen.
- **Auto-Sync:** On loop/reset back to the splash screen, the application will attempt to reconnect to MySQL and batch-upload all queued offline votes.
- Press `<Control-Shift-Q>` (or `<Control-Shift-q>`) and enter PIN `9744` to exit the application safely.

### Step 3 — View Results (Admin Only)
Run the results generator to count and tabulate the live poll results:
```bash
python result.py
```
- Click **Generate Results** to pull tallies. If MySQL is connected, it syncs first. If offline, it pulls from the local SQLite cache.
- Results are simultaneously saved to `results.csv`.

### Step 4 — Reset Votes (Optional)
To clear counts for testing or starting a fresh session:
```bash
python reset.py
```
> ⚠️ This resets all candidate votes back to `0` in both the MySQL and SQLite databases.

---

## Building Executables (PyInstaller)

To recompile the standalone `.exe` files for distribution, run:

```bash
pyinstaller vimalagiri.spec
pyinstaller result.spec
```
The compiled binaries will be outputted to the `dist/` directory.

---

## Window Resolution

The interface is optimized for **1366×768** screen displays. Running on lower/higher resolutions may shift layout alignments.

---

## Legal & License

- © 2026 EazyVote. All rights reserved.
- Developed by **Gregory Ajish** and **Lestlin Robins**.
- Unauthorized replication, modification, or distribution is prohibited.
- See the `Legal/` folder for full terms and agreements.

*Last updated: July 2026 — EazyVote v2.1-networking*
