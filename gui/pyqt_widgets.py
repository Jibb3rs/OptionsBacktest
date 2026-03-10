"""
Shared custom widgets for OptionsBacktest UI.
ToggleSwitch, FilterSection, CollapsibleSection.
"""

from PyQt5.QtWidgets import (
    QPushButton, QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLabel
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QBrush, QColor

from .pyqt_theme import C


class ToggleSwitch(QPushButton):
    """Pill-style toggle switch with animated knob. Pure PyQt5, no external libs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(44, 24)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("border: none; background: transparent;")
        self.toggled.connect(lambda: self.update())

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        r = h // 2

        # Track
        track_color = QColor(C['accent'] if self.isChecked() else C['card_border'])
        p.setBrush(QBrush(track_color))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(0, 0, w, h, r, r)

        # Knob
        knob_x = w - h + 2 if self.isChecked() else 2
        p.setBrush(QBrush(QColor(C['text'])))
        p.drawEllipse(knob_x, 2, h - 4, h - 4)
        p.end()


class FilterSection(QFrame):
    """
    A filter panel with a ToggleSwitch in the header and a collapsible body.
    Used in Advanced tab and Indicators tab.

    Usage:
        section = FilterSection("VIX Filter", initially_enabled=False)
        section.body_layout().addWidget(some_widget)
        is_on = section.is_enabled()
    """

    toggled = pyqtSignal(bool)

    def __init__(self, title, initially_enabled=False, parent=None):
        super().__init__(parent)
        self.setObjectName("panel")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Header row
        header_widget = QWidget()
        header_widget.setObjectName("filterHeader")
        header_row = QHBoxLayout(header_widget)
        header_row.setContentsMargins(14, 10, 14, 10)
        header_row.setSpacing(10)

        self.toggle = ToggleSwitch()
        self.toggle.setChecked(initially_enabled)
        header_row.addWidget(self.toggle)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            f"font-size: 13px; font-weight: bold; color: {C['text']};"
        )
        header_row.addWidget(title_lbl, 1)

        outer.addWidget(header_widget)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background-color: {C['card_border']}; max-height: 1px; border: none;")
        self._separator = sep
        outer.addWidget(sep)

        # Body
        self._body = QWidget()
        self._body_layout = QVBoxLayout(self._body)
        self._body_layout.setContentsMargins(14, 10, 14, 12)
        self._body_layout.setSpacing(8)
        outer.addWidget(self._body)

        # Wire visibility
        self._body.setVisible(initially_enabled)
        self._separator.setVisible(initially_enabled)
        self.toggle.toggled.connect(self._body.setVisible)
        self.toggle.toggled.connect(self._separator.setVisible)
        self.toggle.toggled.connect(self.toggled)

    def body_layout(self):
        """Returns the QVBoxLayout inside the collapsible body."""
        return self._body_layout

    def is_enabled(self):
        """Returns True if the toggle switch is ON."""
        return self.toggle.isChecked()


class CollapsibleSection(QWidget):
    """
    A section with a clickable header that shows/hides its content.
    Used in Analysis tab to wrap the stats table.

    Usage:
        section = CollapsibleSection("Performance Statistics")
        section.body_layout().addWidget(table)
    """

    def __init__(self, title, initially_expanded=True, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header button
        self._header_btn = QPushButton()
        self._header_btn.setObjectName("collapsibleHeader")
        self._header_btn.setCheckable(True)
        self._header_btn.setChecked(initially_expanded)
        self._header_btn.setFlat(True)
        self._title = title
        self._update_header_text()
        self._header_btn.toggled.connect(self._toggle)
        layout.addWidget(self._header_btn)

        # Content frame
        self._content = QFrame()
        self._content.setObjectName("panel")
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(14, 10, 14, 12)
        self._content_layout.setSpacing(8)
        self._content.setVisible(initially_expanded)
        layout.addWidget(self._content)

    def body_layout(self):
        """Returns the QVBoxLayout inside the collapsible content area."""
        return self._content_layout

    def _toggle(self, expanded):
        self._content.setVisible(expanded)
        self._update_header_text()

    def _update_header_text(self):
        expanded = self._header_btn.isChecked()
        chevron = "▾" if expanded else "▸"
        self._header_btn.setText(f"  {chevron}  {self._title}")
