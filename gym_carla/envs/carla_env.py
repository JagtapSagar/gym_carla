import gym
from gym import spaces, logger
import numpy as np
import random
import math
import cv2
import carla

from gym_carla.envs.carla_car import SensorManager

class CarlaEnv(gym.Env):
    def __init__(self):
        print('Setting up gym-carla environment')

        # Observation shape (x,y)
        self.im_height                    = 150
        self.im_width                     = 150

        self.action_space      = spaces.Discrete(6)
        observation_space_dict = {
                    'camera': spaces.Box(low=0, high=255, shape=(9, self.im_height, self.im_width), dtype=np.uint8)
                    # 'lidar': spaces.Box(low=0, high=255, shape=(self.obs_size, self.obs_size, 3), dtype=np.uint8),
                    # 'state': spaces.Box(np.array([-2, -1, -5, 0]), np.array([2, 1, 30, 1]), dtype=np.float32)
                    }
        self.observation_space = spaces.Dict(observation_space_dict)

        # Connect with CARLA
        print('Connecting to CARLA server')
        self.client                       = carla.Client("localhost", 2000)
        self.client.set_timeout(10.0)
        # self.world = self.client.load_world('/Game/Carla/Maps/Town05_Opt', carla.MapLayer.ParkedVehicles)     # Load map with buildings and parked vehicles
        self.world                        = self.client.get_world()
        self.map                          = self.world.get_map()
        print('Connected established')

        # Get settings 
        self.original_settings            = self.world.get_settings()            # To reset at a later time
        self.settings                     = self.world.get_settings()            # Change setting here
        self.settings.fixed_delta_seconds = 0.05                                 # Set frequency to 20 fps

        # Enable synchronous model
        self.set_synchronous_mode(True)

        # Episode timeout criteria
        self.terminal_tick                = 500

        # Get blueprints and set spectator
        self.blueprint_library            = self.world.get_blueprint_library()
        self.model_3                      = self.blueprint_library.filter("model3")[0]
        self.model_3.set_attribute('color', '255,0,0')

        self.sensors = SensorManager(self.world, self.im_height, self.im_width)

        # Set sensor attributes
        self.sensor_attributes  =  {'RGBCamera':{'transform':carla.Transform(carla.Location(x=2.5, z=0.7)),
                                                'attributes':{'image_size_x' : str(self.im_height), 'image_size_y' : str(self.im_width)}},
                                    # 'SemacticRGBCamera':{'transform':carla.Transform(carla.Location(x=2.5, z=0.7)),
                                    #             'attributes':{'image_size_x' : str(self.im_height), 'image_size_y' : str(self.im_width)}},
                                    # 'LiDAR'    :{'transform':carla.Transform(carla.Location(x=0, z=2.4)),
                                    #             'attributes':{'channels' : '64', 'range' : '100',
                                    #                         'points_per_second': '250000', 'rotation_frequency': '20'}},
                                    # 'SemanticLiDAR'    :{'transform':carla.Transform(carla.Location(x=0, z=2.4)),
                                    #                     'attributes':{'channels' : '64', 'range' : '100',
                                    #                                 'points_per_second': '250000', 'rotation_frequency': '20'}},
                                    'Radar'    :{'transform':carla.Transform(carla.Location(x=2.5, z=0.7), carla.Rotation(pitch=9)),
                                                'attributes':{'horizontal_fov' : '90', 'vertical_fov' : '30'}},
                                    'Collision':{'transform':carla.Transform(), 'attributes':None}
                                    }

    
    def set_synchronous_mode(self, synchronous = True):
        """Set whether to use the synchronous mode"""
        self.settings.synchronous_mode = synchronous
        self.world.apply_settings(self.settings)
    
    def reset(self):
        """Resets CARLA environment"""

        try:
            # Destroy all actors
            if len(self.actor_list)>0:
                self.destroy()
                self.actor_list = []
        except:
            self.actor_list = []

        self.action_buffer                = None         # Used to store last action
        self.tick_count                   = 0
        self.r_proximity                  = 0
        self.vehicle                      = None
        
        # Clear all sensor variables
        self.sensors.reset()

        # Spawn new vehicle
        self.vehicle = self.world.spawn_actor(self.model_3, random.choice(self.map.get_spawn_points()))
        self.actor_list.append(self.vehicle)
        self.vehicle.set_autopilot(True)

        # Instantiate vehicle sensors
        for sensor in self.sensor_attributes:
            self.actor_list.append(self.sensors.init_sensor(sensor, self.sensor_attributes[sensor]['transform'], self.vehicle, self.sensor_attributes[sensor]['attributes']))
        
        # Tick the server
        self.world.tick(0.1)

        # Prepare state inputed state
        self.state             = np.zeros([9, self.im_height, self.im_width])
        _,_ = self.skipFrames()
        # return observation space
        return self.state
    
    def skipFrames(self):
        """Function performs three consecutive ticks to build state array"""
        reward_total = 0
        done = False
        for i in range(0,3):
            tick_success = False
            count = 0
            # To account for tick filure
            while not tick_success:
                try:
                    self.world.tick(0.1)
                    tick_success = True
                    self.tick_count += 1
                except:
                    count += 1
                    print("WARNING: tick not received: ")
                if count > 5 :
                    print('Consecutive tick failure!')
                    break

            # Update state array using LiDAR and RGB images
            obs = self.sensors._get_observations()
            self.state[(i*3):3+(i*3),:,:]     = np.transpose(obs,(2,0,1))
            
            if not done:
                reward,done                    = self._get_reward()
                reward_total                  += reward                 # Calculate cumulative reward
            else:
                reward_total                   = reward
        return reward_total, done
    
    def step(self, action):
        """ Perform simulation step for a given action.
            Action must be from a discrete value between 0 - 5
        """
        self.action_buffer = action
        throttle = 0.6 if self._get_vehicle_speed()<=self.speed_threshold else 0
        self.r_proximity                  = 0

        if action == 0: # Brake
            self.vehicle.apply_control(carla.VehicleControl(throttle=0, steer=0, brake=1))
        elif action == 1: # Forward
            self.vehicle.apply_control(carla.VehicleControl(throttle=throttle, steer= 0))
        elif action == 2: # Slight Left
            self.vehicle.apply_control(carla.VehicleControl(throttle=throttle, steer=-0.25))
            if self.sensors._get_road_highlights(-1):
                self.r_proximity = -0.5
        elif action == 3: # Slight Right
            self.vehicle.apply_control(carla.VehicleControl(throttle=throttle, steer=0.25))
            if self.sensors._get_road_highlights(1):
                self.r_proximity = -0.5
        elif action == 4: # 45 Left
            self.vehicle.apply_control(carla.VehicleControl(throttle=throttle, steer=-0.5))
            if self.sensors._get_road_highlights(-1):
                self.r_proximity = -0.5
        elif action == 5: # 45 Right
            self.vehicle.apply_control(carla.VehicleControl(throttle=throttle, steer=0.5))
            if self.sensors._get_road_highlights(1):
                self.r_proximity = -0.5
        
        # Perform action and observe states and reward
        reward,done = self.skipFrames()

        if self._timeout():
            done = True
        
        info = {}

        return self.state, reward, done, info
    
    def _timeout(self):
        """Returns true if tick episode limit reached"""
        return True if self.tick_count >= self.terminal_tick else False
    
    def _get_vehicle_speed(self):
        v          = self.vehicle.get_velocity()
        kmh        = int(3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2))
        return kmh

    def _get_reward(self):
        """Calculate the step reward"""

        # Set individual reward components to zero
        r_steer    = 0         # Steering reward
        r_radar    = 0         # Reward based on distance to obstacle
        r_con      = 0         # Reward for continuation
        r_col      = 0         # Reward component for collision
        r_lat      = 0         # Lateral component
        done       = False     # True only in case of termination
        
        # Calculate reward for vehicle speed (using quadratic function)
        kmh        = self._get_vehicle_speed()
        r_s        = (-0.0017*kmh**2)+(0.1167*kmh)-1

        # Check radar thresholds for reward
        radar_dist, radar_vel = self.sensors._get_nearest_radar_value()
        if (radar_dist is not None):
            if (radar_dist < 5):
                r_radar = -1
                if self.action_buffer==0:
                    self.r_proximity= 0.1
                if self.action_buffer==1:
                    self.r_proximity= -0.5
                radar_dist = None
            else:
                if self.action_buffer==1 and not(self.sensors._get_road_highlights(0) or self.sensors._get_road_highlights(1) or self.sensors._get_road_highlights(-1)):
                    self.r_proximity= 0.3
                elif not self.sensors._get_road_highlights(0):
                    if self.action_buffer==0:
                        self.r_proximity= -0.5
                    if self.action_buffer==1:
                        self.r_proximity= 0.1
                else:
                    if self.action_buffer==0:
                        self.r_proximity= -0.1
                    if self.action_buffer==1:
                        self.r_proximity= 0.1
                r_lat = -1*(0.05*kmh * abs(self.vehicle.get_control().steer))

        # Calculate Reward for steering
        r_steer = self.vehicle.get_control().steer**2
        if (self.vehicle.get_control().steer<0) and (self.sensors._get_road_highlights(-1)) or (self.vehicle.get_control().steer>0) and (self.sensors._get_road_highlights(1)):
            r_steer *= -1

        # Check for collision
        if self.sensors._check_for_collision():
            print("Collision event occurred")
            done = True
            r_col = -1
        
        if done == False:
            r_con = 0.5

        # Reward function
        reward = 200*r_col + 1*r_radar + 1*r_s + 1*r_con + 1*r_steer + self.r_proximity + 1*r_lat

        return reward, done

    def render(self):
        """Render image in pygame window"""
        # self.clock.tick()
        image = self.sensors._get_observations()
        cv2.imshow('', image)
        cv2.waitKey(1)


    def destroy(self):
        """Destroy all actors in list"""
        for actors in self.actor_list:
            actors.destroy()
    
    def exit(self):
        self.world.apply_settings(self.original_settings)
        self.set_synchronous_mode(False)
