# The Number Game
<!-- TODO: Write The Player UI -->
<!-- TODO: Write TESTING -->

This is a small game engine for a simple game where one has to guess a number between 1 and a large number like 1000. The purpose it mostly to show of my Python skills.
- ⚙️ Object-oriented Programming - See [How it is build?](#how-it-is-build)
- 🛡️ Testing using pytest.
- 🤖 Automation - See [The bots](#the-bots)
- 📊 Data- and mathematical analysis - See [Performnace analysis](PerformanceAnalysis.ipynb)

I have build the game engine using Python object and tested it using the `pytest` framework. In addition everything is typed and `flake8`, `mypy`, and `complexipy` has been used to comply with the [PEP 8 style guide](https://peps.python.org/pep-0008/).

I have then tested the performance of different guessing strategies by implementing them as `Bots`. Each strategy has been analysed mathematically and experimentally. For more details, please see the document [Performnace analysis](PerformanceAnalysis.ipynb)

## Table-of-Content

- [The Number Game](#the-number-game)
  - [Table-of-Content](#table-of-content)
  - [How it is build?](#how-it-is-build)
    - [Overview](#overview)
    - [The Player UI](#the-player-ui)
    - [The bots](#the-bots)
  - [How to install](#how-to-install)
    - [Prerequisites](#prerequisites)
    - [Start the game](#start-the-game)
    - [Testing](#testing)

## How it is build?

### Overview
```mermaid
---
title: Class diagram of the Game Engine
---
classDiagram
    Game <.. UI
    UI <|-- PlayerUI
    UI <|-- BotUI

    class Game {
        ui: UI
        max_attempts: int
        max_questions: int
        max_userinput_attempts: int
        +run()
    }

    class UI {
        +max_target: int
        +restart(max_target: int) None
        *get_guess(prompt: str) int | str
        *provide_feedback(Signal, prompt: str) None
        *echo(message: str) None
    }

    class PlayerUI {
        +restart(max_target: int) None
        +get_guess(prompt: str) int | str
        +provide_feedback(Signal, prompt: str) None
        +echo(message: str) None
    }

    class BotUI {
        +restart(max_target: int) None
        +get_guess(prompt: str) int
        +provide_feedback(Signal, prompt: str) None
        +echo(message: str) None
    }
```
The Game Engine is fundamentally build around the `Game` class. This class takes a User Interface `UI` on construction which is an adapter between a Player and the game. This User Interface is an abstract class that defines four abstract methods:
- `restart: (maximum_target: int) -> None` which resert all internal parameters in the `UI` before a game as well as providing the player with the maximum-target value.
- `get_guess: (prompt: str) -> int | str` which asks the player for a guess as either a string or an integer.
- `provide_feedback: (Signal, prompt: str) -> None` which sends the player a feedback signal. These signals included `GUESS_TOO_LOW`, `GUESS_TOO_HIGH` and `CORRECT_GUESS` in addition with other technical signals.
- `echo: (message: str) -> None` prompts a message to the user.

These methods are classed by the gameto communicate between the player and the game engine. Rendering, communicating to the user, etc. is handled by the implementation of `UI` subclasses. 

There are two general types of `UI` subclasses being
- `PlayerUI` - Defines an interface that human players can use.
- `BotUI` - Defines an interface that bots can use.

From the games point of view, the two classes are equivalent. 

### The Player UI

...



### The bots

```mermaid
---
title: Overview of the bots
---
classDiagram
    class BotUI {
        +restart(max_target: int) None
        +get_guess(prompt: str) int
        +provide_feedback(Signal, prompt: str) None
        +echo(message: str) None
    }

    BotUI <|-- RandoBot
    BotUI <|-- LinearSearchBot
    BotUI <|-- BinarySearchBot
    BotUI <|-- RandoBotWithMemory
    BotUI <|-- CheatBot
```
There are currently five types of bots in the project. These are:
- 🎲 `RandoBot` : Not the smartest bot in the world. Simply makes a guess from the available numbers. It has no memory, so it usually guesses the same number multiple times.
- 🧠 `RandoBotWithMemory` : Guesses a random number, but remembers what it has guessed before.
- 📏 `LinearSearchBot` : Starts from 1 it guesses all numbers in sequence until it guesses correctly.
- `🪚 BinarySearchBot` : Used a binary search stragety go guess the number is very few guesses.
- 😏 `CheatBot` : Always guesses correct. It uses a loophole in the code, which I left in for fun. 

If you are curious, you can read the performance analysis of the bots [here](PerformanceAnalysis.ipynb)

## How to install

### Prerequisites

- Python 3.12 or newer
- Git

Clone the repository and move into the project directory.

```powershell
git clone "https://github.com/EmilCoding/NumberGame"
cd NumberGame
```

Create and activate a virtual environment. In PowerShell, run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script, use Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

Install the dependencies and the package in editable mode:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install --editable .
```

### Start the game

```powershell
python -m numbergame
```

### Testing

The project can be automatically tested by running pytest in the terminal
```powershell
pytest
```

In addition, typing inconsistencies can be checked with `mypy` 
```powershell
mypy .\src\
```

Also, styling inconsistencies can be checked with `flake8`  
```powershell
flake8
```

If you want to go the extra mile `complexipy` can be used to check the complexity of each function.
```powershell
complexipy .\src\ 
```
