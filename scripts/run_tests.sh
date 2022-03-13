#!/bin/bash

BASEDIR=$(git rev-parse --show-toplevel)

python -m unittest discover ${BASEDIR}/tests
