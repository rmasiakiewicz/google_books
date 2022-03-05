#!/usr/bin/env bash

BASEDIR=$(git rev-parse --show-toplevel)

ln -s -f ../../scripts/pre-push.sh ${BASEDIR}/.git/hooks/pre-push