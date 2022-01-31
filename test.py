import gym_carla
import gym

def main():
    env = gym.make('CarlaEnv-v0')
    _ = env.reset()
    env.vehicle.set_autopilot(True)
    for i in range(0,1000):
        env.render()
        env.world.tick()
        env.game.get_events()
        if env.game.to_quit():
            print('Time to quit')
            break
    print('I quit')
    env.destroy()
    env.exit()


if __name__=="__main__":
    main()
