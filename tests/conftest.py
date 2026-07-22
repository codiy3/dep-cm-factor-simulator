from __future__ import annotations

import gc
import os
from collections.abc import Iterator
from typing import TYPE_CHECKING, cast

import pytest


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qt_app() -> Iterator[QApplication]:
    """テストセッション全体で1つのQApplicationを保持する。"""

    from PySide6.QtWidgets import QApplication

    app_instance = QApplication.instance()

    if app_instance is None:
        app = QApplication([])
    else:
        app = cast("QApplication", app_instance)

    app.setQuitOnLastWindowClosed(False)

    yield app

    app.processEvents()


@pytest.fixture
def qt_event_loop(qt_app: QApplication) -> Iterator[None]:
    """各GUIテスト後にQtオブジェクトの終了処理を進める。"""

    from PySide6.QtCore import QCoreApplication, QEvent

    yield

    gc.collect()
    QCoreApplication.sendPostedEvents(
        None,
        QEvent.Type.DeferredDelete,
    )
    qt_app.processEvents()
