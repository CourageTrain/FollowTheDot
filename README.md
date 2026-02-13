## clone or create project
mkdir eyetrax-game
cd eyetrax-game

## create virtual environment
python -m venv venv
source venv/bin/activate # On windows : venv\Scripts\activate

## install in editable mode 
pip install -e

## Or install requirements directly
pip install -r requirements.txt

## run game
eyetrax-game --pattern infinity

## Options
eyetrax-game --pattern spiral --camera 0
eyetrax-game --pattern lissajous --fullscreen
eyetrax-game --pattern circle --no-adaptive
