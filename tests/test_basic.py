import ferum

def test_import():
    try:
        import ferum
        assert True
    except ImportError:
        assert False, "Package 'ferum' not importable"
