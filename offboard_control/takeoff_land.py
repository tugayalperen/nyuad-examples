import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper


uri = uri_helper.uri_from_env(default='radio://0/100/2M/E7E7E7E703')

def run_sequence(cf):
    commander = cf.high_level_commander

    # Arm the Crazyflie
    cf.platform.send_arming_request(True)
    time.sleep(1.0)
    # Takeoff
    commander.takeoff(0.3, 2.0)
    time.sleep(5.0)
    # Land
    commander.land(0.0, 2.0)
    time.sleep(2)
    commander.stop()

if __name__ == '__main__':
    cflib.crtp.init_drivers()

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        cf = scf.cf
        run_sequence(cf)