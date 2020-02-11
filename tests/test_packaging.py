def test_import_package():
    import teimpy  # noqa


def test_package_version():
    import teimpy
    import pkg_resources

    expeect = "develop"
    try:
        expeect = pkg_resources.get_distribution("teimpy").version
    except Exception:
        pass
    assert teimpy.__version__ == expeect
