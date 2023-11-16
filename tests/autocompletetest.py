import pytest
from src.services.autocomplete import list_suggestions, exmple_list_autocoplete


def test_list_suggestions():
    lis = ["apple", "banana", "cherry", "date", "fig", "grape"]

    # Test with a query that matches multiple items in the list
    suggestions = list_suggestions("a", lis)
    assert suggestions == ["apple", "banana", "date", "grape"]

    # Test with a query that matches a single item in the list
    suggestions = list_suggestions("banana", lis)
    assert suggestions == ["banana"]

    # Test with a query that doesn't match any item in the list
    suggestions = list_suggestions("kiwi", lis)
    assert suggestions == []


def test_exmple_list_autocoplete():
    # Test with a query that matches multiple fruits
    suggestions = exmple_list_autocoplete("a")
    assert suggestions == ["apple", "banana", "date", "grape"]

    # Test with a query that matches a single fruit
    suggestions = exmple_list_autocoplete("banana")
    assert suggestions == ["banana"]

    # Test with a query that doesn't match any fruit
    suggestions = exmple_list_autocoplete("kiwi")
    assert suggestions == []


def test_autocomplete_fruits(sync_client):
    query_param = "app"
    response = sync_client.get(
        "/api/v1/autocomplete/fruits", params={"query_param": query_param}
    )
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert isinstance(data["suggestions"], list)


def test_autocomplete_text(sync_client):
    query_param = "I want to say th"
    response = sync_client.get("/api/v1/autocomplete", params={"query_param": query_param})
    assert response.status_code == 200
    data = response.json()
    assert "suggestion" in data
    assert isinstance(data["suggestion"], str)
