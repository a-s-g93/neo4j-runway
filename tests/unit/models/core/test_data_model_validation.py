from neo4j_runway.models import DataModel, Node, Property, Relationship

data_dictionary = {
    "a.csv": {"id": "unique id for a. Has alias a_id", "b": "feature b"},
    "b.csv": {"id": "unique id for b", "a_id": "unique id for a.", "c": "feature c"},
}

valid_columns = {k: list(v.keys()) for k, v in data_dictionary.items()}

nodes = [
    Node(
        label="LabelA",
        properties=[
            Property(
                name="id",
                type="str",
                column_mapping="id",
                alias="a_id",
                is_unique=True,
            ),
            Property(name="b", type="str", column_mapping="b"),
        ],
        source_name="a.csv",
    ),
    Node(
        label="LabelB",
        properties=[
            Property(name="id", type="str", column_mapping="id", is_unique=True),
            Property(name="c", type="str", column_mapping="c"),
        ],
        source_name="b.csv",
    ),
]

data_model = DataModel(
    nodes=nodes,
    relationships=[
        Relationship(
            type="HAS_REL", source="LabelA", target="LabelB", source_name="b.csv"
        )
    ],
)
data_model_flipped = DataModel(
    nodes=nodes,
    relationships=[
        Relationship(
            type="HAS_REL", source="LabelB", target="LabelA", source_name="b.csv"
        )
    ],
)


def test_multi_file_different_source_relationship_valid_source_node() -> None:
    validation = data_model.validate_model(
        valid_columns=valid_columns, data_dictionary=data_dictionary
    )
    for e in validation["errors"]:
        print(e)
    assert len(validation["errors"]) == 0


def test_multi_file_different_source_relationship_valid_target_node() -> None:
    validation = data_model_flipped.validate_model(
        valid_columns=valid_columns, data_dictionary=data_dictionary
    )
    for e in validation["errors"]:
        print(e)
    assert len(validation["errors"]) == 0


def test_multi_file_different_source_relationship_invalid() -> None:
    data_dictionary_bad = {
        "a.csv": {"id": "unique id for a. Has alias a_id", "b": "feature b"},
        "b.csv": {"id": "unique id for b", "c": "feature c"},
    }

    valid_columns_bad = {k: list(v.keys()) for k, v in data_dictionary_bad.items()}
    validation = data_model.validate_model(
        valid_columns=valid_columns_bad, data_dictionary=data_dictionary_bad
    )

    assert len(validation["errors"]) == 1


# valid_columns = {
#     "countries.csv": ["id", "name", "capital", "currency", "region", "subregion"],
#     "states.csv": ["id", "name", "country_id"],
#     "cities.csv": ["id", "name", "state_id", "country_id"],
# }
# data_dictionary = {
#     "countries.csv": {
#         "id": "The unique country id. Has alias: country_id",
#         "name": "The country name.",
#         "capital": "The capital of the country.",
#         "currency": "The currency used by the country.",
#         "region": "The region that contains the country.",
#         "subregion": "The subregion that contains the country.",
#     },
#     "states.csv": {
#         "id": "The unique state id. Has alias: state_id",
#         "name": "The state name.",
#         "country_id": "The unique id of the country the state belongs to.",
#     },
#     "cities.csv": {
#         "id": "The unique city id.",
#         "name": "The name of the city.",
#         "state_id": "The unique id of the state that contains the city.",
#         "country_id": "The unique id of the country that contains the city.",
#     },
# }

# data_model = DataModel(
#     nodes=[
#         Node(
#             label="Country",
#             properties=[
#                 Property(
#                     name="id",
#                     type="int",
#                     column_mapping="id",
#                     alias="country_id",
#                     is_unique=True,
#                     part_of_key=False,
#                 ),
#                 Property(
#                     name="name",
#                     type="str",
#                     column_mapping="name",
#                     alias=None,
#                     is_unique=False,
#                     part_of_key=False,
#                 ),
#                 Property(
#                     name="capital",
#                     type="str",
#                     column_mapping="capital",
#                     alias=None,
#                     is_unique=False,
#                     part_of_key=False,
#                 ),
#                 Property(
#                     name="currency",
#                     type="str",
#                     column_mapping="currency",
#                     alias=None,
#                     is_unique=False,
#                     part_of_key=False,
#                 ),
#                 Property(
#                     name="region",
#                     type="str",
#                     column_mapping="region",
#                     alias=None,
#                     is_unique=False,
#                     part_of_key=False,
#                 ),
#                 Property(
#                     name="subregion",
#                     type="str",
#                     column_mapping="subregion",
#                     alias=None,
#                     is_unique=False,
#                     part_of_key=False,
#                 ),
#             ],
#             source_name="countries.csv",
#         ),
#         Node(
#             label="City",
#             properties=[
#                 Property(
#                     name="id",
#                     type="int",
#                     column_mapping="id",
#                     alias=None,
#                     is_unique=True,
#                     part_of_key=False,
#                 ),
#                 Property(
#                     name="name",
#                     type="str",
#                     column_mapping="name",
#                     alias=None,
#                     is_unique=False,
#                     part_of_key=False,
#                 ),
#                 Property(
#                     name="stateId",
#                     type="int",
#                     column_mapping="state_id",
#                     alias="id",
#                     is_unique=False,
#                     part_of_key=True,
#                 ),
#                 Property(
#                     name="countryId",
#                     type="int",
#                     column_mapping="country_id",
#                     alias="id",
#                     is_unique=False,
#                     part_of_key=True,
#                 ),
#             ],
#             source_name="cities.csv",
#         ),
#         Node(
#             label="State",
#             properties=[
#                 Property(
#                     name="id",
#                     type="int",
#                     column_mapping="id",
#                     alias="state_id",
#                     is_unique=True,
#                     part_of_key=False,
#                 ),
#                 Property(
#                     name="name",
#                     type="str",
#                     column_mapping="name",
#                     alias=None,
#                     is_unique=False,
#                     part_of_key=False,
#                 ),
#                 Property(
#                     name="countryId",
#                     type="int",
#                     column_mapping="country_id",
#                     alias="country_id",
#                     is_unique=False,
#                     part_of_key=True,
#                 ),
#             ],
#             source_name="states.csv",
#         ),
#     ],
#     relationships=[
#         Relationship(
#             type="CITY_TO_STATE",
#             properties=[],
#             source="City",
#             target="State",
#             source_name="cities.csv",
#         ),
#         Relationship(
#             type="CITY_TO_COUNTRY",
#             properties=[],
#             source="City",
#             target="Country",
#             source_name="cities.csv",
#         ),
#     ],
#     metadata=None,
# )
