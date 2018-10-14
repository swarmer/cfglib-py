import argparse


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config-file', type=argparse.FileType(mode='r'),
        required=False, default=None,
        help='Path to a json-encoded config file',
    )
    parser.add_argument(
        '--message', type=str,
        required=False, default='Hello!',
        help='The message that will be printed',
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    print(f'Config: {args.config_file}')

    message = args.message
    print(message)


if __name__ == '__main__':
    main()
