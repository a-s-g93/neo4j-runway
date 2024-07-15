import os
import unittest

# import your test modules
from . import *

dirs = [
    "test_code_generator/",
    "test_discovery/",
    "test_ingest/",
    "test_integration/",
    "test_modeler/",
    "test_models/",
    "test_inputs/",
    "test_utils/",
]

mods = []
for dir in dirs:
    mods += [
        f"{dir[:-1]}." + x[:-3]
        for x in os.listdir(f"tests/{dir}")
        if x.startswith("test_")
    ]

# initialize the test suite
loader = unittest.TestLoader()
suite = unittest.TestSuite()

# add tests to the test suite
for mod in mods:
    suite.addTests(loader.loadTestsFromName(f"tests.{mod}"))

# initialize a runner, pass it your suite and run it
runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)
