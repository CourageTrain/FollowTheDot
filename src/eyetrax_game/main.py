""""
Main entry point for eye tracker game
"""

import argparse
import sys
import traceback

import cv2
import numpy as np

from .calibration import calibrate_for_game
from eyetrax.utils.screen import get_screen_size
from .game import Game
from .patterns import PatternType

def main():
    """Run the eye tracker game"""
    parser = argparse.ArgumentParser(description = "Eye Tracker game using EyeTrax")
    parser.add_argument(
        "--camera",
        type = int,
        default = 0,
        help = "Camera index ( default 0 )"
    )
    parser.add_argument(
        "--pattern",
        type = str,
        choices = ["infinity", "spiral", "circle", "wave", "lissajous"],
        default = "infinity",
        help = "Starting pattern ( default infinity"
    )
    parser.add_argument(
        "--calibration",
        type = str,
        choices = ["9p", "5p", "dense_grid"],
        default = "9p",
        help = "9 Point calibration pattern"
    )
    parser.add_argument(
        "--no-adaptive",
        action="store_true",
        help = "Run in fullscreen mode"
    )
    parser.add_argument(
        "--fullscreen",
        action="store_true",
        help="Run in fullscreen mode"
    )
    args = parser.parse_args()

    # Calibrate
    try:
        gaze_estimator = calibrate_for_game(camera_index=args.camera, calibration_pattern = args.calibration)
    except KeyboardInterrupt:
        print("\n  Calibration cancelled by user")
        sys.exit(1)

    # Get screen size
    # screen = cv2.setWindowImageProcessor()

    screen_width = 1920
    screen_height = 1080
    try:
        screen_width, screen_height = get_screen_size()
    except ImportError as e:
        print("Import Error: ScreenInfo - can't be imported")
        print(f"Import Error: {e}")
        traceback.print_exc()

    # Create game
    game = Game(
        gaze_estimator,
        screen_width = screen_width,
        screen_height = screen_height,
        use_adaptive_filter = not args.no_adaptive,
    )

    # Set starting pattern
    pattern_map = {
        "infinity": PatternType.INFINITY,
        "spiral": PatternType.SPIRAL,
        "circle" : PatternType.CIRCLE,
        "wave": PatternType.WAVE,
        "lissajous": PatternType.LISSAJOUS
    }

    game.set_pattern(pattern_map[args.pattern])

    # Open camera
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"ERROR: Could not open camera {args.camera}")
        sys.exit(1)

    # Create window
    window_name = "Eye Trax Game"
    cv2.namedWindow(window_name)
    if args.fullscreen:
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # UI
    print("\n"+"="*60)
    print("GAME STARTED")
    print("="*60)
    print("Follow the green pattern with your eyes")
    print("Press 'q' to quit, 'r' to reset, 'n' for next pattern")
    print()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("ERROR: Failed to read frame from camera")
                break
            # Extract gaze
            features, blink_detected = gaze_estimator.extract_features(frame)

            # Create canvas
            canvas = np.zeros((screen_height, screen_width, 3), dtype = np.uint8)
            canvas[:] = (20,20,20)

            if features is not None and not blink_detected:
                gaze_x, gaze_y = gaze_estimator.predict(np.array([features]))[0]
                gaze_x, gaze_y = int(gaze_x), int(gaze_y)

                #Update game
                state = game.update(gaze_x, gaze_y, blink_detected)

                # Draw gaze cursor
                cv2.circle(canvas, (gaze_x, gaze_y), 15, (0, 255, 255), -1)
                cv2.circle(canvas, (gaze_x, gaze_y), 15, (255, 255, 0), 2)
            else:
                # Blink or no face detected
                state = game.update(-1, -1, True)
                cv2.putText(
                    canvas,
                    "Waiting for face detection...",
                    (screen_width // 2 - 200, screen_height // 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 0, 255),
                    2
                )
            # Draw game
            canvas = game.draw(canvas)

            # Display
            cv2.imshow(window_name, canvas)

            # Handle input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\n Game quit by user")
                break
            elif key == ord('r'):
                print("Resetting pattern .... ")
                game.set_pattern(PatternType.INFINITY)
            elif key == ord('n'):
                print("Loading next pattern...")
                patterns = list(PatternType)
                current_idx = patterns.index(
                    [pt for pt in patterns if pt.value == game.current_pattern.__class__.__name__.replace("Pattern","").lower()][0]
                )
                next_pattern = patterns[(current_idx + 1)%len(patterns)]
                game.set_pattern(next_pattern)
    except KeyboardInterrupt:
        print("\n game interrupted by user")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Game ended")
        print(f"Final score: {game.score}")
        print(f"Final level: {game.level}")

if __name__ == "__main__":
    main()
