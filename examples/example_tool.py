import argparse
import json
import sys

import cfglib
from cfglib.sources.env import EnvConfig


# Config definitions
# These will normally be in a separate module,
# to be imported by the rest of the project like:
# from xyz.config import cfg
def parse_config_file(config_file_path) -> cfglib.DictConfig:
    with open(config_file_path) as config_file:
        return cfglib.DictConfig(json.load(config_file))


class ExampleToolConfig(cfglib.SpecValidatedConfig):
    message = cfglib.StringSetting(default='Hello!')
    config_file = cfglib.StringSetting()


cfg = ExampleToolConfig([
    EnvConfig(prefix='EXAMPLE_'),
])


# Main program
def parse_cmdline_arguments() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config-file', type=str,
        required=False, default=cfglib.MISSING,
        help='Path to a json-encoded config file',
    )
    parser.add_argument(
        '--message', type=str,
        required=False, default=cfglib.MISSING,
        help='The message that will be printed',
    )

    parsed_args = parser.parse_args()
    config_items = {
        k: v
        for k, v in parsed_args.__dict__.items()
        if v is not cfglib.MISSING
    }
    return config_items


def initialize_config():
    cmdline_config = cfglib.DictConfig(parse_cmdline_arguments())
    # Command line arguments shoule be highest priority, so append them to the end
    cfg.subconfigs.append(cmdline_config)

    if cfg.get('config_file'):
        # Load configuration from a config file, if specified
        # Config file's priority is below that of cmdline args, so insert at position 1
        cfg.subconfigs.insert(1, parse_config_file(cfg['config_file']))

    # With the additional configuration sources injected, the end priority order
    # from lowest to highest priority is now:
    # - environment variables
    # - config file
    # - command line arguments

    cfg.validate()


def main():
    initialize_config()
    print(f'Config: {cfg}', file=sys.stderr)

    message = cfg['message']
    print(message)


if __name__ == '__main__':
    main()
