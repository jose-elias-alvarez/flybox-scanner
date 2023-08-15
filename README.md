# flybox-scanner

## Setup

First, make sure [Anaconda](https://www.anaconda.com) is installed.

Then, navigate to the project directory and run the following command:

```sh
conda env create --file environment.yml
```

This will create a new environment called `flybox-scanner` containing all the necessary dependencies.

## Start

Activate the environment:

```sh
conda activate flybox-scanner
```

Then, run the script:

```sh
python main.py
```

## Uninstall

To uninstall the environment, run the following command:

```sh
conda env remove --name flybox-scanner
```

## Development

### Videos

Note that video output is not yet optimized and may differ from webcam output.

- [Fly.mp4](https://drive.google.com/file/d/1q6RSJJIWKrrxvLqLVuanaOrmj1ull6yN/view?usp=share_link)
- [DoubleFly.mp4](https://drive.google.com/file/d/1jw3vVR3u8bQfJR4toDuorEAYqEPXu1Qc/view?usp=share_link)

### VS Code

#### Tasks

The repository contains a `Run` task to run `main.py`. To use it, open the command palette and select `Tasks: Run Task`. Then, select `Run`.

#### Interpreter

Upon creating the new environment, VS Code should prompt you to use it for the current workspace. If not, use the `Python: Select Interpreter` command to select the interpreter at `./env/bin/python.`
