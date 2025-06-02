#!/bin/bash

dirname=$(dirname "$0")

source $dirname/.venv/bin/activate
python main.py

$SHELL