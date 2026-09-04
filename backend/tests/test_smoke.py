from devsupport_agent import __version__


def test_package_is_importable() -> None:
    """The installed package can be imported from the test environment."""
    assert __version__ == "0.1.0"
