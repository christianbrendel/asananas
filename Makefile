.PHONY: all format-code check-docstrings 

all: format-code check-docstrings

format-code:
		pre-commit install
		isort asananas
		black asananas

check-docstrings:
		pydocstyle --explain asananas