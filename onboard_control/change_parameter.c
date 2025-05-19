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

static float go_to_x = 1.0;
static float go_to_y = 0.5;
static float go_to_z = 0.2;
static float go_to_yaw = 0.0;
static float go_to_duration = 2.0;
static bool go_to_relative = true;
static bool update_setpoint = true;

static paramVarId_t paramIdiftakeoff;
static paramVarId_t paramIdifterminate;
static paramVarId_t paramIdifland;

// Total flight time
double total_flight = 0.0;

// State machine
typedef enum {
    idle,
    takingOff,
    onAir,
    land,
    terminate,
} State;

static State state = idle;

void appMain()
{
    static uint8_t iftakeoff;
    static uint8_t ifterminate;
    static uint8_t ifland;

    iftakeoff = 0;
    ifterminate = 0;
    ifland = 0;

    // -> Flight modes
    PARAM_GROUP_START(fmodes)
    PARAM_ADD_CORE(PARAM_UINT8, if_takeoff, &iftakeoff)
    PARAM_ADD_CORE(PARAM_UINT8, if_terminate, &ifterminate)
    PARAM_ADD_CORE(PARAM_UINT8, if_land, &ifland)
    PARAM_GROUP_STOP(fmodes)

    // Setting Ids for logging
    logVarId_t idX = logGetVarId("stateEstimate", "x");
    logVarId_t idY = logGetVarId("stateEstimate", "y");
    logVarId_t idZ = logGetVarId("stateEstimate", "z");

    paramIdCommanderEnHighLevel = paramGetVarId("commander", "enHighLevel");
    paramIdResetKalman = paramGetVarId("kalman", "resetEstimation");

    paramIdiftakeoff = paramGetVarId("fmodes", "if_takeoff");
    paramIdifterminate = paramGetVarId("fmodes", "if_terminate");
    paramIdifland = paramGetVarId("fmodes", "if_land");

    resetKalman();
    enableHighlevelCommander();

  while(1) {

    if (state == idle)
    {
        if (iftakeoff == 0)
      {
        // Gets takeoff flag
        iftakeoff = paramGetInt(paramIdiftakeoff);
        vTaskDelay(M2T(100));
      }

      if (iftakeoff == 1)
      {
        vTaskDelay(M2T(1000));
        crtpCommanderHighLevelTakeoff(0.5, 2.5);
        vTaskDelay(M2T(4000));
        state = takingOff;
      }
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

      if (update_setpoint) {
      //Sending control commands to high level Controllers
      crtpCommanderHighLevelGoTo(
          go_to_x,
          go_to_y,
          go_to_z,
          go_to_yaw,
          go_to_duration,
          go_to_relative
      );
        update_setpoint = false;
      }

      ifterminate = paramGetInt(paramIdifterminate);
      ifland = paramGetInt(paramIdifland);
      total_flight += dt * 1000;

      if (total_flight > 10000  || ifland == 1) {
        state = land;
      }
      vTaskDelay(M2T(50));
    }

    if (state == land)
    {
        crtpCommanderHighLevelLand(0.0, 2.5);
        vTaskDelay(M2T(2000));
        return;
    }
  }
}

