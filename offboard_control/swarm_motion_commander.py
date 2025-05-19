import time

import cflib.crtp
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.crazyflie.swarm import Swarm
from cflib.positioning.motion_commander import MotionCommander

uris = {
    'radio://0/100/2M/E7E7E7E701',
    'radio://0/100/2M/E7E7E7E702',
    # Add more URIs if you want more copters in the swarm
    # URIs in a swarm using the same radio must also be on the same channel
}

def arm(scf):
    scf.cf.platform.send_arming_request(True)
    time.sleep(1.0)

def swarm_mc(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        time.sleep(1)

        # There is a set of functions that move a specific distance
        # We can move in all directions
        mc.forward(0.4)
        mc.back(0.4)
        time.sleep(1)

        mc.up(0.2)
        mc.down(0.2)
        time.sleep(1)

        mc.stop()

if __name__ == '__main__':
    DEFAULT_HEIGHT = 0.6
    cflib.crtp.init_drivers()
    factory = CachedCfFactory(rw_cache='./cache')
    with Swarm(uris, factory=factory) as swarm:
        swarm.reset_estimators()
        swarm.parallel_safe(arm)
        swarm.parallel_safe(swarm_mc)