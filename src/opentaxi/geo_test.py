import unittest
from unittest.mock import patch, Mock

import s2sphere
from opentaxi import geo


class OpenTaxiGeoTests(unittest.TestCase):

    def test_get_hierarchy_as_tokens(self):
        cellid = s2sphere.CellId.from_token('48761b4c9')
        tokens = geo.get_hierarchy_as_tokens(cellid)
        tokens_str = '/'.join(map(str, tokens))
        self.assertEqual(tokens_str, '48761b/48761b5/48761b4d/48761b4c9')

        cellid = s2sphere.CellId.from_token('48761b5')
        tokens = geo.get_hierarchy_as_tokens(cellid)
        tokens_str = '/'.join(map(str, tokens))
        self.assertEqual(tokens_str, '48761b/48761b5/x/x')

        cellid = s2sphere.CellId.from_token('48761b4')
        tokens = geo.get_hierarchy_as_tokens(cellid, level_mod=2, placeholder=None)
        tokens_str = '/'.join(map(str, tokens))
        self.assertEqual(tokens_str, '48761b')
