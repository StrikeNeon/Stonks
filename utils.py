from os import mkdir


def setup_dirs():
    try:
        mkdir("data")
    except FileExistsError:
        pass
