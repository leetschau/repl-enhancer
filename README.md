# REPL Enhancer

Verwandeln Sie jede einfache Konsole in ein schickes REPL.

# Usage

Put the executable into $PATH and run: `repl -h`.

# Deployment

```sh
poetry install
poetry run pyinstaller --onefile --strip repl.py
```
