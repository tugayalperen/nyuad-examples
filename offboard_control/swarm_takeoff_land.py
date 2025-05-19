import time

import cflib.crtp
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.crazyflie.swarm import Swarm

uris = {
    'radio://0/100/2M/E7E7E7E701',
    'radio://0/100/2M/E7E7E7E702',
    # Add more URIs if you want more copters in the swarm
    # URIs in a swarm using the same radio must also be on the same channel
}

def arm(scf):
    scf.cf.platform.send_arming_request(True)
    time.sleep(1.0)

def run_shared_sequence(scf):
    commander = scf.cf.high_level_commander

    commander.takeoff(0.6, 2.0)
    time.sleep(3)

    commander.land(0.0, 2.0)
    time.sleep(2)

    commander.stop()

if __name__ == '__main__':
    cflib.crtp.init_drivers()
    factory = CachedCfFactory(rw_cache='./cache')
    with Swarm(uris, factory=factory) as swarm:
        swarm.reset_estimators()
        swarm.parallel_safe(arm)
        swarm.parallel_safe(run_shared_sequence)