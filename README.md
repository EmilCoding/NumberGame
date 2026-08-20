# The Number Game

- What is it

## What is its purpose?

The purpose it mostly to show of my Python skills.
- Object-oriented Programming (OOP).
- Testing using pytest.
- Automation.
- Data- and mathematical analysis.

## How its build?
<!-- ```mermaid
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
``` -->
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

## How to install

### Prerequisites

- Python 3.10 or newer
- Git

Clone the repository and move into the project directory. Replace `<repository-url>` with the URL of this repository:

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

## The bots
...

## Performance analysis of bots
...