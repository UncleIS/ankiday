"""Test cloze model creation functionality in AnkiConnect backend."""

import json
from unittest.mock import Mock, patch
from ankiday.backends.ankiconnect import AnkiConnectBackend


class MockResponse:
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


def test_create_regular_model():
    """Test creating a regular (non-cloze) model."""
    backend = AnkiConnectBackend()

    with patch('httpx.Client') as mock_client_class:
        # Mock the context manager and response
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        mock_client_class.return_value.__exit__.return_value = None

        mock_response = MockResponse({"result": None, "error": None})
        mock_client.post.return_value = mock_response

        # Test creating a regular model
        backend.create_model(
            name="TestModel",
            fields=["Front", "Back"],
            templates=[{"name": "Card 1", "qfmt": "{{Front}}", "afmt": "{{Back}}"}],
            css=".card { font-family: arial; }",
            is_cloze=False
        )

        # Verify the request was made correctly
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args

        # Check the payload
        payload = call_args[1]['json']
        assert payload['action'] == 'createModel'
        assert payload['version'] == 5

        params = payload['params']
        assert params['modelName'] == 'TestModel'
        assert params['inOrderFields'] == ['Front', 'Back']
        assert params['css'] == '.card { font-family: arial; }'
        assert 'isCloze' not in params  # Should not be present for regular models

        # Check templates format
        expected_templates = [{"Name": "Card 1", "Front": "{{Front}}", "Back": "{{Back}}"}]
        assert params['cardTemplates'] == expected_templates


def test_create_cloze_model():
    """Test creating a cloze model with isCloze=True."""
    backend = AnkiConnectBackend()

    with patch('httpx.Client') as mock_client_class:
        # Mock the context manager and response
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        mock_client_class.return_value.__exit__.return_value = None

        mock_response = MockResponse({"result": None, "error": None})
        mock_client.post.return_value = mock_response

        # Test creating a cloze model
        backend.create_model(
            name="ClozeModel",
            fields=["Text", "Extra"],
            templates=[{"name": "Cloze", "qfmt": "{{cloze:Text}}", "afmt": "{{cloze:Text}}<br>{{Extra}}"}],
            css=".cloze { color: blue; }",
            is_cloze=True
        )

        # Verify the request was made correctly
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args

        # Check the payload
        payload = call_args[1]['json']
        assert payload['action'] == 'createModel'
        assert payload['version'] == 5

        params = payload['params']
        assert params['modelName'] == 'ClozeModel'
        assert params['inOrderFields'] == ['Text', 'Extra']
        assert params['css'] == '.cloze { color: blue; }'
        assert params['isCloze'] == True  # This is the key difference!

        # Check templates format
        expected_templates = [{"Name": "Cloze", "Front": "{{cloze:Text}}", "Back": "{{cloze:Text}}<br>{{Extra}}"}]
        assert params['cardTemplates'] == expected_templates


def test_create_model_with_error():
    """Test error handling when AnkiConnect returns an error."""
    backend = AnkiConnectBackend()

    with patch('httpx.Client') as mock_client_class:
        # Mock the context manager and response
        mock_client = Mock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        mock_client_class.return_value.__exit__.return_value = None

        mock_response = MockResponse({"result": None, "error": "Model already exists"})
        mock_client.post.return_value = mock_response

        # Test that error is properly raised
        try:
            backend.create_model(
                name="ExistingModel",
                fields=["Text"],
                templates=[{"name": "Card", "qfmt": "{{Text}}", "afmt": "{{Text}}"}],
                css="",
                is_cloze=False
            )
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "AnkiConnect error: Model already exists" in str(e)


if __name__ == "__main__":
    test_create_regular_model()
    print("Regular model creation test passed!")

    test_create_cloze_model()
    print("Cloze model creation test passed!")

    test_create_model_with_error()
    print("Error handling test passed!")

    print("All AnkiConnect cloze tests passed!")
