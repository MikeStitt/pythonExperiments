// Copyright (c) FIRST and other WPILib contributors.
// Open Source Software; you can modify and/or share it under the terms of
// the WPILib BSD license file in the root directory of this project.

#pragma once

#include <chrono>
#include <functional>
#include <utility>
#include <vector>

#include <hal/Notifier.h>
#include <hal/Types.h>
#include <units/math.h>
#include <units/time.h>
#include <wpi/priority_queue.h>

#include "frc/IterativeRobotBase.h"
#include "frc/RobotController.h"

namespace frc {

/**
 * TimedRobot implements the IterativeRobotBase robot program framework.
 *
 * The TimedRobot class is intended to be subclassed by a user creating a
 * robot program.
 *
 * Periodic() functions from the base class are called on an interval by a
 * Notifier instance.
 */
class ExpTimedRobot : public IterativeRobotBase {
 public:
  /// Default loop period.
  static constexpr auto kDefaultPeriod = 20_ms;

  /**
   * Provide an alternate "main loop" via StartCompetition().
   */
  void StartCompetition() override;

  /**
   * Ends the main loop in StartCompetition().
   */
  void EndCompetition() override;

  /**
   * Constructor for TimedRobot.
   *
   * @param period Period.
   */
  explicit ExpTimedRobot(units::second_t period = kDefaultPeriod);

  ExpTimedRobot(ExpTimedRobot&&) = default;
  ExpTimedRobot& operator=(ExpTimedRobot&&) = default;

  ~ExpTimedRobot() override;


  };

}  // namespace frc
