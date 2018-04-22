import os


def run(**args):
    print("[*] In enviroment module.")
    return str(os.environ)