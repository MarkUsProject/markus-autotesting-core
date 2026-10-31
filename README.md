# markus-autotesting-core

`markus-autotesting-core` defines the data types for [MarkUs autotester](https://github.com/MarkUsProject/markus-autotesting) test settings. The types are [msgspec](https://jcristharif.com/msgspec/) structs, so one definition gives you both:

- **validation:** decoding settings JSON into typed objects, rejecting invalid settings
- **a JSON schema:** used by MarkUs to render the test settings form

Each tester (Python, Java, Haskell, …) defines its own settings by subclassing the base types here.

## Installation

```
pip install markus-autotesting-core
```

Requires Python 3.11 or later.

## Usage

### Defining a tester's settings

Subclass `BaseTestData` for the settings of one test group, and `BaseTesterSettings` for the tester as a whole:

```python
from typing import Annotated, Literal

from msgspec import Meta
from markus_autotesting_core.types import BaseTestData, BaseTesterSettings


class PyTestData(BaseTestData, kw_only=True):
    """The settings for one Python test group."""

    tester: Literal["pytest", "unittest"] = "pytest"


class PyTesterSettings(BaseTesterSettings):
    """The settings for the Python tester."""

    test_data: Annotated[list[PyTestData], Meta(title="Test Groups", min_length=1)]
```

`BaseTestData` provides the fields every test group has:

| Field | Type | Default |
|---|---|---|
| `category` | `list[str]`, no duplicates | required |
| `script_files` | `list[str]`, at least one, no duplicates | required |
| `timeout` | `int`, in seconds | `30` |
| `feedback_file_names` | `list[str]` | `[]` |
| `extra_info` | any | `{}` |

`BaseTesterSettings` is a tagged union on the `tester_type` field. A subclass's tag is its class name without the `TesterSettings` suffix, lowercased, so `PyTesterSettings` is `"py"`. To use a different tag, pass `tag=`:

```python
class CustomTesterSettings(BaseTesterSettings, tag="custom"): ...
```

### Decoding settings

`create_autotest_settings_class` builds the type for a complete settings document from the tester classes you have:

```python
import msgspec
from markus_autotesting_core.types import create_autotest_settings_class

AutotestSettings = create_autotest_settings_class([PyTesterSettings])

settings = msgspec.json.decode(
    b'{"testers": [{"tester_type": "py", "test_data": [{"category": ["instructor"], "script_files": ["test.py"]}]}]}',
    type=AutotestSettings,
)
settings.testers[0].tester_type  # "py"
settings.testers[0].test_data[0].timeout  # 30
```

Invalid settings raise `msgspec.ValidationError`, with the location of the problem:

```python
msgspec.json.decode(
    b'{"testers": [{"tester_type": "py", "test_data": [{"category": [], "script_files": ["a.py", "a.py"]}]}]}',
    type=AutotestSettings,
)
# msgspec.ValidationError: `script_files` contains duplicate items: ['a.py'] - at `$.testers[0].test_data[0]`
```

`msgspec.to_builtins(settings)` converts decoded settings back to plain dicts and lists, with defaults filled in.

### Generating the JSON schema

```python
schema, components = msgspec.json.schema_components([PyTesterSettings])
```

Some values depend on the assignment, so the schema refers to definitions that the consumer (MarkUs) fills in before rendering the form:

| Definition | Used for | Filled in with |
|---|---|---|
| `#/definitions/files_list` | each entry of `script_files` | the assignment's test files |
| `#/definitions/test_data_categories` | each entry of `category` | the test categories |
| `#/definitions/extra_group_data` | `extra_info` | MarkUs's test group settings |

msgspec's decoder doesn't check these definitions, or other keywords added with `Meta(extra_json_schema=...)`. The one exception is `uniqueItems`, which `BaseTestData` checks when decoding.

## Development

The project uses [uv](https://docs.astral.sh/uv/).

```
uv sync
uv run pytest
```

Linting and formatting use [ruff](https://docs.astral.sh/ruff/), and run as [pre-commit](https://pre-commit.com/) hooks:

```
uv run ruff check .
uv run ruff format .
```

Contributions are welcome: please open an issue or a pull request.

## License

MIT. See [LICENSE](LICENSE).
