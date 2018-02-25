import dronekit_sitl
import dronekit
import json
import argparse
import os
import threading
import time
import signal
import util
import logging

_LOG = logging.getLogger(__name__)
_LOG.setLevel(logging.INFO)

fh = logging.FileHandler('main.log', mode='w')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('| %(levelname)6s | %(funcName)8s:%(lineno)2d | %(message)s |')
fh.setFormatter(formatter)
_LOG.addHandler(fh)


DO_CONT = False
LOCATIONS = []

# make sure you change this so that it's correct for your system 
ARDUPATH = os.path.join('/', 'home', 'emily', 'git', 'ardupilot')


def load_json(path2file):
    d = None
    try:
        with open(path2file) as f:
            d = json.load(f)
    except Exception as e:
        exit('Invalid path or malformed json file! ({})'.format(e))

    return d


def connect_vehicle(instance, home):
    home_ = tuple(home) + (0,)
    home_ = ','.join(map(str, home_))
    sitl_defaults = os.path.join(ARDUPATH, 'Tools', 'autotest', 'default_params', 'copter.parm')
    sitl_args = ['-I{}'.format(instance), '--home', home_, '--model', '+', '--defaults', sitl_defaults]
    sitl = dronekit_sitl.SITL(path=os.path.join(ARDUPATH, 'build', 'sitl', 'bin', 'arducopter'))
    sitl.launch(sitl_args, await_ready=True)

    tcp, ip, port = sitl.connection_string().split(':')
    port = str(int(port) + instance * 10)
    conn_string = ':'.join([tcp, ip, port])

    vehicle = dronekit.connect(conn_string)
    vehicle.wait_ready(timeout=120)

    return vehicle, sitl


def get_vehicle_id(i):
    return 'drone{}'.format(i)


def state_out_work(dronology, vehicles):
    while DO_CONT:
        for i, v in enumerate(vehicles):
            state = util.StateMessage.from_vehicle(v, get_vehicle_id(i))
            state_str = str(state)
            _LOG.info(state_str)
            dronology.send(state_str)

        time.sleep(1.0)

def get_vehicle_locations(vehicles):
    for i, vehicle in enumerate(vehicles):
        location = vehicle.location.global_relative_frame
        LOCATIONS[i] = location

