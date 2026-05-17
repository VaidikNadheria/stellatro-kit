# Stellatro.ai

![logo](/assets/qualcomm_logo.png)

Welcome to ACM AI's Spring 2026 Competition, **Stellatro.AI**! In this competition, you will build AI bots to pick winning poker hands and pick power ups to multiply scores! Compete against your peers to win a Qualcomm-sponsored Snapdragon X-Elite Laptop!

> [!IMPORTANT]
> How to get help
>
> - Discord: You can reach us on Discord in the #ai channel.
> - In person: You can find us at the back of Henry Booker Room. We'll also be walking around.

## Table of Contents

- [Repo Structure](#repo-structure)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Clone repo and create environment](#clone-repo-and-create-environment)
  - [VS Code Setup](#vs-code-setup)
- [Instructions](#instructions)
  - [Game Flow](#game-flow)
  - [Starter Bots](#starter-bots)
- [Submission and Evaluation](#submission-and-evaluation)
  - [Submission](#submission)
  - [Evaluation](#evaluation)
- [Competition Rules](#competition-rules)
- [FAQ](#faq)
- [Resources](#resources)

## Repo Structure

This repo is being refactored into three main surfaces:

| Path | Purpose |
| --- | --- |
| `stellatro-game/` | Canonical game engine, rules, and exported game-facing APIs |
| `starter-kit/` | Bot templates, built-in bots, GUI, local assets, and starter-kit tests |

Supporting package:

| Path | Purpose |
| --- | --- |
| `stellatro-common/` | Shared enums and Pydantic models used across the other surfaces |

## Installation

In this section, you'll install Git, Python, pip, and a code editor. If you already have these tools installed, you can skip to the [Clone Repo and Create Environment](#clone-repo-and-create-environment) section.

### Prerequisites

Please make sure you've installed the following tools:

- **Git**, which should already be installed on your system if you use MacOS or Linux.
If you're on Windows, you can download it from <https://git-scm.com/download/win>, or use Windows Subsystem for Linux (WSL).
- **Python 3.13** and **pip**, the standard package manager for Python.
- A code editor. We strongly recommend using [**Visual Studio Code**](https://code.visualstudio.com/download), but you can also use other code editors.

### Clone repo and create environment

To clone this repository, open your git bash or terminal and type in the following command:

```shell
git clone https://github.com/acmucsd/stellatro
cd stellatro
```

From the repo root, create and populate the shared virtual environment with Python 3.13. The GUI depends on `pygame`, and on Windows that is the version with a prebuilt wheel for this repo today.

Create environment and install required package:

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

⚠️ During the competition, if you want to install other packages, you should use pip. For example, to install numpy:

```shell
pip install numpy
```

### VS Code Setup

If you have never used Git in Visual Studio Code, read through this documentation: <https://code.visualstudio.com/docs/sourcecontrol/intro-to-git>

## Instructions

Stellatro is a two-player competitive card game inspired by Balatro, built for bot-vs-bot play. Players score points using poker hands, where each card contributes chips and the hand contributes a multiplier. Jokers are special modifiers that change how scoring works.

### Game Flow

1. **Draft phase:** players take turns selecting jokers from a shared pool to build their scoring strategy.
2. **Play phase:** each player submits their best 5-card poker hand.
3. **Scoring:** the final score is calculated from hand value, card chips, multipliers, and joker effects.
4. **Game over:** the player with the higher final score wins.

For a more detailed explanation of the game, see `starter-kit/tutorial.md`.

To find the comprehensive list of jokers, see `starter-kit/jokers.md`

### Starter Bots

The starter bots live in `starter-kit/bots/` and all expose the same two
methods: `pick_joker(state)` for drafting a joker and `pick_hand(state)` for
choosing five card indices to play.

| Bot | File | Description |
| --- | --- | --- |
| Random bot | `starter-kit/bots/random_bot.py` | Minimal baseline that always takes the first available joker and plays the first five cards. Useful as the simplest interface example. |
| Greedy bot | `starter-kit/bots/greedy_bot.py` | Tries each available joker, scores every 5-card hand with that joker, drafts the joker with the best immediate score, then plays the best-scoring hand. |
| Minimax bot | `starter-kit/bots/minimax_bot.py` | Looks ahead through the joker draft with alpha-beta minimax, estimates future score advantage, and uses exhaustive search for the final hand. |
| RL bot | `starter-kit/bots/rl/rl_bot.py` | Loads a trained checkpoint to choose jokers during the draft, then plays the exact best 5-card hand. See `starter-kit/bots/rl/README.md` for training and evaluation. |
| Participant bot selector | `starter-kit/bots/participant_bot.py` | Small switchboard that points local starter-kit tools at whichever bot class you want to test. |
| Bot interface | `starter-kit/bots/bot_interface.py` | Abstract interface documenting the required `pick_joker` and `pick_hand` methods. |
| Bot utilities | `starter-kit/bots/utils.py` | Shared helpers for converting game state models, scoring candidate hands, and measuring possible joker improvements. |

## Submission and Evaluation

### Submission

You should submit a zip file containing your final `bot.py` to the portal: <https://ai.acmucsd.com/portal>. For packaging instructions, see `starter-kit/README.md`.

### Evaluation

The competition will be in a round-robin format, which means each bot will play against each other once. The final ranking will be determined based on the total scores, where each win is +3, tie is +1, and loss is +0.

You can check <https://ai.acmucsd.com/portal> for current leaderboard.
**Please note that the submission portal will be closed at 5 pm.**

Note the follow additional clauses for evaluation:
1. We will run games in sets of four, swapping who goes first and who has which hand, to ensure evaluation fairness. 
2. Each joker pool will have at least one joker that generates stella and one joker that uses stella. This is reflected in your starter kit game logic as well.
3. For determining leaderboard winners, we will run an additional round robin evaluation with additional sets between the top eight submissions.


## Competition Rules

1. You are welcome to use any model for this competition as long as you can explain the algorithm or logic behind your solution.
2. Winners will be interviewed to discuss their approach and solution before prizes are awarded.
3. The use of LLM is permitted, but participants are responsible for reviewing and testing all submitted code.
4. Any attempt to cheat, including hacking, exploiting the evaluation server, or other dishonest behavior, will result in disqualification. We have the right of interpretation.

## FAQ

**Q: Where can I see the current leaderboard?**

**A:** You can go to <https://ai.acmucsd.com/portal> to see your submissions and the current leaderboard.

**Q: What if I have questions related to the competition?**

**A:** Go to our discord server [ACM AI @ UCSD](https://acmurl.com/ai-discord) and find the channel for stellatro-q-and-a. You can also directly reach out to our staff, but we may not help you with your solution.

## Resources

Here is some suggested algorithms to try and implement:

1. Minimax Algorithm:
    - <https://www.justinmath.com/minimax-strategy/>
    - <https://www.datacamp.com/tutorial/minimax-algorithm-for-ai-in-python>
2. Greedy: <https://www.geeksforgeeks.org/dsa/applications-advantages-and-disadvantages-of-greedy-algorithms/>
3. Alpha-beta pruning: <https://www.geeksforgeeks.org/artificial-intelligence/alpha-beta-pruning-in-adversarial-search-algorithms/>
4. Monte-Carlo Tree Search: [Wikipedia](https://en.wikipedia.org/wiki/Monte_Carlo_tree_search)
