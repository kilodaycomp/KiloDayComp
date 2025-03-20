# List all available commands
default:
    @just --list

# Install project dependencies
install:
    pip3 install -r requirements.txt

# Run the main program
run:
    python main.py

# Generate audit report for the first time
generate:
    python main.py --generate

# Update today's balance
update:
    python main.py --update

# Check code style (ignoring venv directory)
lint:
    flake8 . --exclude=venv/* --max-line-length=100
    black . --exclude=venv/* --line-length=100 --check

# Format code using black
format:
    black . --line-length=100

push:
    git pull
    git add .
    git commit -m "Update $(date +%Y-%m-%d)"
    git push