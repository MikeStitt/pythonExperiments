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

```

```