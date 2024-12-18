import unittest

from neo4j_runway.inputs import UserInput, user_input_safe_construct

USER_GENERATED_INPUT = {
    "general_description": "This is data on some interesting data.",
    "id": "unique id for a node.",
    "feature_1": "this is a feature",
    "feature_2": "this is also a feature",
}

data = {
    "id": [1, 2, 3, 4, 5],
    "feature_1": ["a", "b", "c", "d", "e"],
    "feature_2": ["z", "y", "x", "w", "v"],
    "bad_feature": [11, 22, 33, 44, 55],
}


class TestUserInput(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pass

    def test_no_general_description(self) -> None:
        UserInput(data_dictionary={"feature_1": "f1", "feature_2": "f2"})

    def test_bad_col_description(self) -> None:
        with self.assertRaises(ValueError):
            UserInput(
                general_description="gen",
                data_dictionary={"feature_1": 1, "feature_2": "f2"},
            )

    def test_empty_col_description(self) -> None:
        with self.assertWarns(Warning):
            UserInput(general_description="gen", data_dictionary={})

    def test_unsafe_construction_no_general_description(self) -> None:
        unsafe_input = {"col_a": "this is col a.", "col_b": "this is col_b."}
        allowed_columns = ["col_a", "col_b"]

        with self.assertWarns(Warning):
            safe_input = user_input_safe_construct(
                unsafe_user_input=unsafe_input, allowed_columns=allowed_columns
            )

            self.assertEqual(safe_input.general_description, "")
            self.assertEqual(
                set(unsafe_input.keys()),
                set(safe_input.data_dictionary.get_table_schema("file").column_names),
            )
            self.assertIn("col_a", safe_input.allowed_columns.get("file"))
            self.assertIn("col_b", safe_input.allowed_columns.get("file"))

    # def test_unsafe_construction_no_data_dictionary(self) -> None:
    #     unsafe_input = {"general_description": "this is the general description."}
    #     allowed_columns = ["col_a", "col_b"]

    #     with self.assertWarns(Warning):
    #         safe_input = user_input_safe_construct(
    #             unsafe_user_input=unsafe_input, allowed_columns=allowed_columns
    #         )

    #         self.assertEqual(
    #             safe_input.general_description, "this is the general description."
    #         )
    #         self.assertEqual(
    #             set(allowed_columns),
    #             set(safe_input.data_dictionary.get_table_schema("file").column_names),
    #         )
    #         self.assertIn("col_a", safe_input.allowed_columns.get("file"))
    #         self.assertIn("col_b", safe_input.allowed_columns.get("file"))

    # def test_unsafe_construction_no_input(self) -> None:
    #     unsafe_input = {}
    #     allowed_columns = ["col_a", "col_b"]

    #     with self.assertWarns(Warning):
    #         safe_input = user_input_safe_construct(
    #             unsafe_user_input=unsafe_input, allowed_columns=allowed_columns
    #         )

    #         self.assertEqual(safe_input.general_description, "")
    #         self.assertEqual(
    #             set(allowed_columns),
    #             set(safe_input.data_dictionary.get_table_schema("file").column_names),
    #         )
    #         self.assertIn("col_a", safe_input.allowed_columns.get("file"))
    #         self.assertIn("col_b", safe_input.allowed_columns.get("file"))

    def test_unsafe_construction_columns_not_found_in_allowed_list(self) -> None:
        unsafe_input = {
            "general_description": "this is the general description.",
            "col_a": "this is col a.",
            "col_c": "this is col_c.",
        }
        allowed_columns = ["col_a", "col_b"]

        with self.assertRaises(ValueError):
            user_input_safe_construct(
                unsafe_user_input=unsafe_input, allowed_columns=allowed_columns
            )

    def test_is_multifile_true(self) -> None:
        dd = {
            "a.csv": {"a": "desc", "b": "desc2"},
            "b.csv": {"c": "desc3", "d": "desc4"},
        }

        u = UserInput(general_description="general", data_dictionary=dd)

        self.assertTrue(u.is_multifile)

    def test_is_multifile_false(self) -> None:
        dd = {"a": "desc", "b": "desc2"}

        u = UserInput(general_description="general", data_dictionary=dd)

        self.assertFalse(u.is_multifile)

    # def test_data_dictionary_with_column_descriptions(self) -> None:
    #     ui = UserInput(column_descriptions={"feature_1": "f1", "feature_2": "f2"})


if __name__ == "__main__":
    unittest.main()
