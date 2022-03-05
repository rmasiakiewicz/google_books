#!/bin/bash

BASEDIR=$(git rev-parse --show-toplevel)

black $BASEDIR || exit 1

exit;
