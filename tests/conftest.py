import os
import sys

# Ensure the project root is on the import path so tests can import algorithm modules
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root not in sys.path:
    sys.path.insert(0, root)
