# Import gym ang gym_carla
import gym_carla
import gym
# import cv2

def main():
    # Instantiate the environment
    env = gym.make('CarlaEnv-v0')
    # Initialize parameters or reset environment
    _ = env.reset()
    # Enable Autopilot
    env.vehicle.set_autopilot(True)

    # For each episode
    for _ in range(0,1000):

        # Render pygame window
        env.render()
        action = 1

        # Execute action
        state, reward, done, info = env.step(action)
        
        if done:
            _ = env.reset()

        # Check for user inputs
        env.game.event_parser()


        if env.game.to_quit():
            print('Stopping test')
            break
    
    # Clear carla actors and close environment
    env.destroy()
    env.close()


if __name__=="__main__":
    main()
