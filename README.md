# Traffic Management and Vehicle Counting System

This repository currently includes a working traffic signal simulation built with `pygame`.

## Project Structure

- `traffic_simulation/`: main simulation code
- `traffic_simulation/assets/`: background, vehicles, and signal images
- `traffic_simulation/model_weights/`: YOLO model weights used by the experimental detection script

## Quick Start

From the project root:

```bash
/usr/bin/python3 -m venv .venv39
source .venv39/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python traffic_simulation/simulation.py
```

## Recommended Environment

- macOS with `/usr/bin/python3` (`Python 3.9`) is the most reliable setup for this project.
- Use a virtual environment so package installs stay local to the repo.

## Running the Simulation

After the environment is created once:

```bash
cd /Users/deep/Documents/Traffic-management-system/Traffic-management-and-vehicle-counting-system
source .venv39/bin/activate
python traffic_simulation/simulation.py
```

## Troubleshooting

- If `pygame` fails to install, make sure you are using `/usr/bin/python3` and not a newer system Python like `3.14`.
- If the window opens but looks scaled incorrectly, close it and rerun the command after pulling the latest changes.
- If the environment gets messy, remove `.venv39`, recreate it, and reinstall from `requirements.txt`.

## Notes for Developers

- The main maintained entrypoint is `traffic_simulation/simulation.py`.
- Asset paths are resolved relative to the script, so you can run the simulation from the repo root.
- The older vehicle-counting helper script inside `traffic_simulation/assets/` is still experimental and may need additional files before it runs end-to-end.
