import os
import unittest
from tests.resources.test_dirs import UNIT_TEST_DIRS

# import your test modules
from . import *

dirs = UNIT_TEST_DIRS

mods = []
for dir in dirs:
    # DONT include $$$ modules!
    mods += [
        dir + x[:-3]
        for x in os.listdir(f"tests/{dir}")
        if x.startswith("test_") and not "paid" in x
    ]


# initialize the test suite
loader = unittest.TestLoader()
suite = unittest.TestSuite()

# add tests to the test suite
for mod in mods:
    suite.addTests(loader.loadTestsFromName(f"tests.{mod.replace('/', '.')}"))

# initialize a runner, pass it your suite and run it
runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)
