# PDB-Social-Network

# Project structure
.
├── app/
│   ├── controllers/ (contains the controllers for the command and query side)
│   │   ├── command_controller.py
│   │   └── query_controller.py
│   ├── message_broker/ (contains the event handler for the message broker)
│   │   └── event_handler.py
│   ├── models/ (contains the models for the command and query side)
│   │   ├── controller_model.py
│   │   └── query_model.py
│   └── utils/ (contains the utils for the command, query and message broker)
│       ├── controller.py
│       ├── pika.py
│       └── query.py
└── tests (contains tests)

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

# Pre-commit hooks
Before you commit, you need to run pre-commit to ensure that your code is formatted correctly and that you have no linting errors. To do this, run `pre-commit` in the root directory of the project. If you have any errors, you will need to fix them before you can commit.

# Testing
For testing you have to have dependencies installed.

You can run tests in 2 ways:
1. Run tests in VSCode (this way you can also debug tests)
   1. Select poetry shell python interpreter in VSCode
      1. `CTRL + SHIFT + P`
      2. `Python: Select Interpreter`
      3. `pdb-social-network-...`,  `Poetry`
   2. You can click on the **run and debug** icon in VSCode and run test discovery
2. Run tests in the terminal with `poetry run pytest`
