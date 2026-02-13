"""
Calibration UI
"""
import traceback

from eyetrax.calibration import (run_9_point_calibration, run_5_point_calibration,
                                 run_lissajous_calibration, run_dense_grid_calibration)
from eyetrax.gaze import GazeEstimator

def calibrate_for_game(camera_index: int = 0, calibration_pattern: str = "9p") -> GazeEstimator:
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
        if calibration_pattern == "9p":
            run_9_point_calibration(estimator, camera_index = camera_index)
        elif calibration_pattern == "5p":
            run_5_point_calibration(estimator, camera_index = camera_index)
        elif calibration_pattern == "lissajous":
            run_lissajous_calibration(estimator, camera_index = camera_index)
        elif calibration_pattern == "dense_grid":
            run_dense_grid_calibration(estimator, camera_index = camera_index)
        else:
            print(f"Running default calibration - {calibration_pattern} - is not valid!")
            run_9_point_calibration(estimator, camera_index = camera_index)
    except Exception as e:
        print(f"Error in EyeTrax: {e}")
        traceback.print_exc()
        return None
    return estimator