// Copyright (c) FIRST and other WPILib contributors.
// Open Source Software; you can modify and/or share it under the terms of
// the WPILib BSD license file in the root directory of this project.

#include "ExpTimedRobot.h"

#include <stdint.h>
#include <inttypes.h>

#include <cstdio>
#include <utility>

#include <hal/DriverStation.h>
#include <hal/FRCUsageReporting.h>
#include <hal/Notifier.h>

#include "frc/Errors.h"

using namespace frc;

void ExpTimedRobot::StartCompetition() {
  RobotInit();

  if constexpr (IsSimulation()) {
    SimulationInit();
  }

  // Tell the DS that the robot is ready to be enabled
  std::puts("\n********** Robot program startup complete **********");
  HAL_ObserveUserProgramStarting();


  auto startTime = frc::RobotController::GetFPGATime();
  
  int32_t status1 = 0;
  HAL_NotifierHandle m_notifier = HAL_InitializeNotifier(&status1);
  int32_t status2 = 0;
  HAL_SetNotifierName(m_notifier, "TimedRobot", &status2);

  int32_t status3 = 0;
  HAL_UpdateNotifierAlarm(m_notifier, startTime+100000, &status3);
  int32_t status4 = 0;
  auto now_us = HAL_WaitForNotifierAlarm(m_notifier, &status4);

  auto endTime = frc::RobotController::GetFPGATime();

  printf("HAL_InitializeNotifier  : Notifier: %d status=%x\n", (int)m_notifier, status1);
  printf("HAL_SetNotifierName     : Notifier: %d status=%x\n", (int)m_notifier, status2);
  printf("HAL_UpdateNotifierAlarm : Notifier: %d status=%x\n", (int)m_notifier, status3);
  printf("HAL_WaitForNotifierAlarm: Notifier: %d status=%x\n", (int)m_notifier, status4);

  FRC_CheckErrorStatus(status1, "InitializeNotifier");
  FRC_CheckErrorStatus(status3, "UpdateNotifierAlarm");

  printf("GetFPGATime: startTime=%" PRIu64 " now_us=%" PRIu64 " endTime=%" PRIu64 "\n", startTime, now_us, endTime);


}

void ExpTimedRobot::EndCompetition() {
}

ExpTimedRobot::ExpTimedRobot(units::second_t period) : IterativeRobotBase(period) {
}

ExpTimedRobot::~ExpTimedRobot() {
}
