import json


def merge_json(default: dict, overrides: dict) -> dict:
    """
    Recursively merges two dictionaries, with the values in `overrides` taking precedence over the values in `default`.

    Args:
        default (dict): The default dictionary to merge.
        overrides (dict): The dictionary to merge with `default`.

    Returns:
        dict: The merged dictionary.
    """
    result = {}
    for key in set(default.keys()).union(overrides.keys()):
        if (
            key in overrides
            and key in default
            and isinstance(default[key], dict)
            and isinstance(overrides[key], dict)
        ):
            result[key] = merge_json(default[key], overrides[key])
        elif key in overrides:
            result[key] = overrides[key]
        else:
            result[key] = default[key]
    return result


def diff_dicts(d1, d2):
    """
    Return a dictionary that contains key-value pairs from d1 that
    differ from those in d2 or don't exist in d2 at all.
    """
    result = {}
    for key in d1:
        if key not in d2:
            result[key] = d1[key]
        elif isinstance(d1[key], dict) and isinstance(d2[key], dict):
            nested_diff = diff_dicts(d1[key], d2[key])
            if nested_diff:
                result[key] = nested_diff
        elif d1[key] != d2[key]:
            result[key] = d1[key]
    return result


class AppSettings:
    def __init__(self):
        self.default_settings_file = "default_settings.json"
        self.settings_file = "settings.json"
        # first, load default settings from default_settings.json
        with open(self.default_settings_file, "r") as default_settings_file:
            self.settings = json.load(default_settings_file)
        # then, check if settings.json exists and merge w/ defaults if so
        try:
            with open(self.settings_file, "r") as settings_file:
                overrides = json.load(settings_file)
                self.settings = merge_json(self.settings, overrides)
        except FileNotFoundError:
            pass

    def get(self, key: str):
        keys = key.split(".")
        value = self.settings
        for key in keys:
            try:
                value = value[key]
            except KeyError:
                raise KeyError(f"Invalid settings key: {key}")
        return value

    def set(self, key: str, value):
        keys = key.split(".")
        target = self.settings
        for key in keys[:-1]:
            try:
                target = target[key]
            except KeyError:
                raise KeyError(f"Invalid settings key: {key}")
        target[keys[-1]] = value

    def save(self):
        with open(self.default_settings_file, "r") as default_settings_file:
            default_settings = json.load(default_settings_file)
        # diff the current settings with the default settings,
        # so we can save only the settings that differ from the defaults
        new_settings = diff_dicts(self.settings, default_settings)
        with open(self.settings_file, "w") as settings_file:
            json.dump(new_settings, settings_file, indent=2)
