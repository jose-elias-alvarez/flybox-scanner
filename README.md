# flybox-scanner

## Setup

First, make sure [Anaconda](https://www.anaconda.com) is installed.

Then, navigate to the project directory and run the following command:

```sh
conda env create --file environment.yml
```

This will create a new environment called `flybox-scanner` containing all the necessary dependencies.

### Start

Activate the environment:

```sh
conda activate flybox-scanner
```

Then, run the script:

```sh
python main.py
```

### Uninstall

To uninstall the environment, run the following command:

```sh
conda env remove --name flybox-scanner
```

## Parameters

### Motion Detection

To tune motion detection parameters, run the following command:

```sh
python main.py --tuning=motion
```

Once you've found a set of parameters that works well, you can save them to `settings.json` using the `Save` button in the UI. The parameters will then be loaded automatically on subsequent runs.

### Other Parameters

Other parameters are currently hard-coded into the following Python source files and must be edited manually:

- `main.py`: controls source and window parameters

### Detection

- `detection/border.py`: controls the detection of borders in frames (used to "crop" the flybox background)
- `detection/grids.py`: controls the detection of wells

### Handlers

- `handlers/debug.py`: controls the display of debug info in the recording window (e.g. wells, flies)
- `handlers/file_interval.py`: controls the output of data into a file at a given interval
- `handlers/frame.py`: controls the handling of detected motion and its conversion into motion events

## Development

### Architecture

UI logic lives in `components/`. The main UI entrypoint is `components/root_window.py`, which is responsible for the main event loop and for mounting and unmounting "state canvases".

Each state canvas is responsible for a specific UI state, as defined in `components/state_manager.py`:

- `components/idle_canvas.py`: initial state, displays a source preview and state transition buttons
- `components/select_webcam_canvas.py`: active when selecting a webcam source
- `components/scan_canvas.py`: active when "scanning" (running grid detection on) the source, allows transitioning to the recording state
- `components/record_canvas.py`: active when recording, shows a (hideable) preview

### Videos

Note that video output is not yet optimized and may differ from webcam output.

- [Fly.mp4](https://drive.google.com/file/d/1q6RSJJIWKrrxvLqLVuanaOrmj1ull6yN/view?usp=share_link)
- [DoubleFly.mp4](https://drive.google.com/file/d/1jw3vVR3u8bQfJR4toDuorEAYqEPXu1Qc/view?usp=share_link)

### VS Code

#### Tasks

The repository contains a `Run` task to run `main.py`. To use it, open the command palette and select `Tasks: Run Task`. Then, select `Run`.

#### Interpreter

Upon creating the new environment, VS Code should prompt you to use it for the current workspace. If not, use the `Python: Select Interpreter` command to select the interpreter at `./env/bin/python.`
