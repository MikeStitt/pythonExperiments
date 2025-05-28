import gc
import sys

from wpilib import RobotController
from timedrobotpy import TimedRobotPy
from wpilib.timedrobotpy import TimedRobotPy
from wpilib import TimedRobot

_getFPGATime = RobotController.getFPGATime

microsecondsAsInt = int

PRINT_ENTRY_EXIT = False
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
USE_TIMEDROBOT = False
if USE_TIMEDROBOT:
    RobotParentClass = TimedRobot

NUM_TEST_PERIODIC = 2
NUM_PERIODS = 1000

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
        print(f"commonCallCount={commonCallCount}")
        for name, value in self._callTimesUs.items():
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
        print(f"robotInit Done RobotParentClass={RobotParentClass.__name__}")
        if not USE_TIMEDROBOT:
            print(f"self._callbacks={type(self._callbacks).__name__}")
        #gc.freeze()
        #gc.disable()



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

