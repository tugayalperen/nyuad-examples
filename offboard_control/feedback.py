import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper
from cflib.crazyflie.log import LogConfig


uri = uri_helper.uri_from_env(default='radio://0/100/2M/E7E7E7E701')

def position_callback(timestamp, data, logconf):
    x = data['kalman.stateX']
    y = data['kalman.stateY']
    z = data['kalman.stateZ']
    print('pos: ({}, {}, {})'.format(x, y, z))


def start_position_printing(scf):
    log_conf = LogConfig(name='Position', period_in_ms=500)
    log_conf.add_variable('kalman.stateX', 'float')
    log_conf.add_variable('kalman.stateY', 'float')
    log_conf.add_variable('kalman.stateZ', 'float')

    scf.cf.log.add_config(log_conf)
    log_conf.data_received_cb.add_callback(position_callback)
    log_conf.start()

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
        start_position_printing(scf)
        run_sequence(cf)