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
    import msgspec
    import json

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
