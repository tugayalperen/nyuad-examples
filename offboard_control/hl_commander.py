import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.position_hl_commander import PositionHlCommander
from cflib.utils import uri_helper

# URI to the Crazyflie to connect to
uri = uri_helper.uri_from_env(default='radio://0/100/2M/E7E7E7E702')

def simple_sequence():
    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        # Arm the Crazyflie
        scf.cf.platform.send_arming_request(True)
        time.sleep(1.0)

        with PositionHlCommander(scf, controller=PositionHlCommander.CONTROLLER_PID) as pc:
            pc.forward(0.5)
            pc.left(0.5)
            pc.back(0.5)
            pc.go_to(0.0, 0.0, 0.5)
            pc.move_distance(-0.5, 0.0, 0.0)
            pc.move_distance(0.5, 0.0, 0.0)
            pc.land(0.2, 0.0)


if __name__ == '__main__':
    cflib.crtp.init_drivers()
    simple_sequence()


