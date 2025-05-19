#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>

#include "app.h"

#include "FreeRTOS.h"
#include "task.h"

#include "radiolink.h"
#include "configblock.h"

#define DEBUG_MODULE "P2P"
#include "debug.h"
#include "log.h"
#include "param.h"
#include "crtp_commander_high_level.h"
#include "commander.h"
#include "estimator_kalman.h"
#include "deck_constants.h"

static paramVarId_t paramIdCommanderEnHighLevel;
static paramVarId_t paramIdResetKalman;

static void resetKalman() { paramSetInt(paramIdResetKalman, 1); }
static void enableHighlevelCommander() { paramSetInt(paramIdCommanderEnHighLevel, 1); }

double dt = 0.05;

static float self_x;
static float self_y;
static float self_z;

// Total flight time
double total_flight = 0.0;

// Velocity
double vx = 0.1;
double vy = 0.1;
double vz = 0.0;

// State machine
typedef enum {
    idle,
    takingOff,
    onAir,
    land,
    terminate,
} State;

static State state = idle;

// This function is used to send velocity commands since the original set VelCmd does
// not have altitude control integrated and needs to be send with vz.
// SetHoverSetpoint has altitude control integrated
static void setVelCmd(setpoint_t *setpoint, float vx, float vy, float vz)
{

  setpoint->mode.x = modeVelocity;
  setpoint->mode.y = modeVelocity;
  setpoint->mode.z = modeVelocity;

  setpoint->velocity.x = vx;
  setpoint->velocity.y = vy;
  setpoint->velocity.z = vz;

  setpoint->mode.yaw = modeVelocity;
  setpoint->attitudeRate.yaw = 0.0;
}

void appMain()
{
    static setpoint_t setpoint;

    // Setting Ids for logging
    logVarId_t idX = logGetVarId("stateEstimate", "x");
    logVarId_t idY = logGetVarId("stateEstimate", "y");
    logVarId_t idZ = logGetVarId("stateEstimate", "z");

    paramIdCommanderEnHighLevel = paramGetVarId("commander", "enHighLevel");
    paramIdResetKalman = paramGetVarId("kalman", "resetEstimation");

    resetKalman();
    enableHighlevelCommander();

  while(1) {

    if (state == idle)
    {
        vTaskDelay(M2T(5000));
        crtpCommanderHighLevelTakeoff(0.5, 2.5);
        vTaskDelay(M2T(3000));
        state = takingOff;
    }

    if (state == takingOff) {
        if (crtpCommanderHighLevelIsTrajectoryFinished())
            {state = onAir;}
    }

    // Flying state
    if (state == onAir) {

      // Print state
      self_x = logGetFloat(idX);
      DEBUG_PRINT("X position is %.3f\n", (double)self_x);
      self_y = logGetFloat(idY);
      DEBUG_PRINT("Y position is %.3f\n", (double)self_y);
      self_z = logGetFloat(idZ);
      DEBUG_PRINT("Z position is %.3f\n", (double)self_z);

      // Setting a total flight time
      total_flight += dt * 1000;

      //Sending control commands to low level Controllers
      setVelCmd(&setpoint, vx, vy, vz);
      commanderSetSetpoint(&setpoint, 3);

      if (total_flight > 5000) {
        state = land;
      }
      vTaskDelay(M2T(50));
    }

    // Our defined land sequence.
    if(state == land) {
      int tm;
      tm = 0;

      while (tm < 61)
        {
            setVelCmd(&setpoint, 0.0, 0.0, -0.1);
            commanderSetSetpoint(&setpoint, 3);
            tm += 1;
            vTaskDelay(M2T(50));
        }
      vTaskDelay(M2T(500));
      return;
    }

//    if (state == land)
//    {
//        crtpCommanderHighLevelLand(0.0, 2.5);
//        vTaskDelay(M2T(2000));
//        return;
//    }
  }
}

