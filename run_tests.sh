#!/bin/bash

uv run coverage run -m pytest
uv run coverage report
uv run coverage html

echo -e "HTML coverage report available in htmlcov/ directory."
