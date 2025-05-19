import time
import cflib.crtp
from cflib.crazyflie.swarm import Swarm
from cflib.crazyflie.swarm import CachedCfFactory

uris = {
    'radio://0/100/2M/E7E7E7E703',
    # 'radio://0/100/2M/E7E7E7E703',
    # 'radio://0/100/2M/E7E7E7E709',
}

def _take_off(scf):
    cf = scf.cf
    cf.param.set_value("fmodes.if_takeoff", 1)
    time.sleep(0.1)

def take_off(swarm):
    swarm.parallel_safe(_take_off)

def _land(scf):
    cf = scf.cf
    cf.param.set_value("fmodes.if_land", 1)
    time.sleep(0.1)

def land(swarm):
    swarm.parallel_safe(_land)

if __name__ == '__main__':
    cflib.crtp.init_drivers(enable_debug_driver=False)
    factory = CachedCfFactory(rw_cache='./cache')

    took_off = False
    landed = True

    with Swarm(uris, factory=factory) as swarm:
        # take_off(swarm)
        # time.sleep(10)
        land(swarm)