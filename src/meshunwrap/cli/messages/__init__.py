"""CLI messages package for meshunwrap.

Provides error_panel, warning_panel, info_panel, and use_layout for consistent
CLI styling. Commands can import from this package for user-facing output.
"""

from meshunwrap.cli.messages.capability import supports_unicode_markdown
from meshunwrap.cli.messages.error import error_panel
from meshunwrap.cli.messages.layout import use_layout
from meshunwrap.cli.messages.message import info_panel
from meshunwrap.cli.messages.warning import warning_panel

__all__ = [
    "error_panel",
    "info_panel",
    "supports_unicode_markdown",
    "use_layout",
    "warning_panel",
]
