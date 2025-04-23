from wpilib import IterativeRobotBase
import hal

from hal import initializeNotifier, setNotifierName, observeUserProgramStarting, updateNotifierAlarm, \
    waitForNotifierAlarm
from wpilib import RobotController


class ExpTimedRobotPy(IterativeRobotBase):

    def __init__(self, periodS: float = 0.020):  # todo are the units on period correct?
        super().__init__(periodS)


    def startCompetition(self) -> None:
        self.robotInit()

        if self.isSimulation():
            self._simulationInit()

        # Tell the DS that the robot is ready to be enabled
        print("********** Robot program startup complete **********")
        observeUserProgramStarting()

        startTime = RobotController.getFPGATime()

        status1 = 0
        status2 = 0
        status3 = 0
        status4 = 0

        self.notifier, status1 = initializeNotifier()

        status2 = setNotifierName(self.notifier, "TimedRobot")

        status3 = updateNotifierAlarm(self.notifier, startTime+100000)

        now_us, status4 = waitForNotifierAlarm(self.notifier)

        endTime = RobotController.getFPGATime()

        print(f"HAL_InitializeNotifier  : Notifier: {self.notifier} status=0x{status1&0xFFFFFFFF :08x}")
        print(f"HAL_SetNotifierName     : Notifier: {self.notifier} status=0x{status2&0xFFFFFFFF :08x}")
        print(f"HAL_UpdateNotifierAlarm : Notifier: {self.notifier} status=0x{status3&0xFFFFFFFF :08x}")
        print(f"HAL_WaitForNotifierAlarm: Notifier: {self.notifier} status=0x{status4&0xFFFFFFFF :08x}")
        print(f"GetFPGATime: startTime={startTime} now_us={now_us} endTime={endTime}")

    def endCompetition(self):
        hal.stopNotifier(self.notifier)
