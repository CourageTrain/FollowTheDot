"""
Visual patterns that fill up as the user follows them with their eyes
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Tuple
import cv2
import numpy as np


class PatternType(Enum):
    """"Available pattern types."""
    INFINITY = "infinity"
    SPIRAL = "spiral"
    CIRCLE = "circle"
    WAVE = "wave"
    LISSAJOUS = "lissajous"

class Pattern(ABC):
    """Base class for gaze-tracking patterns"""
    def __init__(self, screen_width: int, screen_height: int, thickness: int = 5):
        """
        Initialize pattern
        Args:
            :param screen_width: Screen width in px
            :param screen_height: Screen height in px
            :param thickness: line thickness in px
        Returns:
            None
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.thickness = thickness
        self.center_x = screen_width // 2
        self.center_y = screen_height // 2

    @abstractmethod
    def get_points(self, num_points: int = 1000)-> list[Tuple[int, int]]:
        """
        Generate pattern path points.
        Args:
            :param num_points: Number of points to generate

        :return:
            List of (x, y) tuples representing the pattern path.
        """
        pass

    @abstractmethod
    def draw_partial(
            self,
            canvas: np.ndarray,
            completion_ratio: float,
            color: Tuple[int, int, int] = (0, 255,0),
                     ):
        """
        Draw pattern partially filled

        Args:
            :param canvas: OpenCV image array to draw on.
            :param completion_ratio: How much of the pattern to draw ( 0.0 to 1.0 ).
            :param color: BGR color tuple.
        :return:
            None
        """
        pass

    def draw_target_point(
            self,
            canvas: np.ndarray,
            x: int,
            y: int,
            radius: int = 20,
            color: Tuple[int, int, int] = (0,0,255)
                          ):
        cv2.circle(canvas, (x,y), radius, color, -1)
        cv2.circle(canvas, (x,y), radius, (255,255,255), 2) # white border

class InfinityPattern(Pattern):
    """Infinity symbol figure-8 pattern"""

    def get_points(self, num_points: int = 1000)-> list[Tuple[int, int]]:
        """Generate infinity symbol points"""
        points = []
        scale_x = self.screen_width * 0.3
        scale_y = self.screen_height * 0.25

        for i in range(num_points):
            t = ( i / num_points) * ( 2 * np.pi)

            # inifinity symbol parametric equations
            x = scale_x * np.cos(t) / ( 1 + np.sin(t) ** 2)
            y = scale_y * np.sin(t) * np.cos(t) / ( 1 + np.sin(t) ** 2)

            points.append((
                int(self.center_x + x),
                int(self.center_y + y)
            ))

        return points

    
