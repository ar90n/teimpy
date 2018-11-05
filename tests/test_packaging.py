def test_import_package():
    import teimpy  # noqa


def test_package_version():
    import teimpy
    import pkg_resources

    assert teimpy.__version__ == pkg_resources.get_distribution('teimpy').version
