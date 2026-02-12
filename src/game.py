"""
Main game engine for Gaze Tracking Game
"""

from __future__ import annotations

import time
from typing import Tuple

import cv2
import numpy as np
from eyetrax.filters import AdaptiveKalmanSmoother,KalmanSmoother
from eyetrax.gaze import GazeEstimator

from .patterns import Pattern, PatternType, create_pattern

class Game:
    "Game Engine"
    def __init__(
            self,
            gaze_estimator: GazeEstimator,
            screen_width: int = 1920,
            screen_height: int = 1080,
            use_adaptive_filter: bool = True
    ):
        """
        Initialize Game.

        :param gaze_estimator: Calibrated GazeEstimator instance
        :param screen_width: Screen width in pixels
        :param screen_height: Screen height in pixels
        :param use_adaptive_filter: Use adaptive kalman or kalman smoother
        """
        self.gaze_estimator = gaze_estimator
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Gaze Filter
        if use_adaptive_filter:
            self.smoother = AdaptiveKalmanSmoother(adaptation_rate=0.9)
        else:
            from eyetrax.filters import make_kalman
            kf = make_kalman
            self.smoother=KalmanSmoother(kf)

        # Game state
        self.current_pattern: Pattern | None = None
        self.completion_ratio = 0.0
        self.score = 0
        self.level = 1
        self.game_time = 0.0
        self.start_time: float | None = None

        # Gaze proximity tracking
        self.gaze_on_path_count = 0
        self.gaze_off_path_count = 0
        self.proximity_threshold = 30 # pixels

        