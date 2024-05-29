import os
import unittest

# import your test modules
from . import *

mods = [
    x[:-3]
    for x in os.listdir("neo4j_runway/tests/test_modeler")
    if x.startswith("test_")
]

# initialize the test suite
loader = unittest.TestLoader()
suite = unittest.TestSuite()

# add tests to the test suite
for mod in mods:
    suite.addTests(loader.loadTestsFromName(f"neo4j_runway.tests.test_modeler.{mod}"))

# initialize a runner, pass it your suite and run it
runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)
