import argparse


def tuning_type(value):
    allowed_values = ["motion"]
    if value not in allowed_values:
        raise argparse.ArgumentTypeError(
            f"Invalid tuning type: {value}. Valid types are: 'motion'."
        )
    return value


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tuning", help="Tuning mode", type=tuning_type)

    return parser.parse_args()
