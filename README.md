# Shopping Manager API
This is an API that manages shopping lists.  
Users have to create stores they frequent and articles (and how much they cost) themselves before adding them to shopping lists as items.  
Shopping lists calculate their costs using article prices of the last time the specific list was updated.

## Installation

First, set up a virtual environment using:

    python3 -m venv .venv

On macOS and Linux, run:

    . .venv/bin/activate

On Windows, run:

    .\.venv\Scripts\activate

To activate your virtual environment.

Next, to install required packages run:

    pip install -r requirements.txt

## Setup
Create a `.env` file and set the following environment variables:
- `DATABASE_URL = "mysql+mysqldb://<username>:<password>@<database host>/<database name>"`
  
- `CREATE_DATABASE = true`
  If set to true, the database tables will be created on startup.

- `SALT`
  Random value used to salt user passwords before hashing

- `SECRET_KEY`
  HS256 key used to encode JWT tokens.

## Execution

To execute, first activate your virtual environment (see above).

Then run:

    uvicorn app.main:app --reload

The Shopping Manager API is now running under http://localhost:8000