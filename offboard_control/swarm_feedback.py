import time
import threading
import cflib.crtp
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.crazyflie.swarm import Swarm
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger

URI1 = 'radio://0/100/2M/E7E7E7E701'
URI2 = 'radio://0/100/2M/E7E7E7E702'

# List of URIs
uris = {
    URI1,
    URI2,
}

def log_swarm(swarm):
    swarm.parallel_safe(log_swarm_func)

def log_swarm_func(scf):
    log_config = LogConfig(name="Position", period_in_ms=500)
    log_config.add_variable('stateEstimate.x', 'float')
    log_config.add_variable('stateEstimate.y', 'float')
    log_config.add_variable('stateEstimate.z', 'float')

    with SyncLogger(scf, log_config) as logger:
        for entry in logger:
            if scf.cf.link_uri == URI1:
                x = entry[1]['stateEstimate.x']
                y = entry[1]['stateEstimate.y']
                z = entry[1]['stateEstimate.z']
                print('URI1 pos: ({}, {}, {})'.format(x, y, z))
            elif scf.cf.link_uri == URI2:
                x = entry[1]['stateEstimate.x']
                y = entry[1]['stateEstimate.y']
                z = entry[1]['stateEstimate.z']
                print('URI2 pos: ({}, {}, {})'.format(x, y, z))

def arm(scf):
    scf.cf.platform.send_arming_request(True)
    time.sleep(1.0)

def swarm_hl(scf):
    box_size = 0.5
    flight_time = 2


    commander = scf.cf.high_level_commander

    commander.takeoff(DEFAULT_HEIGHT, 2.0)
    time.sleep(3)

    if scf.__dict__['_link_uri'] == URI1:
        commander.go_to(box_size, 0, 0, 0, flight_time, relative=True)
        time.sleep(flight_time)
    elif scf.__dict__['_link_uri'] == URI2:
        commander.go_to(-box_size, 0, 0, 0, flight_time, relative=True)
        time.sleep(flight_time)

    if scf.__dict__['_link_uri'] == URI1:
        commander.go_to(0, -box_size, 0, 0, flight_time, relative=True)
        time.sleep(flight_time)
    elif scf.__dict__['_link_uri'] == URI2:
        commander.go_to(0, box_size, 0, 0, flight_time, relative=True)
        time.sleep(flight_time)

    if scf.__dict__['_link_uri'] == URI1:
        commander.go_to(0, 0, box_size, 0, flight_time, relative=True)
        time.sleep(flight_time)
    elif scf.__dict__['_link_uri'] == URI2:
        commander.go_to(0, 0, -box_size, 0, flight_time, relative=True)
        time.sleep(flight_time)

    if scf.__dict__['_link_uri'] == URI1:
        commander.go_to(0, 0, -box_size, 0, flight_time, relative=True)
        time.sleep(flight_time)
    elif scf.__dict__['_link_uri'] == URI2:
        commander.go_to(0, 0, box_size, 0, flight_time, relative=True)
        time.sleep(flight_time)

    commander.land(0.0, 2.0)
    time.sleep(2)

    commander.stop()

if __name__ == '__main__':
    DEFAULT_HEIGHT = 0.6
    cflib.crtp.init_drivers()
    factory = CachedCfFactory(rw_cache='./cache')
    with Swarm(uris, factory=factory) as swarm:
        thread_1 = threading.Thread(target=log_swarm, args=([swarm]))
        thread_1.start()
        swarm.parallel_safe(arm)
        swarm.parallel_safe(swarm_hl)
