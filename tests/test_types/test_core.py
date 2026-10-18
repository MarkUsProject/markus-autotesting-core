import json

import msgspec
import pytest

from markus_autotesting_core.types import BaseTestData


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
