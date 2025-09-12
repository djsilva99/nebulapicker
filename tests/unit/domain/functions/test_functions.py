from datetime import datetime
from unittest.mock import patch

from src.domain.functions.print_hello import print_hello


def test_print_hello_outputs_expected_message(capsys):
    # GIVEN
    fake_now = datetime(2023, 1, 1, 12, 0, 0)

    # WHEN
    with patch("src.domain.functions.print_hello.datetime") as mock_datetime:
        mock_datetime.utcnow.return_value = fake_now
        print_hello("Bob")

    # THEN
    captured = capsys.readouterr()
    assert f"[{fake_now}] Hello Bob!" in captured.out
