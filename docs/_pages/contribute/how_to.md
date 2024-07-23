---
permalink: /contribute/how-to/
---

# How To Contribute

## Fork & Clone Repository

Details on this process can be found in the [GitHub Documentation](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo).

## Dependency Management: Poetry and other env/dependency managers
This project utilizes [Poetry](https://python-poetry.org/) v1.8.2+ as a dependency manager.
❗Note: *Before installing Poetry*, if you use Conda, create and activate a new Conda env (e.g. conda create -n langchain python=3.10)
* [Poetry install instructions](https://python-poetry.org/docs/#installation).

❗Note: If you use Conda or Pyenv as your environment/package manager, after installing Poetry, tell Poetry to use the virtualenv python environment (poetry config virtualenvs.prefer-active-python true)

❗Note: Please ensure that you are developing and testing in Python 3.10 to ensure compatibility. 

## Local Set Up

Install dependencies and set up precommit hooks:
```
make init
```
You must also install Graphviz if you intend to use visualization features. 
* [Graphviz install instructions](https://graphviz.org/download/)
* [Graphviz Python package documentation](https://graphviz.readthedocs.io/en/stable/manual.html#installation)

Verify that proper dependencies are installed and the project is set up properly:
```
make test_unit
```
- This will run all tests that don’t engage with the OpenAI API or require a database.

Create an `.env` file that contains the contents of `example.env`. Replace the `OPENAI_API_KEY` value with your OpenAI key if you intend to contribute to LLM dependent modules. 

## Testing

Run all tests:
```
make test
```
* This will require the OPENAI_API_KEY environment variable to be declared in the .env file.
* This will require a local instance of Neo4j running to test against. 

Run all free tests:
```
make test_free
```
* This will require a local instance of Neo4j running to test against. 

Run all unit tests:
```
make test_unit
```

Run all integration tests:
```
make test_integration
```
* This will require the OPENAI_API_KEY environment variable to be declared in the .env file.
* This will require a local instance of Neo4j running to test against. 

## Formatting

Run formatter:
```
make format
```
* This will run black formatting over the project.

Formatting will also be handled via a precommit hook.

## Documentation

Runway uses the [NumPy documentation style guide](https://numpydoc.readthedocs.io/en/latest/format.html). All public facing classes and methods should be documented in this manner. 

Documentation will be refreshed from the `main` branch upon a new release. 




