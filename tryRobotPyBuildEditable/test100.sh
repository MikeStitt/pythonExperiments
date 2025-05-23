#!/bin/bash
set -e
pushd mostrobotpy
set -e
for i in {1..100}; do
pytest -vvvv --no-header -s subprojects/robotpy-wpilib/tests/test_poc_timedrobot.py
done
popd