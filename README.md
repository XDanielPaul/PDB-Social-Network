# PDB-Social-Network

# Prerequisites
Python >= 3.10 
Docker Desktop >= 4.21.1

# Package installation
- Install **poetry** python package manager with `pip install poetry`
- Once poetry is on your system, install python dependencies with `poetry install`

# Create docker containers
- If you have Docker Desktop running, build docker containers with  `docker compose up -d`

# Run the application
Option 1:
- Install [overmind](https://github.com/DarthSim/overmind) (a process manager for Procfile-based applications)
- Run `overmind s -f Procfile.dev`

Option 2:
- Run the application in 3 shell instances with:
  - `poetry run litestar --app app.controllers.command_controller:app run --port 8000`
  - `poetry run litestar --app app.controllers.query_controller:app run --port 8001`
  - `poetry run python app/message_broker/event_handler.py`
