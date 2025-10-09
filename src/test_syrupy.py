


# tests/test_greeting.py
def test_greeting(snapshot):
    payload = {"message": "hello", "lang": "en"}
    assert payload == snapshot