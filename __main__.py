import runpy, os, sys

sys.path.insert(0, os.path.dirname(__file__))
runpy.run_path(os.path.join(os.path.dirname(__file__), "main.py"), run_name="__main__")
