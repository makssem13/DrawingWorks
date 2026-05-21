# DrawingWorks launcher
# This script just launches the main program (dw.py)

import os
import runpy

def run():
    runpy.run_path(os.path.join(os.path.dirname(__file__), "dw.py"))

if __name__ == "__main__":
    run()
