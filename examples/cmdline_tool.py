import argparse
import json
import sys

import cfglib


class CmdlineToolConfig(cfglib.utils.InitializableConfig):
    @staticmethod
    def parse_cmdline_arguments() -> dict:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--config-file', type=str,
            required=False, default=None,
            help='Path to a json-encoded config file',
        )
        parser.add_argument(
            '--message', type=str,
            required=False, default=None,
            help='The message that will be printed',
        )

        parsed_args = parser.parse_args()
        config_items = {
            k: v
            for k, v in parsed_args.__dict__.items()
            if v is not None
        }
        return config_items

    @staticmethod
    def parse_config_file(config_file) -> dict:
        config_data = json.load(config_file)
        return config_data

    @classmethod
    def build_config(cls, config_file=None) -> cfglib.Config:
        default_config = cfglib.DictConfig({
            'message': 'Hello!',
            'config_file': None,
        })

        env_config = cfglib.EnvConfig(prefix='EXAMPLE_')

        cmdline_config = cfglib.DictConfig(cls.parse_cmdline_arguments())

        config = cfglib.CompositeConfig([
            default_config,
            env_config,
            *([cls.parse_config_file(config_file)] if config_file else []),
            cmdline_config,
        ])
        return config


# Main program
def main():
    config = CmdlineToolConfig()

    # if we can do complex work (such as querying a database)
    # to augment our config, do that and reinitialize it with new data
    if config['config_file']:
        with open(config['config_file']) as config_file:
            CmdlineToolConfig.initialize(config_file)
            config = CmdlineToolConfig()

    print(f'Config: {config}', file=sys.stderr)

    message = config['message']
    print(message)


if __name__ == '__main__':
    main()
