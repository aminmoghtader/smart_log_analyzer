import pytest
from analyzer.parser import LogParser, MalformedLogEntryError

parser = LogParser()

def test_parse_plain_log():
    line = "2025-10-10 12:00:00 ERROR: Something bad happened"
    result = parser.parse(line)
    assert isinstance(result, dict)
    assert result["level"] == "ERROR"
    assert "Something bad" in result["message"]
    assert result["timestamp"].startswith("2025-10-10")

def test_parse_json_log():
    line = '{"timestamp":"2025-10-10T12:00:00","level":"INFO","message":"ok"}'
    result = parser.parse(line)
    assert isinstance(result, dict)
    assert result["level"] == "INFO"
    assert result["timestamp"].startswith("2025-10-10")
    assert result["message"] == "ok"

def test_parse_invalid_log():
    line = "random nonsense without timestamp or level"
    with pytest.raises(MalformedLogEntryError):
        parser.parse(line)



