"""
Calibration UI
"""
import traceback

from eyetrax.calibration import run_9_point_calibration
from eyetrax.gaze import GazeEstimator

def calibrate_for_game(camera_index: int = 0) -> GazeEstimator:
    """
    Run Calibration and return calibrated GazeEstimator
    :param
        camera_index:  Camera index to use ( default = 0 )
    :return:
        Calibrated GazeEstimator instance.
    """
    print("="*60)
    print("EYE TRACKER GAME - CALIBRATION")
    print("Look at each point as it appears on screen")
    print("Press ESC to cancel at any time")
    print ("="*60)

    try:
        estimator = GazeEstimator()
        run_9_point_calibration(estimator, camera_index = camera_index)
    except Exception as e:
        print(f"Error in EyeTrax: {e}")
        traceback.print_exc()
        return None
    return estimator