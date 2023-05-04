# Performs unittests on the functions in the module
import unittest
import sys
import os

# Add the parent directory to the path so that we can import the module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sync

class TestSync(unittest.TestCase):
    # Test that the get_lua_script function returns the correct lua script
    def test_get_lua_script(self):
        # Get the lua script from the xml file
        lua_script = sync.get_lua_script_from_xml("<muclient><script>print(\"Hello World\")</script></muclient>")
        
        # Check that the lua script is correct
        self.assertEqual(lua_script, "print(\"Hello World\")")
        
        # Check that the lua script is correct
        self.assertIsNone(sync.get_lua_script_from_xml("<script></script>"))