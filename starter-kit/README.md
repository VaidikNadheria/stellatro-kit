# Starter Kit

This folder contains the starter surface for building and testing bots locally.

## Contents

- `bots/` built-in bot implementations and examples
- `tutorial.md` beginner-friendly participant tutorial
- `gui/` the local Pygame interface
- `assets/` art, fonts, and UI assets used by the GUI
- `jokers.md` participant-friendly joker lookup by name, description, and phase
- `submission_folder/` copy-ready bot template for final submissions
- `scripts/` local command-line helpers
- `tests/` starter-kit level tests

If you are not sure where to begin, start with `tutorial.md`.

## Setup

From the repo root, create and populate the shared virtual environment with
Python 3.13. The GUI depends on `pygame`, and on Windows that is the version
with a prebuilt wheel for this repo today.

On Windows PowerShell:

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

On macOS or Linux:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

After that, just reactivate `.venv` whenever you want to work on Stellatro.

## Typical Commands

Run these from the repo root after activating `.venv`.

On macOS or Linux, the commands below are the same after activation. If you
prefer not to activate the environment, replace `python` with `.venv/bin/python`.

Run the GUI:

```powershell
python starter-kit/gui/gui.py
```

Run the text shell:

```powershell
python starter-kit/scripts/shell.py
```

Run the starter-kit tests:

```powershell
python -m pytest starter-kit/tests
```

Run a local bot-vs-bot simulation:

```powershell
python starter-kit/scripts/run_bot_match.py minimax random --rounds 3
```

Benchmark draft-call speed for a bot on random draft states:

```powershell
python starter-kit/scripts/benchmark_draft_call.py greedy --trials 20
```

List the built-in bot aliases:

```powershell
python starter-kit/scripts/run_bot_match.py --list-bots
```

(Reinforcement-learning training components were removed from this
starter kit. If you plan to add RL training scripts, place them under
`starter-kit/bots/rl/` and document them here.)

Package a submission zip:

```powershell
python starter-kit/scripts/zip_submission.py my_bot_name
```

The zip is written to `starter-kit/submission_zips/` and contains the contents
of `starter-kit/submission_folder/` at the zip root.

The tournament loader expects the zip to contain a `bot.py` file defining a
`Bot` class with:

```python
def pick_joker(self, state) -> int:
    ...

def pick_hand(self, state) -> list[int]:
    ...
```

Name the zip file with your team name, then upload it to
<https://ai.acmucsd.com/portal>.

`starter-kit` now consumes `stellatro-game` directly. New engine changes should land in `stellatro-game/`.
