import os
import unittest

# import your test modules
from . import *

mods = [
    x[:-3]
    for x in os.listdir("tests/test_modeler/")
    if x.startswith("test_")
]
# only run the tests that don't charge money $$$
mods.remove("test_data_modeler_with_yaml")
# initialize the test suite
loader = unittest.TestLoader()
suite = unittest.TestSuite()

# add tests to the test suite
for mod in mods:
    suite.addTests(loader.loadTestsFromName(f"tests.test_modeler.{mod}"))

# initialize a runner, pass it your suite and run it
runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)
