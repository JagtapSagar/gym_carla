import gym_carla
import gym

def main():
    env = gym.make('CarlaEnv-v0')
    _ = env.reset()
    env.vehicle.set_autopilot(True)
    for _ in range(0,1000):
        env.render()
        action = 1
        state, reward, done, info = env.step(action)
        if done:
            _ = env.reset()

        env.game.event_parser()


        if env.game.to_quit():
            print('Time to quit')
            break
    print('I quit')
    env.destroy()
    env.close()


if __name__=="__main__":
    main()
