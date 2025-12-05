"""Section 2: Major Historical Events

Tracks city founding, conquests, and other major events throughout the game.
"""

from typing import Dict, List
from .base_section import BaseSection, SectionData
from ..utils.event_detector import EventDetector, GameEvent


class HistoricalEventsSection(BaseSection):
    """Generate historical events section"""

    def __init__(self):
        super().__init__('historical_events')

    def generate(
        self,
        states: Dict[int, Dict],
        config,
        data_loader,
        visualizer
    ) -> SectionData:
        """Generate historical events section

        Args:
            states: Dict mapping turn numbers to game states
            config: ReportConfig instance
            data_loader: DataLoader instance
            visualizer: MapVisualizer instance

        Returns:
            SectionData with events table and mini-maps
        """
        detector = EventDetector()
        all_events: List[GameEvent] = []

        # Sort turns
        sorted_turns = sorted(states.keys())

        # Detect events by comparing consecutive states
        prev_state = None
        for turn in sorted_turns:
            curr_state = states[turn]
            events = detector.detect_all_events(prev_state, curr_state, turn)
            all_events.extend(events)
            prev_state = curr_state

        # Generate content
        images = {}

        # Section 2.1: City Events
        city_events = [e for e in all_events if e.event_type in
                      ['city_founded', 'city_conquered', 'city_destroyed']]

        html_parts = []
        html_parts.append('<h2>2. Major Historical Events</h2>')
        html_parts.append('<h3>2.1 City Founding and Conquest</h3>')

        if city_events:
            # Create events table
            table_rows = []
            for event in city_events:
                turn_str = f"Turn {event.turn}"
                event_type = event.event_type.replace('_', ' ').title()
                description = event.description

                # Add location if available
                if event.location:
                    x, y = event.location
                    description += f" at ({x}, {y})"

                table_rows.append([turn_str, event_type, description])

            events_table = self._format_html_table(
                headers=['Turn', 'Event Type', 'Description'],
                rows=table_rows,
                caption='City Events Throughout History'
            )
            html_parts.append(events_table)

            # Generate mini-maps for significant city events (limit to first 10)
            significant_events = [e for e in city_events
                                if e.event_type in ['city_founded', 'city_conquered']][:10]

            if significant_events:
                html_parts.append('<h4>Event Locations</h4>')
                html_parts.append('<div class="mini-maps-grid">')

                for idx, event in enumerate(significant_events):
                    if event.location and event.turn in states:
                        x, y = event.location
                        state = states[event.turn]

                        # Generate mini-map
                        img_name = f'event_{idx}_turn{event.turn}'
                        title = f"Turn {event.turn}: {event.metadata.get('city_name', 'City')}"

                        try:
                            img_buf = visualizer.render_mini_map(
                                map_state=state.get('map', {}),
                                player_state=state.get('player', {}),
                                center_x=x,
                                center_y=y,
                                radius=8,
                                title=title
                            )
                            images[img_name] = img_buf

                            html_parts.append(f'<div class="mini-map">')
                            html_parts.append(f'<img src="{img_name}.png" alt="{title}"/>')
                            html_parts.append(f'<p class="caption">{event.description}</p>')
                            html_parts.append('</div>')
                        except Exception as e:
                            print(f"Warning: Failed to generate mini-map for event {idx}: {e}")

                html_parts.append('</div>')
        else:
            html_parts.append('<p>No city events recorded.</p>')

        # Section 2.2: Territorial Control (if we have map data)
        if states:
            html_parts.append('<h3>2.2 Territorial Control</h3>')

            # Generate territory maps at key turns
            max_turn = max(states.keys())
            snapshot_turns = [1, max_turn // 2, max_turn]
            snapshot_turns = [t for t in snapshot_turns if t in states]

            if snapshot_turns:
                html_parts.append('<div class="territory-maps">')

                for turn in snapshot_turns:
                    state = states[turn]
                    img_name = f'territory_turn{turn}'

                    try:
                        img_buf = visualizer.render_territory_map(
                            map_state=state.get('map', {}),
                            player_state=state.get('player', {}),
                            title=f"Territorial Control - Turn {turn}",
                            highlight_cities=True,
                            show_legend=True
                        )
                        images[img_name] = img_buf

                        html_parts.append(f'<div class="territory-map">')
                        html_parts.append(f'<img src="{img_name}.png" alt="Territory at turn {turn}"/>')
                        html_parts.append('</div>')
                    except Exception as e:
                        print(f"Warning: Failed to generate territory map for turn {turn}: {e}")

                html_parts.append('</div>')

        # Technology and government events
        tech_events = [e for e in all_events if e.event_type == 'tech_discovered']
        gov_events = [e for e in all_events if e.event_type == 'government_change']

        if tech_events:
            html_parts.append('<h3>2.3 Major Technological Advances</h3>')
            tech_rows = []
            for event in tech_events[:20]:  # Limit to first 20
                turn_str = f"Turn {event.turn}"
                player_name = self._get_player_name(event.player_id, states.get(event.turn, {}))
                tech_rows.append([turn_str, player_name, event.description])

            tech_table = self._format_html_table(
                headers=['Turn', 'Civilization', 'Discovery'],
                rows=tech_rows,
                caption='Major Technological Discoveries'
            )
            html_parts.append(tech_table)

        if gov_events:
            html_parts.append('<h3>2.4 Government Changes</h3>')
            gov_rows = []
            for event in gov_events:
                turn_str = f"Turn {event.turn}"
                gov_rows.append([turn_str, event.description])

            gov_table = self._format_html_table(
                headers=['Turn', 'Change'],
                rows=gov_rows,
                caption='Government Transitions'
            )
            html_parts.append(gov_table)

        content = '\n'.join(html_parts)

        return SectionData(
            title='Major Historical Events',
            content=content,
            images=images,
            metadata={
                'total_events': len(all_events),
                'city_events': len(city_events),
                'tech_events': len(tech_events),
                'gov_events': len(gov_events)
            }
        )
