#!/usr/bin/env python3
"""Collect game data with full terrain information for world reports"""

from civrealm.configs import fc_args
from civrealm.agents import RandomAgent
import gymnasium

# Configuration
# Use same username as before to avoid authentication issues
fc_args['username'] = 'myagent2'
fc_args['debug.record_action_and_observation'] = True
fc_args['aifill'] = 3  # 1 agent + 3 AI players

def main():
    print("Starting full collection...")
    print(f"Username: {fc_args['username']}")
    print(f"Recording to: logs/recordings/{fc_args['username']}/")
    print()

    env = gymnasium.make('civrealm/FreecivBase-v0')
    agent = RandomAgent()

    observations, info = env.reset()
    done = False
    step = 0
    max_turns = 50

    print(f"Game started - running for {max_turns} turns")

    while not done:
        try:
            action = agent.act(observations, info)
            observations, reward, terminated, truncated, info = env.step(action)

            turn = info.get('turn', 0)
            if turn > 0 and turn % 10 == 0:
                print(f"Turn {turn}/{max_turns}")

            step += 1
            done = terminated or truncated or turn >= max_turns

        except Exception as e:
            print(f"Error: {e}")
            raise e

    env.close()

    print()
    print("="*60)
    print("DATA COLLECTION COMPLETE!")
    print("="*60)
    return 0

if __name__ == '__main__':
    main()
