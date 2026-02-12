from eyetrax.gaze import GazeEstimator
from eyetrax_game.calibration import calibrate_for_game

ge = calibrate_for_game(camera_index = 0)
print("calibrate for game returned:", ge, type(ge))