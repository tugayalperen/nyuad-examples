import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper


uri = uri_helper.uri_from_env(default='radio://0/100/2M/E7E7E7E702')

def run_sequence(cf):
    commander = cf.high_level_commander
    commander_low = cf.commander
    altitude = 0.3

    # Arm the Crazyflie
    cf.platform.send_arming_request(True)
    time.sleep(1.0)
    # Takeoff
    commander.takeoff(altitude, 2.0)
    time.sleep(3.0)

    for i in range(5):
        commander_low.send_hover_setpoint(0.2, 0.0, 0.0, altitude)
        time.sleep(1.0)
    for i in range(5):
        commander_low.send_hover_setpoint(0.0, 0.2, 0.0, altitude)
        time.sleep(1.0)

    altitude = altitude + 0.4
    for i in range(2):
        commander_low.send_hover_setpoint(0.0, 0.0, 0.0, altitude)
        time.sleep(1.0)

    # Low Level landing
    while altitude > 0.05:
        commander_low.send_hover_setpoint(0.0, 0.0, 0.0, altitude)
        time.sleep(0.1)
        altitude = altitude - 0.02


    commander_low.send_stop_setpoint()

    # commander.land(0.0, 2.0)
    # time.sleep(2)
    # commander.stop()

if __name__ == '__main__':
    cflib.crtp.init_drivers()

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        cf = scf.cf
        run_sequence(cf)