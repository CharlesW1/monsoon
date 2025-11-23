![monsoon_wordmark](https://user-images.githubusercontent.com/87099578/193130174-e464d4a6-afa3-453f-a36e-4289acf5f248.png)

# 🌀 Monsoon
Monsoon is a lightweight overlay solution for your League client that shows 
ARAM balance changes in champion select. Let the winds reveal the unexpected 
surprises before the match begins! :3

# Table of Contents
- [🌀 Monsoon](#-monsoon)
- [Table of Contents](#table-of-contents)
- [Download](#download)
- [Guide](#guide)
  - [Getting started](#getting-started)
- [Limitations](#limitations)
- [FAQ](#faq)
- [Legal](#legal)
- [License](#license)

# Download
Interested in using Monsoon? Download the releases from this fork:
[Get it here!](https://github.com/CharlesW1/monsoon/releases) :hype_kitty:

# Guide
## Getting started
<TODO Showcase section>

## Quick start (from source code)

If you'd like to run Monsoon from source, a helper script is included to set up a
Python virtual environment, install dependencies and optionally run the app.

- Just navigate to the script directory, make the script executable (on Unix-like shells), and run it:

```bash
cd ./scripts
chmod +x ./quick_start.sh
./quick_start.sh
```

- On Windows PowerShell or cmd, follow the printed activation instructions from
  the script, or run the setup steps manually:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # PowerShell
# or: .\.venv\Scripts\activate.bat  # cmd.exe
pip install -r .\requirements.txt
python .\src\monsoon.py
```

Notes:
- The helper prefers a `.venv` directory and will use an existing `.venv` or
  `env` if present
- The script checks for Python >= 3.10. If you don't have a suitable Python
  installed it will print instructions on where to get one

# FAQ
**How was Monsoon made?**

I forked this repo from BlossomiShymae and added in winrate data from LoLalytics.

**Does Monsoon support Mac (or even Linux with Wine)?**

Due to the nature of pywin32, Monsoon cannot currently support Mac or Linux. 
I also do not own an Apple-based computer, so I cannot approve any changes made 
to support said platform.

Support for Linux with Wine will also never be supported as Riot does not 
support the platform with the game anyways.

I am very sorry... :c

# Legal
Monsoon isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games, and all associated properties are trademarks or registered trademarks of Riot Games, Inc.

# License
Monsoon is licensed under the terms of the GNU GPL v3 license.
