# tryRobotPyBuildEditable

steps:

```
git clone git@github.com:MikeStitt/pythonExperiments.git 
cd pythonExperiment/tryRobotPyBuildEditable
```

If there is already a python venv active:

```
deactivate
```

Make a new venv, activate it, install trpbe as editable in the venv

```
python3 -m venv .venvRobotPyBuildEditable
. ./.venvRobotPyBuildEditable/bin/activate
pip install -e .
```

Try trpbe:

```
trpbe --help
```

interesting commands

```
pushd mostrobotpy
set -e
for i in {1..100}; do
pytest -vvvv --no-header -s subprojects/robotpy-wpilib/tests/test_poc_timedrobot.py
done
popd

```