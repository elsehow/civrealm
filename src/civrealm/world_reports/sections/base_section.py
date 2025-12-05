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

    def _get_player_name(self, player_id: int, state: Dict) -> str:
        """Get player name from state

        Args:
            player_id: Player ID
            state: Game state dict

        Returns:
            Player name or default
        """
        players = self._get_player_info(state)
        if player_id in players and isinstance(players[player_id], dict):
            return players[player_id].get('name', f'Player {player_id}')
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
