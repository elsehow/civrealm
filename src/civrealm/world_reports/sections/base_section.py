"""Base class for report sections"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List
from io import BytesIO


@dataclass
class SectionData:
    """Data container for a report section

    Attributes:
        title: Section title
        content: HTML content for the section
        images: Dict mapping image names to BytesIO buffers
        metadata: Additional section metadata
    """
    title: str
    content: str
    images: Dict[str, BytesIO]
    metadata: Dict[str, Any]


class BaseSection(ABC):
    """Abstract base class for report sections

    All report sections should inherit from this class and implement
    the generate() method.
    """

    def __init__(self, section_name: str):
        """Initialize section

        Args:
            section_name: Unique identifier for this section
        """
        self.section_name = section_name

    @abstractmethod
    def generate(
        self,
        states: Dict[int, Dict],
        config: Any,
        data_loader: Any,
        visualizer: Any
    ) -> SectionData:
        """Generate section content

        Args:
            states: Dict mapping turn numbers to game states
            config: ReportConfig instance
            data_loader: DataLoader instance for accessing additional data
            visualizer: MapVisualizer instance for generating images

        Returns:
            SectionData containing the generated content and images
        """
        pass

    def _get_player_info(self, state: Dict) -> Dict[int, Dict]:
        """Extract player information from state

        Args:
            state: Game state dict

        Returns:
            Dict mapping player IDs to player info
        """
        return state.get('player', {})

    def _get_nation_name(self, nation_id: int, state: Dict) -> str:
        """Get nation/civilization name from nation ID

        Args:
            nation_id: Nation ID
            state: Game state dict

        Returns:
            Nation name or empty string if not found
        """
        if 'rules' in state and 'nations' in state['rules']:
            nations = state['rules']['nations']
            nation_key = str(nation_id)  # Nations dict uses string keys
            if nation_key in nations:
                return nations[nation_key].get('name', '')
        return ''

    def _get_player_name(self, player_id: int, state: Dict) -> str:
        """Get player display name from state

        Returns player name with civilization name if available.
        Format: "Player Name (Civilization)" or just "Player Name" if civ unknown.

        Args:
            player_id: Player ID
            state: Game state dict

        Returns:
            Player display name
        """
        players = self._get_player_info(state)
        if player_id in players and isinstance(players[player_id], dict):
            player = players[player_id]
            player_name = player.get('name', f'Player {player_id}')

            # Try to get civilization name
            nation_id = player.get('nation')
            if nation_id is not None:
                civ_name = self._get_nation_name(nation_id, state)
                if civ_name:
                    return f"{player_name} ({civ_name})"

            return player_name
        return f'Player {player_id}'

    def _format_html_table(
        self,
        headers: List[str],
        rows: List[List[Any]],
        caption: str = ""
    ) -> str:
        """Format data as HTML table

        Args:
            headers: List of column headers
            rows: List of row data
            caption: Optional table caption

        Returns:
            HTML table string
        """
        html = ['<table class="data-table">']

        if caption:
            html.append(f'<caption>{caption}</caption>')

        # Headers
        html.append('<thead><tr>')
        for header in headers:
            html.append(f'<th>{header}</th>')
        html.append('</tr></thead>')

        # Rows
        html.append('<tbody>')
        for row in rows:
            html.append('<tr>')
            for cell in row:
                html.append(f'<td>{cell}</td>')
            html.append('</tr>')
        html.append('</tbody>')

        html.append('</table>')
        return '\n'.join(html)
