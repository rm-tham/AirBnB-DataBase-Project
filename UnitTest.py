import unittest
import assignment_eleven as ae


class TestAE(unittest.TestCase):

    def test_invalid_inputs(self):
        air_bnb = ae.DataSet()
        with self.assertRaises(air_bnb.EmptyDatasetError):
            air_bnb._cross_table_statistics("Staten Island", "Luxury Suite")
        air_bnb.load_file()
        with self.assertRaises(air_bnb.NoMatchingItems):
            air_bnb._cross_table_statistics("Staten Island", "Luxury Suite")
        with self.assertRaises(KeyError):
            ae.currency_converter(100, "Galactic Credit Standard", "USD")

    def test_return_values(self):
        self.assertEqual(1.96, ae.currency_converter(1.26, "EUR", "CAD"))
        self.assertEqual(6.00, ae.currency_converter(8.40, "CAD", "USD"))
        self.assertEqual(4.00, ae.currency_converter(5, "USD", "GBP"))

    def test_num_lines(self):
        air_bnb = ae.DataSet()
        self.assertEqual(48895, air_bnb.load_file())


if __name__ == "__main__":
    unittest.main()
