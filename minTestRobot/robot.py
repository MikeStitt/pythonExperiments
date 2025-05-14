import sys
import wpilib

from wpilib import RobotController

def printEntryAndExit(func):
    def wrapper(*args, **kwargs):
        #name = inspect.currentframe().f_code.co_name
        name = func.__name__
        print(f"{RobotController.getFPGATime()/1000_000.0:.3f}:Enter:{name}")
        result = func(*args, **kwargs)
        print(f"{RobotController.getFPGATime()/1000_000.0:.3f}:Exit :{name}")
        return result
    return wrapper

class MyRobot(wpilib.TimedRobot):

    @printEntryAndExit
    def startCompetition(self):
        super().startCompetition()

    @printEntryAndExit
    def endCompetition(self):
        super().endCompetition()

    @printEntryAndExit
    def robotInit(self):
        pass

    @printEntryAndExit
    def robotPeriodic(self):
        pass

    @printEntryAndExit
    def autonomousInit(self):
        pass

    @printEntryAndExit
    def autonomousPeriodic(self):
        pass

    @printEntryAndExit
    def autonomousExit(self):
        pass

    @printEntryAndExit
    def disabledInit(self):
        pass

    @printEntryAndExit
    def disabledPeriodic(self):
        pass

    @printEntryAndExit
    def disabledExit(self):
        pass

    @printEntryAndExit
    def _simulationInit(self):
        pass

    @printEntryAndExit
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

