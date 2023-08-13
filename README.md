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

### VS Code

Upon creating the new environment, VS Code should prompt you to use it for the current workspace. If not, use the `Python: Select Interpreter` command to select the interpreter at `./env/bin/python.`
