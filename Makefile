.PHONY: smoke-test test smoke clean-fixtures

PYTHON ?= python

smoke-test:
	PYTHONPATH=src $(PYTHON) -m pytest -q
	PYTHONPATH=src $(PYTHON) -m moltrustbench.smoke --allow-fallback-standardizer

test:
	PYTHONPATH=src $(PYTHON) -m pytest -q

smoke:
	PYTHONPATH=src $(PYTHON) -m moltrustbench.smoke --allow-fallback-standardizer

clean-fixtures:
	PYTHONPATH=src $(PYTHON) -m moltrustbench.smoke --clean
