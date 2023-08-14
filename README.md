# flybox-scanner

## Setup

First, make sure [Anaconda](https://www.anaconda.com) is installed.

Then, navigate to the project directory and run the following command:

```sh
conda env create --prefix ./env --file environment.yml
```

## Start

Activate the environment:

```sh
conda activate ./env
```

Then, run the script:

```sh
python main.py
```

## Development

### Videos

Note that video output is not yet optimized and may differ from webcam output.

- [Fly.mp4](https://drive.google.com/file/d/1q6RSJJIWKrrxvLqLVuanaOrmj1ull6yN/view?usp=share_link)
- [DoubleFly.mp4](https://drive.google.com/file/d/1jw3vVR3u8bQfJR4toDuorEAYqEPXu1Qc/view?usp=share_link)

### VS Code

Upon creating the new environment, VS Code should prompt you to use it for the current workspace. If not, use the `Python: Select Interpreter` command to select the interpreter at `./env/bin/python.`
