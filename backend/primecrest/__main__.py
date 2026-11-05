"""``python -m primecrest`` entry point.

Delegates to the same ``main`` the ``primecrest`` console script uses,
so this module form is a drop-in, PATH-independent way to launch the app.
"""

from __future__ import annotations

from primecrest import main

if __name__ == "__main__":
    main()
