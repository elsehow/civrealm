#!/usr/bin/env python3
"""Run a Civilization game and generate world reports

This script runs an all-AI competitive game where ALL players are controlled
by Freeciv's built-in AI, then automatically generates world reports from the
recorded gameplay.

Setup:
- Connects as 1 player (myagent2) with NoOpAgent
- Toggles that player to Freeciv AI control via /aitoggle
- Adds 4 additional AI players via aifill
- Total: 5 Freeciv AI players, ALL using the same strategy

NoOpAgent's role:
- Simply returns None to end turn immediately
- Freeciv AI actually plays for this player
- This allows CivRealm to maintain connection and record observations

Result: A competitive 5-player all-AI game with full recording coverage.
All players use the same Freeciv AI algorithm, ensuring fair comparison.

After the game completes, world reports are automatically generated.
"""

import sys
from pathlib import Path

# Add src to path for world report imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from civrealm.configs import fc_args
from civrealm.agents import NoOpAgent
from civrealm.world_reports import ReportGenerator, ReportConfig
import gymnasium
import time

# Configuration
fc_args['username'] = 'myagent2'
fc_args['debug.record_action_and_observation'] = True

# AI Configuration
NUM_AI_PLAYERS = 4  # Number of AI opponents
AI_DIFFICULTY = 'hard'  # Options: 'handicapped', 'novice', 'easy', 'normal', 'hard', 'cheating', 'experimental'
fc_args['aifill'] = NUM_AI_PLAYERS

def main():
    print("Starting all-AI game collection...")
    print(f"Username: {fc_args['username']} (will be toggled to AI control)")
    print(f"AI Players: {NUM_AI_PLAYERS + 1} total (all Freeciv AI at {AI_DIFFICULTY} difficulty)")
    print(f"Setup: {NUM_AI_PLAYERS} via aifill + 1 connected player toggled to AI")
    print(f"Recording to: logs/recordings/{fc_args['username']}/")
    print()

    env = gymnasium.make('civrealm/FreecivBase-v0')
    # NoOpAgent just ends turn - connected player will be toggled to Freeciv AI
    agent = NoOpAgent()

    observations, info = env.reset()

    # Set AI difficulty level for all AI players
    print(f"Setting AI difficulty to {AI_DIFFICULTY}...")
    env.civ_controller.ws_client.send_message(f"/set skilllevel {AI_DIFFICULTY}")
    time.sleep(1)

    # Toggle the connected player to be AI-controlled by Freeciv's built-in AI
    # This makes ALL players in the game controlled by Freeciv AI
    print(f"Toggling {fc_args['username']} to Freeciv AI control...")
    env.civ_controller.ws_client.send_message(f"/aitoggle {fc_args['username']}")
    time.sleep(1)

    done = False
    step = 0
    max_turns = 50

    print(f"Game started - all {NUM_AI_PLAYERS + 1} players controlled by Freeciv AI")
    print(f"Running for {max_turns} turns (AI vs AI competitive game)")
    print()

    while not done:
        try:
            # NoOpAgent returns None, ending turn and letting Freeciv AI play
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
    print()

    # Generate world reports automatically
    print("Generating world reports...")
    print()

    # Configuration for world report generation
    report_config = ReportConfig(
        # Input: where our game recording is stored
        recording_dir=f'logs/recordings/{fc_args["username"]}/',

        # Output: where to save the report
        output_dir='reports/latest_game/',

        # Generate reports at turns 10, 25, and 50
        report_turns=[10, 25, 50],

        # Enable all implemented sections
        enabled_sections=['overview', 'historical_events', 'economics', 'demographics', 'technology'],

        # Output formats
        formats=['html'],

        # Visualization settings
        plot_style='seaborn',
        dpi=150
    )

    # Create generator and generate reports
    print("Initializing World Report Generator...")
    generator = ReportGenerator(report_config)

    print("Validating configuration...")
    if not generator.validate_config():
        print("Configuration validation failed!")
        return 1

    print("Configuration validated successfully!")
    print()
    print("Generating reports...")
    generator.generate_reports()

    print()
    print("="*60)
    print("WORLD REPORTS GENERATED!")
    print("="*60)
    print(f"\nReports saved to: {report_config.output_dir}")
    print("\nOpen the HTML files in your browser to view the reports.")

    return 0

if __name__ == '__main__':
    main()