def get_distance_meters(latitude1, longitude1, latitude2, longitude2):
    lat1 = radians(latitude1)
    lon1 = radians(longitude1)
    lat2 = radians(latitude2)
    lon2 = radians(longitude2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    distance = R * c * 1000

    print("Result: ", distance)

def check_distance(vehicle_num, waypoint):
    if get_distance_meters(LOCATIONS[vehicle_num].lat, LOCATIONS[vehicle_num].lon, waypoint[0], waypoint[1]) <= 3:
        return True
    else:
        return False

def set_mode(vehicle, mode):
    vehicle.mode = dronekit.VehicleMode(mode)
    _mode = vehicle.mode.name

    while _mode != mode:
        vehicle.mode = dronekit.VehicleMode(mode)
        _mode = vehicle.mode.name

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self.timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs

        self.active = False

        self.start_timer()


	def start_timer(self):
		if not self.active:
			self.next = self.interval
			self.timer = threading.RepeatedTimer(self.next - time.time(), self.run)
			self.timer.start_timer()
			self.active = True

    def start_timer(self):
        if not self.active:
            self.next = self.interval
            self.timer = threading.Timer(self.next - time.time(), self.run)
            self.timer.start_timer()
            self.active = True


    def run(self):
        self.active = False
        self.start_timer()
        self.function(*self.args, **self.kwargs)

    def stop(self):
        self.timer.cancel()
        self.active = False





def main(path_to_config, ardupath=None):
    if ardupath is not None:
        global ARDUPATH
        ARDUPATH = ardupath
    
    global DO_CONT
    DO_CONT = True

    config = load_json(path_to_config)
    dronology = util.Connection()
    dronology.start()

    # A list of sitl instances.
    sitls = []
    # A list of drones. (dronekit.Vehicle)
    vehicles = []
    # A list of lists of lists (i.e., [ [ [lat0, lon0, alt0], ...] ...]
    # These are the waypoints each drone must go to!
    routes = []

    # Example:
    # vehicle0 = vehicles[0]
    # waypoints_for_vehicle0 = routes[0]
    # for waypoint in waypoints_for_vehicle0:
    #    lat, lon, alt = waypoint
    #    vehicle0.simple_goto(lat, lon, alt)

    # The above example obviously won't work... you'll need to write some code to figure out when the current waypoint
    # has been reached and it's time to go to the next waypoint.

    # Define the shutdown behavior
    def stop(*args):
        global DO_CONT
        DO_CONT = False
        w0.join()

        for v, sitl in zip(vehicles, sitls):
            v.close()
            sitl.stop()

        dronology.stop()

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    
    # Start up all the drones specified in the json configuration file
    for i, v_config in enumerate(config):
        home = v_config['start']
        vehicle, sitl = connect_vehicle(i, home)

        handshake = util.DroneHandshakeMessage.from_vehicle(vehicle, get_vehicle_id(i))
        dronology.send(str(handshake))

        sitls.append(sitl)
        vehicles.append(vehicle)
        routes.append(v_config['waypoints'])
        
    # Create a thread for sending the state of drones back to Dronology
    w0 = threading.Thread(target=state_out_work, args=(dronology, vehicles))
    # Start the thread.
    w0.start()

    # At this point, all of the "behind the scenes stuff" has been set up.
    # It's time to write some code that:
    #   1. Starts up the drones (set the mode to guided, arm, takeoff)
    #   2. Sends the drones to their waypoints
    #   3. Hopefully avoids collisions!


    # You're encouraged to restructure this code as necessary to fit your own design.
    # Hopefully it's flexible enough to support whatever ideas you have in mind.

    # Create an array called "done" that keeps track of whether the drone has reached its destination
    done = []
    # Create an array called "curr_dest" that keeps track of the number waypoint that the drone is currently going
    curr_dest = []

    # Start up the drones
    for vehicle in vehicles:
        # Set mode to guided
        set_mode(vehicle, "GUIDED")

        # Arm vechicle
        if vehicle.armed != True:
            while not vehicle.is_armable:
                time.sleep(2)

            vehicle.armed = True
            while vehicle.armed != True:
                vehicle.armed = True

        #Takeoff
        vehicle.simple_takeoff(20)
        print("Starting drone: ", vehicle)
        done.append(False)
        curr_dest.append(-1)

        location = vehicle.location.global_relative_frame
        LOCATIONS.append(location)


    # Get all drones location at every second
    location_timer = RepeatedTimer(1, get_vehicle_locations, vehicles)


    # Send drones to their waypoints
    while DO_CONT:
        print("Sending drones to waypoints")
        for i, vehicle in enumerate(vehicles):

            way_number = curr_dest[i]
            #if len(routes[i]) == way_number:
            #   done[i] = True
            #   set_mode(vehicle, "LAND")

        if way_number == -1:
            ready=True
        else:               
            ready = check_distance(i, routes[i][way_number-1])

            if not done[i] and ready:
            if way_number == len(route[i]):
                set_mode(vehicle, "LAND")
                done[i]=True
                break
                curr_dest[i] += 1               
            vehicle.simple_goto(dronekit.LocationGlobalRelative(routes[i][way_number][0], routes[i][way_number][1], routes[i][way_number][2]))





    # wait until ctrl c to exit
    while DO_CONT:
        time.sleep(5.0)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('path_to_config', type=str, help='the path to the drone configuration file.')
    ap.add_argument('--ardupath', type=str, default=ARDUPATH)
    args = ap.parse_args()
    main(args.path_to_config, ardupath=args.ardupath)
