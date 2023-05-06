# Doc-Search Backend
The Doc-Search backend is a REST API application that allows users to upload documents and search for documents that match a specified query. The application is built using Python and FastAPI, and uses Elasticsearch as the search engine.

## Installation
To install the necessary dependencies for the Doc-Search backend, run:

```
pip install -r requirements.txt
```

## Application Configuration
The Doc-Search backend uses environment-specific settings to configure the application. By default, the application runs in development mode, but you can switch to production mode by setting the `APP_ENV` environment variable to `production`.

The settings files are located in the `app/settings` directory, and include:

* `base.py`: The base settings class that defines the required settings.
* `development.py`: The development environment settings.
* `production.py`: The production environment settings.

The application also uses a `.env` file to load environment variables. An example `.env` file is provided, but you should create your own for your specific configuration.

## Application Usage
To start the Doc-Search backend locally, run:

```
uvicorn app.main:app --reload
```

This will start the application in development mode and automatically reload the server when changes are made.

The API endpoints are:

* `GET /v1/documents/`: Get a list of all documents uploaded to the application.
* `POST /v1/documents/`: Upload a new document to the application.
* `GET /v1/documents/search/{query}`: Search for documents that match the specified query.

## Diagrams-as-Code Configuration
* Install Graphviz: If you have not installed Graphviz yet, download and install it from the official website (https://graphviz.org/download/). Make sure to add the installation directory to your system's PATH.
* Add Graphviz to your PATH: If you have already installed Graphviz but it is not added to your system's PATH, you can add it manually. To do this, open a command prompt and type set PATH=%PATH%;C:\path\to\graphviz\bin, replacing C:\path\to\graphviz\bin with the actual path to the Graphviz bin directory.

## Diagrams-as-Code Usage
To generate the diagrams:

* Go to the `diagrams` directory.
* Run `python {diagram_name}.py`, replacing `{diagram_name}` with the name of the diagram you want to generate. For example:
```
python high_level_architecture.py
```
* The diagram will be generated in the `diagrams\generated_diagrams` directory.

## Files
* `app`: The main application directory containing the FastAPI application, routes, models, utilities, and other modules.
* `diagrams`: The directory containing Diagram-as-Code diagrams for the Doc-Search backend.
* `.env`: The environment variable file containing the configuration settings.
* `config.py`: The configuration file that loads the appropriate settings based on the current environment.
* `main.py`: The main application entry point.
* `requirements.txt`: The list of required Python dependencies.
* `README.md`: The README file for the Doc-Search backend.
* `.gitignore`: The list of files and directories to ignore in Git.
