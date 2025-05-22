import gc
import sys

from wpilib import RobotController
from wpilib.timedrobotpy import TimedRobotPy
from wpilib import TimedRobot

import os

def isEnvVarTrue(var_name):
    """
    Checks if an environment variable exists and evaluates to True.

    Args:
        var_name: The name of the environment variable.

    Returns:
        True if the variable exists and is considered true, False otherwise.
    """
    var_value = os.environ.get(var_name)

    if var_value is None:
        return False  # Variable does not exist

    true_values = ['true', '1', 'yes', 'y']
    return var_value.lower() in true_values

_getFPGATime = RobotController.getFPGATime

microsecondsAsInt = int

PRINT_ENTRY_EXIT = isEnvVarTrue('MINTESTROBOT_PRINT_ENTRY_EXIT')
if PRINT_ENTRY_EXIT:
    def printEntry(name, startTimeUs:microsecondsAsInt):
        print(f"{startTimeUs/1000_000.0:.6f}:Enter:{name}")

    def printExit(name):
        print(f"{_getFPGATime()/1000_000.0:.6f}:Exit :{name}")
else:
    def printEntry(name, startTimeUs):
        pass
    def printExit(name):
        pass


def printEntryAndExit(func):
    def wrapper(*args, **kwargs):
        name = args[1]
        startTimeUs = _getFPGATime()
        args[0].addCallLog(name,startTimeUs)
        printEntry(name, startTimeUs)
        result = func(*args, **kwargs)
        printExit(name)
        return result
    return wrapper

RobotParentClass = TimedRobotPy
if isEnvVarTrue('MINTESTROBOT_USE_TIMEDRROBOT'):
    RobotParentClass = TimedRobot




NUM_TEST_PERIODIC = 10
NUM_PERIODS = 100

class MyRobot(RobotParentClass):

    def addCallLog(self, name, timeUs):
        if self._callCount[name] < NUM_PERIODS:
            self._callTimesUs[name] += timeUs
            self._callCount[name] +=1

    @printEntryAndExit
    def testPeriodic(self,name):
        if PRINT_ENTRY_EXIT:
            print(f"testPeriodic({name})")
        pass

    def startCompetition(self):
        super().startCompetition()

    def endCompetition(self):
        super().endCompetition()
        avgDeltaCallTimesUs = {}
        commonCallCount = self._callCount['loopStartTime']
        for name, value in self._callTimesUs.items():
            print(f"commonCallCount={commonCallCount}=self._callCount[{name}]={self._callCount[name]}")
            assert commonCallCount == self._callCount[name]
            avgDeltaCallTimesUs[name] = (self._callTimesUs[name]-self._callTimesUs['loopStartTime'])/self._callCount[name]
            print(f'avgDeltaCallTimesUs[{name}]={avgDeltaCallTimesUs[name]}')

    def robotInit(self):
        self.count = 0
        self._callTimesUs = {}
        self._callCount = {}
        self._callTimesUs['loopStartTime'] = 0
        self._callTimesUs['disabledPeriodic'] = 0
        self._callTimesUs['robotPeriodic'] = 0
        self._callCount['loopStartTime'] = 0
        self._callCount['disabledPeriodic'] = 0
        self._callCount['robotPeriodic'] = 0
        for i in range(NUM_TEST_PERIODIC):
            name = f"{i}"
            self.addPeriodic(lambda current_name=name: self.testPeriodic(f"{current_name}"),
                             0.020, 0.000_001+0.000_001*i)
            self._callTimesUs[name] = 0
            self._callCount[name] = 0
        gc.freeze()
        gc.disable()



    @printEntryAndExit
    def robotPeriodicBody(self, name):
        self.count += 1
        self.addCallLog('loopStartTime',self.getLoopStartTime())
        if self.count > NUM_PERIODS:
            self.endCompetition()

    def robotPeriodic(self):
        self.robotPeriodicBody('robotPeriodic')

    def autonomousInit(self):
        pass

    def autonomousPeriodic(self):
        pass

    def autonomousExit(self):
        pass

    def disabledInit(self):
        pass

    @printEntryAndExit
    def disabledPeriodicBody(self, name):
        pass

    def disabledPeriodic(self):
        self.disabledPeriodicBody('disabledPeriodic')

    def disabledExit(self):
        pass

    def _simulationInit(self):
        pass

    def _simulationPeriodic(self):
        pass

def remoteRIODebugSupport():
    if __debug__ and "run" in sys.argv:
        print("Starting Remote Debug Support....")
        try:
            import debugpy  # pylint: disable=import-outside-toplevel
        except ModuleNotFoundError:
            pass
        else:
            debugpy.listen(("0.0.0.0", 5678))
            debugpy.wait_for_client()

