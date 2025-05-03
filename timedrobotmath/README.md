# timedrobotgmath

experiment to use robotpy-build to call some c++ math from python

See https://github.com/robotpy/robotpy-build

See https://github.com/MikeStitt/mostrobotpy/blob/pyIterativeAndTimedRobot/subprojects/robotpy-wpilib/wpilib/timedrobotpy.py#L79

# to run

```
python3 -m venv .venvTimedrobotmath; . .venvTimedrobotmath/bin/activate; pip install --upgrade pip ; python -m pip install -e .
```


```
python -c "import timedrobotmath; print(f'l={timedrobotmath.getSizeOfLong()}'); print(f'n={timedrobotmath.cppCalcFutureExpirationUs(0, 100, 1000, 100)}')"
```

results in:
```
l=8
n=1100
```
