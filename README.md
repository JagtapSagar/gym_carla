# Gym_CARLA
Gym wrapper for CARLA simulator.

Requirements:
* CARLA 9.11 or later
* Python 3.7

Installing the Gym Simulator
---
To run this project:
1. Install Carla Simulator
2. Download this repository to a local directory
3. Open the directory in terminal or command prompt
4. Execute following command to install 'gym_carla'
   >`pip install -e .`
4. Reffer `test.py` script on how to use gym wrapper.

Note:
* To create additional sensors edit `envs/carla_sensor.py`
* To instatiate sensors and modify agent properties edit `envs/carla_env.py`
