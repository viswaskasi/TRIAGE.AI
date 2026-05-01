import os
print(f"File: {__file__}")
print(f"Dirname: {os.path.dirname(__file__)}")
print(f"Dirname 2: {os.path.dirname(os.path.dirname(__file__))}")
print(f"Frontend: {os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')}")
