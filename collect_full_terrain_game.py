#!/usr/bin/env python3
"""Collect game data with full terrain information for world reports

IMPORTANT: Understanding Agents vs AI Players
---------------------------------------------
In CivRealm, there are TWO different types of "AI":

1. AGENTS (Python classes like RandomAgent, ControllerAgent, NoOpAgent):
   - These are Python implementations that control a player through the CivRealm API
   - RandomAgent: Takes random actions from available actions
   - ControllerAgent: Takes semi-random actions with some heuristics
   - NoOpAgent: Does nothing (returns None, ending the turn immediately)
   - These run in your Python process and decide actions programmatically

2. FREECIV AI (Built-in game AI):
   - This is the native AI that comes with the Freeciv game engine
   - It's a sophisticated C implementation that plays Civilization competently
   - Has multiple difficulty levels: handicapped, novice, easy, normal, hard, cheating, experimental
   - This runs inside the Freeciv server and is MUCH more competent than Python agents

This script uses the FREECIV AI for all players by:
1. Setting aifill=7 to add 7 AI players
2. Connecting as 1 player (myagent2)
3. Using NoOpAgent (does nothing) for the connected player
4. Toggling the connected player to Freeciv AI control with /aitoggle
5. Result: 8 total players, ALL controlled by competent Freeciv AI at hard difficulty
"""

from civrealm.configs import fc_args
from civrealm.agents import NoOpAgent
import gymnasium
import time

# Configuration
fc_args['username'] = 'myagent2'
fc_args['debug.record_action_and_observation'] = True

# AI Configuration
# Total AI players = NUM_AI_PLAYERS (via aifill) + 1 (the connected player, toggled to AI)
NUM_AI_PLAYERS = 7  # Number of additional AI players to add (configurable)
AI_DIFFICULTY = 'hard'  # Options: 'handicapped', 'novice', 'easy', 'normal', 'hard', 'cheating', 'experimental'
fc_args['aifill'] = NUM_AI_PLAYERS

def main():
    print("Starting full collection...")
    print(f"Username: {fc_args['username']}")
    print(f"Total AI Players: {NUM_AI_PLAYERS + 1} ({NUM_AI_PLAYERS} via aifill + 1 connected player toggled to AI)")
    print(f"AI Difficulty: {AI_DIFFICULTY} (using built-in Freeciv AI)")
    print(f"Recording to: logs/recordings/{fc_args['username']}/")
    print()

    env = gymnasium.make('civrealm/FreecivBase-v0')
    # NoOpAgent does nothing - we'll toggle the player to Freeciv AI control
    agent = NoOpAgent()

    observations, info = env.reset()

    # Set AI difficulty level for all AI players
    # This must be done before toggling our player to AI
    print(f"Setting AI difficulty to {AI_DIFFICULTY}...")
    env.civ_controller.ws_client.send_message(f"/set skilllevel {AI_DIFFICULTY}")

    # Toggle the connected player to be AI-controlled by Freeciv's built-in AI
    # This makes ALL players in the game controlled by competent Freeciv AI
    print(f"Toggling {fc_args['username']} to Freeciv AI control...")
    env.civ_controller.ws_client.send_message(f"/aitoggle {fc_args['username']}")

    # Give the server a moment to process the commands
    time.sleep(2)

    done = False
    step = 0
    max_turns = 50

    print(f"Game started - all {NUM_AI_PLAYERS + 1} players are controlled by Freeciv AI")
    print(f"Running for {max_turns} turns (AI vs AI competitive game)")
    print()

    while not done:
        try:
            # NoOpAgent returns None, ending the turn and letting Freeciv AI play
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
