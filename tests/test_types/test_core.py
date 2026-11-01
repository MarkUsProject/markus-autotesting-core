import json

import msgspec
import pytest

from markus_autotesting_core.types import (
    BaseTestData,
    BaseTesterSettings,
    create_autotest_settings_class,
)


def test_base_test_data_fields():
    """Test that the BaseTestData class has the expected fields."""
    annotations = BaseTestData.__annotations__

    assert "category" in annotations
    assert "script_files" in annotations
    assert "timeout" in annotations
    assert "feedback_file_names" in annotations
    assert "extra_info" in annotations


def test_base_test_data_decoding():
    """Test that an instance of BaseTestData can be dencoded from JSON."""
    json_data = json.dumps(
        {
            "category": ["unit", "integration"],
            "script_files": ["test1.py", "test2.py"],
            "timeout": 60,
            "feedback_file_names": ["feedback.txt"],
            "extra_info": {"note": "This is a test."},
        }
    )

    decoded = msgspec.json.decode(json_data, type=BaseTestData)

    assert decoded.category == ["unit", "integration"]
    assert decoded.script_files == ["test1.py", "test2.py"]
    assert decoded.timeout == 60
    assert decoded.feedback_file_names == ["feedback.txt"]
    assert decoded.extra_info == {"note": "This is a test."}


def test_base_test_data_decoding_error():
    """Test that invalid JSON is not decoded into a BaseTestData instance."""
    json_data = json.dumps(
        {
            "category": ["unit", "integration"],
            "script_files": [],
            "timeout": 60,
            "feedback_file_names": ["feedback.txt"],
            "extra_info": {"note": "This is a test."},
        }
    )

    with pytest.raises(msgspec.ValidationError):
        msgspec.json.decode(json_data, type=BaseTestData)


def base_test_data(**fields) -> dict:
    return {"category": ["instructor"], "script_files": ["test1.py"], **fields}


@pytest.mark.parametrize(
    "fields",
    [
        pytest.param({"category": ["instructor", "instructor"]}, id="category"),
        pytest.param(
            {"script_files": ["test1.py", "test2.py", "test1.py"]}, id="script_files"
        ),
    ],
)
def test_base_test_data_duplicate_items_rejected(fields):
    """Test that fields marked uniqueItems reject duplicate items."""
    with pytest.raises(msgspec.ValidationError, match="contains duplicate items"):
        msgspec.convert(base_test_data(**fields), type=BaseTestData)


def test_base_test_data_duplicate_items_error_path():
    """Test that the duplicate items error reports where in the document it occurred."""
    with pytest.raises(msgspec.ValidationError, match=r"\$\[1\]"):
        msgspec.convert(
            [base_test_data(), base_test_data(category=["a", "a"])],
            type=list[BaseTestData],
        )


def test_base_test_data_duplicates_allowed_without_unique_items():
    """Test that a subclass overriding a field without uniqueItems allows duplicates."""

    class NonUniqueTestData(BaseTestData, kw_only=True):
        script_files: list[str]

    decoded = msgspec.convert(
        base_test_data(script_files=["a.py", "a.py"]), type=NonUniqueTestData
    )

    assert decoded.script_files == ["a.py", "a.py"]


class FakeTesterSettings(BaseTesterSettings):
    """A minimal concrete subclass used to test BaseTesterSettings fields."""


def test_base_tester_settings_env_defaults_to_empty_dict():
    """Test that _env defaults to a new empty dict for each instance, and is encoded as {}."""
    first = msgspec.convert({"tester_type": "fake"}, type=FakeTesterSettings)
    second = FakeTesterSettings()

    assert first._env == {}
    assert first._env is not second._env
    assert msgspec.to_builtins(first)["_env"] == {}


def test_base_tester_settings_env_decoding():
    """Test that _env is decoded, and that null is rejected."""
    decoded = msgspec.convert(
        {"tester_type": "fake", "_env": {"PYTHON": "/bin/python3"}},
        type=FakeTesterSettings,
    )

    assert decoded._env == {"PYTHON": "/bin/python3"}
    with pytest.raises(msgspec.ValidationError):
        msgspec.convert({"tester_type": "fake", "_env": None}, type=FakeTesterSettings)


class ExplicitTagTesterSettings(BaseTesterSettings, tag="explicit"):
    """A subclass whose tag is set explicitly rather than derived from its name."""


@pytest.mark.parametrize(
    "cls, expected",
    [
        pytest.param(FakeTesterSettings, "fake", id="derived tag"),
        pytest.param(ExplicitTagTesterSettings, "explicit", id="explicit tag"),
    ],
)
def test_base_tester_settings_tester_type_matches_tag(cls, expected):
    """Test that tester_type is the tag msgspec encodes and decodes as `tester_type`."""
    settings = msgspec.convert({"tester_type": expected}, type=cls)

    assert settings.tester_type == expected
    assert msgspec.to_builtins(settings)["tester_type"] == expected


class AlphaTesterSettings(BaseTesterSettings):
    """A tester class used to test create_autotest_settings_class."""

    test_data: list[BaseTestData]


class BetaTesterSettings(BaseTesterSettings):
    """A second tester class used to test create_autotest_settings_class."""

    test_data: list[BaseTestData]


def test_create_autotest_settings_class_decodes_union():
    """Test that each tester is decoded as the class matching its tester_type."""
    settings_class = create_autotest_settings_class(
        [AlphaTesterSettings, BetaTesterSettings]
    )

    decoded = msgspec.convert(
        {
            "testers": [
                {"tester_type": "beta", "test_data": [base_test_data()]},
                {"tester_type": "alpha", "test_data": [base_test_data(timeout=10)]},
            ],
            "_user": "instructor",
        },
        type=settings_class,
    )

    assert [type(tester) for tester in decoded.testers] == [
        BetaTesterSettings,
        AlphaTesterSettings,
    ]
    assert decoded.testers[1].test_data[0].timeout == 10
    assert decoded._user == "instructor"


def test_create_autotest_settings_class_single_tester_class():
    """Test that a single tester class can be used."""
    settings_class = create_autotest_settings_class([AlphaTesterSettings])

    decoded = msgspec.convert(
        {"testers": [{"tester_type": "alpha", "test_data": [base_test_data()]}]},
        type=settings_class,
    )

    assert isinstance(decoded.testers[0], AlphaTesterSettings)


def test_create_autotest_settings_class_empty_testers_rejected():
    """Test that settings with an empty testers list are rejected."""
    settings_class = create_autotest_settings_class([AlphaTesterSettings])

    with pytest.raises(msgspec.ValidationError):
        msgspec.convert({"testers": []}, type=settings_class)


def test_create_autotest_settings_class_unknown_tester_type_rejected():
    """Test that a tester with a tester_type not in the union is rejected."""
    settings_class = create_autotest_settings_class(
        [AlphaTesterSettings, BetaTesterSettings]
    )

    with pytest.raises(msgspec.ValidationError):
        msgspec.convert(
            {"testers": [{"tester_type": "gamma", "test_data": [base_test_data()]}]},
            type=settings_class,
        )


def test_create_autotest_settings_class_no_tester_classes():
    """Test that creating a settings class with no tester classes raises ValueError."""
    with pytest.raises(ValueError, match="At least one tester class is required"):
        create_autotest_settings_class([])
