#!/bin/bash

echo "running PEP8 verification..."
pycodestyle --max-line-length=120 --statistics --count --exclude=.git,./.venv/ --ignore=E402,E741 . || exit 1

exit;
