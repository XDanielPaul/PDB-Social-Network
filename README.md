# PDB-Social-Network

<img src="https://github.com/XDanielPaul/PDB-Social-Network/assets/47739921/2f7b46f7-bded-4b76-b6a1-7dfdb683b304" alt="PDBlogo" width="400px" height="400px">

This is an implementation of a project made for Advanced Database Systems course. It is a Social Network, where you can read, create, share, rate posts, follow users and comment to share your ideas.

Authors:

-   Daniel Paul (xpauld00@stud.fit.vutbr.cz)
-   Tomáš Křivánek (xkriva29@stud.fit.vutbr.cz)

# Project structure

```
.
├── app/
│   ├── controllers/ (contains controllers for API endpoints)
│   │   ├── command/ (contains controllers for POST, PUT, DELETE requests)
│   │   │   ├── __init__.py
│   │   │   ├── CommentController.py
│   │   │   ├── EventController.py
│   │   │   ├── PostController.py
│   │   │   └── UserController.py
│   │   ├── query/ (contains controllers for GET requests)
│   │   │   ├── __init__.py
│   │   │   ├── CommentController.py
│   │   │   ├── EventController.py
│   │   │   ├── PostController.py
│   │   │   └── UserController.py
│   │   ├── __init__.py
│   │   ├── command_controller.py (contains all command controllers)
│   │   └── query_controller.py (contains all query controllers)
│   ├── message_broker/
│   │   └── event_handler.py (contains event handler for RabbitMQ -> Synchronization of Source of Truth [PostgreSQL] and Materialized View [MongoDB])
│   ├── models/ (contains SQLAlchemy models and seeding functions)
│   │   ├── example_data/
│   │   │   └── users.json
│   │   ├── __init__.py
│   │   ├── base_for_modelling.py
│   │   ├── comment_model.py
│   │   ├── event_model.py
│   │   ├── like_dislike_model.py
│   │   ├── populize_functions.py
│   │   ├── post_model.py
│   │   ├── tag_model.py
│   │   └── user_model.py
│   └── utils/ (contains utilities for API)
│       ├── mongo/
│       │   ├── collections.py (contains Collection class for MongoDB)
│       │   ├── custom_methods.py (contains custom handlers for RabbitMQ messages)
│       │   └── mongo_connect.py
│       ├── pika.py (contains RabbitMQ connection and queues)
│       └── query.py (contains expand methods for MongoDB)
├── tests/ (contains tests for API)
│   ├── conftest.py
│   ├── test_comments.py
│   ├── test_events.py
│   ├── test_posts.py
│   └── test_users.py
├── .pre-commit-config.yaml (contains pre-commit hooks)
├── CHANGELOG.md
├── docker-compose.yml (contains docker-compose configuration)
├── LICENSE
├── poetry.lock (contains poetry dependencies)
├── populize.py (script for generating dummy data in database)
├── Procfile.dev (contains Procfile for overmind process manager)
├── pyproject.toml (contains poetry configuration)
└── README.md (this file)
```

# Prerequisites

Python >= 3.10

Docker Desktop >= 4.21.1

# Package installation

-   Install **poetry** python package manager with `pip install poetry`
-   Once poetry is on your system, install python dependencies with `poetry install`

# Create docker containers

-   If you have Docker Desktop running, build docker containers with `docker compose up -d`

# Run the application

Option 1:

-   Install [overmind](https://github.com/DarthSim/overmind) (a process manager for Procfile-based applications)
-   Run `overmind s -f Procfile.dev`

Option 2:

-   Run the application in 3 shell instances with:
    -   `poetry run litestar --app app.controllers.command_controller:app run --port 8000 --reload`
    -   `poetry run litestar --app app.controllers.query_controller:app run --port 8001 --reload`
    -   `poetry run python app/message_broker/event_handler.py`
-   For generating database data use:
    -   `poetry run python .\populize.py`

# Pre-commit hooks

Before you commit, you need to run pre-commit to ensure that your code is formatted correctly and that you have no linting errors. To do this, run `pre-commit` in the root directory of the project. If you have any errors, you will need to fix them before you can commit.

# Testing with pytest

For testing you have to have dependencies installed and docker containers running.
Secondly you need to clear your MongoDB database and run `poetry run python populize.py` to populate your database with dummy data.
Lastly you need to run the application (see **Run the application** section).

You can run tests in 2 ways:

1. Run tests in VSCode (this way you can also debug tests)
    1. Select poetry shell python interpreter in VSCode
        1. `CTRL + SHIFT + P`
        2. `Python: Select Interpreter`
        3. `pdb-social-network-...`, `Poetry`
    2. You can click on the **run and debug** icon (`CTRL+SHIFT+D`) in VSCode and run test discovery
2. Run tests in the terminal with `poetry run pytest`

# Debugging API

You can debug the API on routes:

-   `/schema` (for [ReDoc](https://redocly.com/redoc))
-   `/schema/swagger` (for [Swagger UI](https://swagger.io/))
-   `/schema/elements` (for [Stoplight Elements](https://stoplight.io/open-source/elements/))
