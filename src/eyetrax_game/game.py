"""
Main game engine for Gaze Tracking Game
"""

from __future__ import annotations

import time
from typing import Tuple

import cv2
import numpy as np
from eyetrax.filters import KalmanSmoother, KalmanEMASmoother
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
            self.smoother = KalmanEMASmoother(ema_alpha=0.9)
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

    def set_pattern(self, pattern_type: PatternType)-> None:
        """set the current pattern"""
        self.current_pattern = create_pattern(
            pattern_type,
            self.screen_width,
            self.screen_height,
            thickness = 5
        )
        self.completion_ratio = 0.0
        self.gaze_on_path_count = 0
        self.gaze_off_path_count = 0

    def update(self, gaze_x: int, gaze_y:int, blink_detected: bool) -> dict:
        """
        Update game state based on gaze position

        Args:
            :param gaze_x: X coordinate of gaze prediction
            :param gaze_y: Y coordinate of gaze prediction
            :param blink_detected: Whether user is blinking
        :return:
            Dictionary with game state updates
        """
        if self.start_time is None:
            self.start_time = time.time()
        self.game_time = time.time() - self.start_time
        if self.current_pattern is None:
            return{"completion": 0.0, "score": 0}

        # Filter gaze position
        x_filt, y_filt = self.smoother.step(gaze_x, gaze_y)

        # Check gaze is on pattern path
        pattern_points = self.current_pattern.get_points(100) # Sample 100 points
        distances = [
            np.hypot(x_filt - px, y_filt- py) for px,py in pattern_points
        ]
        min_distance = min(distances)

        # Track gaze on/off path
        if min_distance < self.proximity_threshold:
            self.gaze_on_path_count += 1
            self.gaze_off_path_count = 0
        else:
            self.gaze_off_path_count += 1
            self.gaze_on_path_count = 0

        # Update completion based on continuous proximity to pattern
        # completion increases when gaze stays on path
        if self.gaze_on_path_count > 5: # After 5 frames on path
            increment = 0.001 * (1.0 - min_distance / self.proximity_threshold)
            self.completion_ratio = min( 1.0, self.completion_ratio + increment)

        # Level up when pattern complete
        if self.completion_ratio >= 1.0:
            self.score += 100* self.level
            self.level += 1
            self.set_pattern(PatternType.INFINITY) # Reset pattern

        return {
            "completion": self.completion_ratio,
            "score": self.score,
            "level": self.level,
            "gaze_x": x_filt,
            "gaze_y": y_filt,
            "min_distance" : min_distance,
            "on_path": min_distance < self.proximity_threshold,
        }

    def draw(self, canvas: np.ndarray)->np.ndarray:
        """
        Draw game state on canvas
        Args:
            :param canvas: OpenCV image to draw on
        :return:
            Updated canvas
        """
        if self.current_pattern is None:
            return canvas

        # Draw pattern background ( unfilled )
        cv2.polylines(
            canvas,
            [np.array(self.current_pattern.get_points(200), dtype=np.int32)],
            False,
            (100, 100, 100),
            1
        )
        # Draw pattern fill ( completed part )
        fill_color = (0,255,0) # Green for on track
        if self.gaze_off_path_count > 10:
            fill_color = (0,165,255) # Orange for off track
        self.current_pattern.draw_partial(canvas, self.completion_ratio, fill_color)

        # Draw HUD
        cv2.putText(
            canvas,
            f"Level:{self.level}",
            (50,50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (0,255,0),
            2
        )

        cv2.putText(
            canvas,
            f"Completion: {self.completion_ratio*100:.1f}%",
            (50,150),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0,255,0),
            2
        )
        cv2.putText(
            canvas,
            f"Time: {self.game_time:.1f}s",
            (50,200),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0,255,0),
            2
        )

        return canvas