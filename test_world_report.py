#!/usr/bin/env python3
"""Test script for world report generation

This script generates a world report from the 50-turn game data
we collected earlier.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from civrealm.world_reports import ReportGenerator, ReportConfig


def main():
    """Generate test world report"""

    # Configuration
    config = ReportConfig(
        # Input: where our 50-turn game recording is stored
        recording_dir='logs/recordings/myagent2/',

        # Output: where to save the report
        output_dir='reports/test_game_fullterrain/',

        # Generate reports at turns 10, 25, 30 (32 is latest so far)
        report_turns=[10, 25, 50],

        # Enable the sections we've implemented
        enabled_sections=['overview', 'historical_events', 'economics', 'demographics', 'technology'],

        # Output formats
        formats=['html'],  # Start with HTML only

        # Visualization settings
        plot_style='seaborn',
        dpi=150
    )

    # Create generator
    print("Initializing World Report Generator...")
    generator = ReportGenerator(config)

    # Validate configuration
    print("\nValidating configuration...")
    if not generator.validate_config():
        print("Configuration validation failed!")
        return 1

    print("\nConfiguration validated successfully!")

    # Generate reports
    print("\nGenerating reports...")
    generator.generate_reports()

    print("\n" + "="*60)
    print("SUCCESS!")
    print("="*60)
    print(f"\nReports have been generated in: {config.output_dir}")
    print("\nGenerated files:")
    print(f"  - turn_010_report.html")
    print(f"  - turn_025_report.html")
    print(f"  - turn_030_report.html")
    print("\nOpen any HTML file in your browser to view the report.")

    return 0


if __name__ == '__main__':
    sys.exit(main())
