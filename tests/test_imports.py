def test_import_sideboarder_modular():
    import sideboarder_modular  # your core logic module
    # optionally, assert it has a function you expect:
    assert hasattr(sideboarder_modular, "parse_decklist")

def test_import_sideboarder_script():
    import sideboarder  # your CLI/UI script
    # you could test that running it with `--help` doesn’t error, etc.
