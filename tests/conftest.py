import pytest


@pytest.hookimpl(optionalhook=True)
def pytest_json_runtest_metadata(item, call):
    test_ids = []

    for marker in item.iter_markers():
        if marker.name.startswith("test_"):
            test_id = marker.name.replace(
                "test_", "TEST-", 1
            ).replace("_", "-").upper()
            test_ids.append(test_id)

    return {"test_ids": test_ids}
