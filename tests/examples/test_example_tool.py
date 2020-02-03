import subprocess


def test_example_tool_basic():
    subprocess.run(['python', '-m', 'examples.example_tool'], check=True)


def test_example_tool_message():
    result = subprocess.run(
        ['python', '-m', 'examples.example_tool', '--message', 'HI'],
        capture_output=True,
        check=True,
    )
    assert b'HI' in result.stdout


def test_example_tool_config_file():
    subprocess.run(
        [
            'python', '-m', 'examples.example_tool',
            '--config-file', 'examples/example_tool_cfg.json'
        ],
        check=True,
    )
