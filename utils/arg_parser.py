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
    parser.add_argument("--keep-defaults", help="Keep defaults", type=bool)
    parser.add_argument("--silent", help="Silent", type=bool)

    # return as dict
    return vars(parser.parse_args())
