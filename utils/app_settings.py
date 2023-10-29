import json
from os import environ
from tkinter import messagebox


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
    differ from those in d2. Keys not present in both dictionaries
    are ignored.
    """
    result = {}
    for key in d1:
        if key in d2:
            if isinstance(d1[key], dict) and isinstance(d2[key], dict):
                nested_diff = diff_dicts(d1[key], d2[key])
                if nested_diff:
                    result[key] = nested_diff
            elif d1[key] != d2[key]:
                result[key] = d1[key]
    return result


class AppSettings:
    env_overrides = {
        "video.source": "SOURCE",
        "recording.output_file": "OUTPUT_FILE",
        "recording.interval": "INTERVAL",
    }
    default_settings_file = "default_settings.json"
    settings_file = "settings.json"

    def __init__(self, keep_defaults=False):
        # first, load default settings from default_settings.json
        with open(self.default_settings_file, "r") as default_settings_file:
            self.settings = json.load(default_settings_file)
        if not keep_defaults:
            # then, check if settings.json exists and merge with defaults
            try:
                with open(self.settings_file, "r") as settings_file:
                    overrides = json.load(settings_file)
                    self.settings = merge_json(self.settings, overrides)
            except FileNotFoundError:
                pass

    def __str__(self):
        return json.dumps(self.settings, indent=2)

    def get(self, key: str):
        # try to resolve from environment variables first
        if key in self.env_overrides:
            env_var = self.env_overrides[key]
            if env_var in environ:
                return environ[env_var]

        keys = key.split(".")
        value = self.settings
        for key in keys:
            try:
                value = value[key]
            except KeyError:
                return None
        return value

    def set(self, key: str, value):
        keys = key.split(".")
        target = self.settings
        for key in keys[:-1]:
            try:
                target = target[key]
            except KeyError:
                return None
        target[keys[-1]] = value

    def save(self, show_message=True):
        with open(self.default_settings_file, "r") as default_settings_file:
            default_settings = json.load(default_settings_file)
        # diff the current settings with the default settings,
        # so we can save only the settings that differ from the defaults
        new_settings = diff_dicts(self.settings, default_settings)
        with open(self.settings_file, "w") as settings_file:
            json.dump(new_settings, settings_file, indent=2)

        if show_message:
            messagebox.showinfo("Success", "Successfully saved settings")
