import unittest
from wtforms import Form, StringField
from wtforms.validators import ValidationError

# Adjust import path if necessary based on how you run tests
# Assuming plots is a package accessible in the python path
from plots.form_valid import data_split, DataFloat, DataLength, DataLengthEqual


# Mock field object for validator tests
class MockField:
    def __init__(self, data):
        self.data = data
        self.label = "Test Field"


# Mock form object for DataLengthEqual
class MockForm(Form):
    field1 = StringField('Field 1')
    field2 = StringField('Field 2')


class TestFormValid(unittest.TestCase):

    def test_data_split(self):
        self.assertEqual(data_split(""), [])
        self.assertEqual(data_split("   "), [])
        self.assertEqual(data_split(",,"), [])
        self.assertEqual(data_split(" , , "), [])
        self.assertEqual(data_split("1,2,3"), ['1', '2', '3'])
        self.assertEqual(data_split("1 2 3"), ['1', '2', '3'])
        self.assertEqual(data_split("1, 2  3,,4"), ['1', '2', '3', '4'])
        self.assertEqual(data_split(",1,2,3,"), ['1', '2', '3'])
        self.assertEqual(data_split("  1, 2 ,3  ,"), ['1', '2', '3'])
        self.assertEqual(data_split("1,hello,3.0"), ['1', 'hello', '3.0'])
        self.assertEqual(data_split("1"), ['1'])

    def test_data_float_validator(self):
        validator = DataFloat()
        mock_form = Form() # Dummy form

        # Valid data
        try:
            validator(mock_form, MockField("1.0,2.1,3.0"))
            validator(mock_form, MockField("1, 2, 3"))
            validator(mock_form, MockField("-1.5, 0, 1e5"))
        except ValidationError:
            self.fail("DataFloat raised ValidationError unexpectedly for valid data.")

        # Invalid data
        with self.assertRaisesRegex(ValidationError, 'All data points must be numbers'):
            validator(mock_form, MockField("1.0,abc,3.0"))
        with self.assertRaisesRegex(ValidationError, 'All data points must be numbers'):
            validator(mock_form, MockField("1, two, 3.0"))

        # Empty data (should pass)
        try:
            validator(mock_form, MockField(""))
            validator(mock_form, MockField("   "))
        except ValidationError:
            self.fail("DataFloat raised ValidationError unexpectedly for empty data.")

    def test_data_length_validator(self):
        mock_form = Form() # Dummy form

        # Test within range
        validator_in_range = DataLength(min=2, max=4)
        try:
            validator_in_range(mock_form, MockField("1,2,3"))
            validator_in_range(mock_form, MockField("1,2"))
            validator_in_range(mock_form, MockField("1,2,3,4"))
        except ValidationError:
            self.fail("DataLength raised ValidationError unexpectedly for data in range.")

        # Test below min
        validator_below_min = DataLength(min=2, max=4, message="Too short")
        with self.assertRaisesRegex(ValidationError, "Too short"):
            validator_below_min(mock_form, MockField("1"))

        # Test above max
        validator_above_max = DataLength(min=2, max=4, message="Too long")
        with self.assertRaisesRegex(ValidationError, "Too long"):
            validator_above_max(mock_form, MockField("1,2,3,4,5"))
        
        # Test with max=-1 (no upper limit)
        validator_no_upper = DataLength(min=1, max=-1)
        try:
            validator_no_upper(mock_form, MockField("1,2,3,4,5"))
            validator_no_upper(mock_form, MockField("1"))
        except ValidationError:
            self.fail("DataLength with max=-1 raised ValidationError unexpectedly.")
        
        # Test exact min
        validator_exact_min = DataLength(min=3, max=5)
        try:
            validator_exact_min(mock_form, MockField("1,2,3"))
        except ValidationError:
            self.fail("DataLength failed for exact minimum length.")

        # Test exact max
        validator_exact_max = DataLength(min=1, max=3)
        try:
            validator_exact_max(mock_form, MockField("1,2,3"))
        except ValidationError:
            self.fail("DataLength failed for exact maximum length.")


    def test_data_length_equal_validator(self):
        form_data = {'field1': '1,2', 'field2': 'a,b'}
        form = MockForm(data=form_data) # Pass data to populate fields

        validator = DataLengthEqual('field1', message="Must be equal length.")

        # Test equal length
        try:
            # Validate field2 against field1
            validator(form, form.field2)
        except ValidationError:
            self.fail("DataLengthEqual raised ValidationError for equal length fields.")

        # Test unequal length
        form.field1.data = "1,2,3" # field1 has 3, field2 has 2
        with self.assertRaisesRegex(ValidationError, "Must be equal length."):
            validator(form, form.field2)
        
        # Test with one field empty, other not (field1 has 3, field2 is now empty)
        form.field2.data = ""
        with self.assertRaisesRegex(ValidationError, "Must be equal length."):
            validator(form, form.field2)

        # Test with target field empty, current field not
        form.field1.data = ""
        form.field2.data = "a,b"
        validator_other_way = DataLengthEqual('field2', message="Must be equal length.")
        with self.assertRaisesRegex(ValidationError, "Must be equal length."):
             validator_other_way(form, form.field1)

        # Test both fields empty
        form.field1.data = ""
        form.field2.data = ""
        try:
            validator(form, form.field2) # field2 vs field1
        except ValidationError:
            self.fail("DataLengthEqual raised ValidationError for two empty fields.")


if __name__ == '__main__':
    unittest.main()
