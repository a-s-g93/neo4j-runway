# tests/runner.py
import os
import unittest
import sys

# import your test modules
from . import *
# import test_node, test_relationship

mods = [x[:-3] for x in os.listdir("neo4j_runway/tests/") if x.startswith("test_")]
# initialize the test suite
loader = unittest.TestLoader()
suite  = unittest.TestSuite()

# add tests to the test suite
for mod in mods:
    suite.addTests(loader.loadTestsFromName(f"neo4j_runway.tests.{mod}"))
# suite.addTests(loader.loadTestsFromModule(test_node))
# suite.addTests(loader.loadTestsFromModule(thing))

# initialize a runner, pass it your suite and run it
runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)