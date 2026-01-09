[![Pylint](https://github.com/Chelsea-Fox/gotchi-game/actions/workflows/pylint.yml/badge.svg)](https://github.com/Chelsea-Fox/gotchi-game/actions/workflows/pylint.yml)
# Gotchi

Gotchi, a tamagotchi inspired game in the browser.

## Authors

- [@Chelsea-Fox](https://www.github.com/Chelsea-Fox)

## Tech Stack

**Client:** HTML5, CSS, Javascript

**Server:** Python 3.13, Flask

## Running Dev Environment

- Init db `flask --app gotchi init-db`
- Run `flask --app gotchi run --debug --no-reload`
- Test `pytest`
- Test Coverage `coverage run -m pytest`
- Coverage reports:
  - `coverage report`
  - `coverage html`

## Build and Deploy from Source

- Build
  - `pip install build`
  - `python -m build --wheel`
- Install `pip install flaskr-1.0.0-py3-none-any.whl` (replace this with output of prior)
- Init db `flask --app gotchi init-db`
- Config Secret Key `python -c 'import secrets; print(secrets.token_hex())'` (save the output)
- Create `config.py` in the instance folder and add the secret key `SECRET_KEY = <PutYourKeyHere>`
- Run With Waitress WSGI
  - `pip install waitress`
  - `waitress-serve --call 'gotchi:create_app'`
