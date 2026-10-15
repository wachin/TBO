"""Shared test configuration for the TBO suite.

Several tests close ``MainWindow`` instances whose undo stack is still
dirty.  Modern pytest-qt closes registered widgets during teardown,
which makes ``MainWindow.closeEvent`` show the unsaved-changes dialog
and blocks the suite forever in offscreen runs.  Tests that care about
that dialog patch ``QMessageBox.warning`` themselves (and therefore
override this default); everywhere else the prompt is auto-answered
with "Discard" so teardown never blocks.
"""

from __future__ import annotations

import pytest
from PyQt6.QtWidgets import QMessageBox


@pytest.fixture(autouse=True)
def _auto_answer_unsaved_changes(monkeypatch):
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        lambda *args, **kwargs: QMessageBox.StandardButton.Discard,
    )
