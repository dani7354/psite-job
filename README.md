# psite-job

## Install
TODO...


## Development setup
Installing dependencies and setting up a virtual environment for development:
```
python3 -m venv venv/
source venv/bin/activate
python -m pip install -r pylock.dev.toml && python -m pip install --no-deps ".[dev]"
```

Regenerate pylock.toml after adding new dependencies:
```
python -m pip lock --output pylock.dev.toml --only-deps '.[dev]'
python -m pip lock --output pylock.toml --only-deps .