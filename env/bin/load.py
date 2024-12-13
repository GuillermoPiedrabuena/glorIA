from loaders import BarLoader
import sys
import subprocess

def load():
    command = sys.argv[1:]
    loader = BarLoader(speed=.1, animation='bounce', colour='yellow')
    loader.start()
    subprocess.call(command)
    loader.stop()

if __name__ == "__main__":
    load()
