"""Visualization utilities for generating maps and charts"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
from typing import Dict, List, Optional, Tuple
from io import BytesIO
import base64


# Color palette for player civilizations
PLAYER_COLORS = [
    '#FF6B6B',  # Red
    '#4ECDC4',  # Teal
    '#45B7D1',  # Blue
    '#FFA07A',  # Light Salmon
    '#98D8C8',  # Mint
    '#F7DC6F',  # Yellow
    '#BB8FCE',  # Purple
    '#85C1E2',  # Sky Blue
    '#F8B739',  # Orange
    '#52B788',  # Green
]

# Terrain colors mapped to terrain IDs
# Based on TERRAIN_NAMES from freeciv/map/map_const.py:
# ['Inaccessible', 'Lake', 'Ocean', 'Deep Ocean', 'Glacier',
#  'Desert', 'Forest', 'Grassland', 'Hills', 'Jungle',
#  'Mountains', 'Plains', 'Swamp', 'Tundra']
TERRAIN_COLORS_BY_ID = {
    0: '#000000',    # Inaccessible - Black
    1: '#4A90E2',    # Lake - Blue
    2: '#1E3A5F',    # Ocean - Dark Blue
    3: '#0A1929',    # Deep Ocean - Darker Blue
    4: '#ECEFF1',    # Glacier - White/Light Gray
    5: '#F4E7C6',    # Desert - Tan
    6: '#2E7D32',    # Forest - Dark Green
    7: '#7CB342',    # Grassland - Green
    8: '#8D6E63',    # Hills - Brown
    9: '#1B5E20',    # Jungle - Very Dark Green
    10: '#5D4037',   # Mountains - Dark Brown
    11: '#D4C07A',   # Plains - Yellow/Tan
    12: '#4A5F4A',   # Swamp - Dark Gray-Green
    13: '#CFD8DC',   # Tundra - Light Gray
    255: '#FFFFFF',  # Unknown - White
}


class MapVisualizer:
    """Generate map visualizations from game state data"""

    def __init__(self, dpi: int = 150, style: str = 'seaborn'):
        """Initialize visualizer

        Args:
            dpi: Resolution for generated images
            style: Matplotlib style to use
        """
        self.dpi = dpi
        try:
            plt.style.use(style)
        except:
            pass  # Use default if style not available

    def render_territory_map(
        self,
        map_state: Dict,
        player_state: Dict,
        title: str = "Territory Map",
        highlight_cities: bool = True,
        show_legend: bool = True
    ) -> BytesIO:
        """Render a territory control map

        Args:
            map_state: Map state dict with tile_owner, terrain, etc.
            player_state: Player state dict for civilization info
            title: Map title
            highlight_cities: Whether to mark city locations
            show_legend: Whether to show player legend

        Returns:
            BytesIO buffer containing PNG image
        """
        # Parse terrain and tile ownership
        terrain = self._parse_terrain(map_state)
        tile_owner = self._parse_tile_owner(map_state, 80, 50)

        # Get actual dimensions from parsed array
        ysize, xsize = tile_owner.shape

        # Create figure
        fig, ax = plt.subplots(figsize=(16, 10), dpi=self.dpi)

        # Render terrain as base layer if available
        if terrain is not None:
            # Create terrain color map
            terrain_colors = [TERRAIN_COLORS_BY_ID.get(i, '#FFFFFF') for i in range(256)]
            terrain_cmap = ListedColormap(terrain_colors)

            # Render terrain
            ax.imshow(terrain, cmap=terrain_cmap, vmin=0, vmax=255,
                     interpolation='nearest', aspect='auto', alpha=1.0)

            # Overlay player territories with semi-transparency
            # Create a masked array where -1 (unowned) is transparent
            territory_mask = np.ma.masked_where(tile_owner == -1, tile_owner)

            # Create color map for players (transparent for unowned)
            player_colors_list = PLAYER_COLORS[:len(player_state)]
            territory_cmap = ListedColormap(player_colors_list)

            ax.imshow(territory_mask, cmap=territory_cmap, vmin=0, vmax=len(player_state)-1,
                     interpolation='nearest', aspect='auto', alpha=0.3)
        else:
            # Fallback: just show territory ownership (old behavior)
            colors = ['#FFFFFF'] + PLAYER_COLORS[:len(player_state)]
            cmap = ListedColormap(colors)
            ax.imshow(tile_owner, cmap=cmap, vmin=-1, vmax=len(player_state)-1,
                     interpolation='nearest', aspect='auto')

        # Add cities if requested
        if highlight_cities and 'city_owner' in map_state:
            self._add_cities(ax, map_state, xsize, ysize)

        # Add grid
        ax.grid(True, which='both', color='gray', alpha=0.2, linewidth=0.5)
        ax.set_xticks(np.arange(0, xsize, 5))
        ax.set_yticks(np.arange(0, ysize, 5))

        # Labels
        ax.set_xlabel('X Coordinate')
        ax.set_ylabel('Y Coordinate')
        ax.set_title(title, fontsize=14, fontweight='bold')

        # Legend with player names
        if show_legend and player_state:
            self._add_player_legend(ax, player_state)

        plt.tight_layout()

        # Save to buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=self.dpi, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)

        return buf

    def render_mini_map(
        self,
        map_state: Dict,
        player_state: Dict,
        center_x: int,
        center_y: int,
        radius: int = 10,
        title: str = "Location"
    ) -> BytesIO:
        """Render a small focused map around a specific location

        Args:
            map_state: Map state dict
            player_state: Player state dict
            center_x: X coordinate of center
            center_y: Y coordinate of center
            radius: Tiles to show in each direction
            title: Map title

        Returns:
            BytesIO buffer containing PNG image
        """
        # Parse terrain and tile ownership
        terrain = self._parse_terrain(map_state)
        tile_owner = self._parse_tile_owner(map_state, 80, 50)

        # Get actual dimensions from parsed array
        ysize, xsize = tile_owner.shape

        # Calculate bounds
        x_min = max(0, center_x - radius)
        x_max = min(xsize, center_x + radius + 1)
        y_min = max(0, center_y - radius)
        y_max = min(ysize, center_y + radius + 1)

        # Crop both terrain and tile ownership
        cropped_owner = tile_owner[y_min:y_max, x_min:x_max]

        # Create figure
        fig, ax = plt.subplots(figsize=(8, 6), dpi=self.dpi)

        # Render with terrain if available
        if terrain is not None:
            cropped_terrain = terrain[y_min:y_max, x_min:x_max]

            # Terrain base layer
            terrain_colors = [TERRAIN_COLORS_BY_ID.get(i, '#FFFFFF') for i in range(256)]
            terrain_cmap = ListedColormap(terrain_colors)
            ax.imshow(cropped_terrain, cmap=terrain_cmap, vmin=0, vmax=255,
                     interpolation='nearest', aspect='auto', alpha=1.0)

            # Territory overlay with transparency
            territory_mask = np.ma.masked_where(cropped_owner == -1, cropped_owner)
            player_colors_list = PLAYER_COLORS[:len(player_state)]
            territory_cmap = ListedColormap(player_colors_list)
            ax.imshow(territory_mask, cmap=territory_cmap, vmin=0, vmax=len(player_state)-1,
                     interpolation='nearest', aspect='auto', alpha=0.3)
        else:
            # Fallback: just show territory
            colors = ['#FFFFFF'] + PLAYER_COLORS[:len(player_state)]
            cmap = ListedColormap(colors)
            ax.imshow(cropped_owner, cmap=cmap, vmin=-1, vmax=len(player_state)-1,
                     interpolation='nearest', aspect='auto')

        # Mark center
        rel_x = center_x - x_min
        rel_y = center_y - y_min
        ax.plot(rel_x, rel_y, 'r*', markersize=15, markeredgecolor='black',
               markeredgewidth=1.5, label='Location')

        # Grid
        ax.grid(True, which='both', color='gray', alpha=0.3, linewidth=0.5)

        # Labels
        ax.set_xlabel(f'X ({x_min}-{x_max})')
        ax.set_ylabel(f'Y ({y_min}-{y_max})')
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.legend()

        plt.tight_layout()

        # Save to buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=self.dpi, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)

        return buf

    def render_line_chart(
        self,
        data: Dict[str, List[Tuple[int, float]]],
        title: str,
        xlabel: str = "Turn",
        ylabel: str = "Value",
        legend_title: str = "Players"
    ) -> BytesIO:
        """Render a line chart for time-series data

        Args:
            data: Dict mapping series name to list of (turn, value) tuples
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            legend_title: Legend title

        Returns:
            BytesIO buffer containing PNG image
        """
        fig, ax = plt.subplots(figsize=(12, 6), dpi=self.dpi)

        for i, (name, points) in enumerate(data.items()):
            if not points:
                continue
            turns, values = zip(*points)
            color = PLAYER_COLORS[i % len(PLAYER_COLORS)]
            ax.plot(turns, values, marker='o', label=name, color=color, linewidth=2)

        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(title=legend_title, loc='best')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=self.dpi, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)

        return buf

    def _parse_tile_owner(self, map_state: Dict, xsize: int, ysize: int) -> np.ndarray:
        """Parse tile_owner array from map state

        Args:
            map_state: Map state dict
            xsize: Map width (will be auto-detected if already 2D)
            ysize: Map height (will be auto-detected if already 2D)

        Returns:
            2D numpy array of owner IDs (-1 for unowned)
        """
        tile_owner_data = map_state.get('tile_owner', [])

        if not tile_owner_data:
            return np.full((ysize, xsize), -1, dtype=int)

        # Check if already 2D (list of lists)
        if isinstance(tile_owner_data, list) and len(tile_owner_data) > 0 and isinstance(tile_owner_data[0], list):
            # Already 2D array
            tile_owner = np.array(tile_owner_data, dtype=int)
        else:
            # Flat array, need to reshape
            tile_owner = np.array(tile_owner_data, dtype=int).reshape(ysize, xsize)

        # Map None/255 to -1 (unowned)
        tile_owner = np.where(tile_owner == 255, -1, tile_owner)

        return tile_owner

    def _parse_terrain(self, map_state: Dict) -> np.ndarray:
        """Parse terrain array from map state

        Returns:
            2D numpy array of terrain type IDs (0-13, 255=unknown)
        """
        terrain_data = map_state.get('terrain', [])

        if not terrain_data:
            return None

        # Check if already 2D (list of lists)
        if isinstance(terrain_data, list) and len(terrain_data) > 0 and isinstance(terrain_data[0], list):
            # Already 2D array
            terrain = np.array(terrain_data, dtype=int)
        else:
            # Flat array - but we don't know dimensions, return None
            return None

        return terrain

    def _add_cities(self, ax, map_state: Dict, xsize: int, ysize: int):
        """Add city markers to map

        Args:
            ax: Matplotlib axes
            map_state: Map state dict
            xsize: Map width (not used if already 2D)
            ysize: Map height (not used if already 2D)
        """
        city_owner_data = map_state.get('city_owner', [])
        if not city_owner_data:
            return

        # Check if already 2D
        if isinstance(city_owner_data, list) and len(city_owner_data) > 0 and isinstance(city_owner_data[0], list):
            city_owner = np.array(city_owner_data, dtype=int)
        else:
            city_owner = np.array(city_owner_data, dtype=int).reshape(ysize, xsize)

        # Find city locations (non-255 values)
        city_locs = np.where(city_owner != 255)

        if len(city_locs[0]) > 0:
            ax.scatter(city_locs[1], city_locs[0], c='black', s=50,
                      marker='s', edgecolors='white', linewidths=1.5,
                      label='Cities', zorder=10)

    def _add_player_legend(self, ax, player_state: Dict):
        """Add player legend to map

        Args:
            ax: Matplotlib axes
            player_state: Player state dict
        """
        patches = []
        for player_id in sorted(player_state.keys()):
            # Handle both string and int player IDs
            if isinstance(player_id, (int, str)):
                pid_int = int(player_id) if isinstance(player_id, str) else player_id
                if pid_int < len(PLAYER_COLORS):
                    player = player_state[player_id]
                    name = player.get('name', f'Player {pid_int}')
                    color = PLAYER_COLORS[pid_int]
                    patches.append(mpatches.Patch(color=color, label=name))

        if patches:
            ax.legend(handles=patches, bbox_to_anchor=(1.05, 1),
                     loc='upper left', borderaxespad=0., title='Civilizations')

    def to_base64(self, buf: BytesIO) -> str:
        """Convert image buffer to base64 string for HTML embedding

        Args:
            buf: BytesIO buffer containing image

        Returns:
            Base64 encoded string
        """
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')
