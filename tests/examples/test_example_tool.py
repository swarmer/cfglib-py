import subprocess


def test_example_tool_basic():
    subprocess.run(['python', '-m', 'examples.example_tool'], check=True)


def test_example_tool_message():
    subprocess.run(['python', '-m', 'examples.example_tool', '--message', 'HI'], check=True)


def test_example_tool_config_file():
    subprocess.run(
        [
            'python', '-m', 'examples.example_tool',
            '--config-file', 'examples/example_tool_cfg.json'
        ],
        check=True,
    )
