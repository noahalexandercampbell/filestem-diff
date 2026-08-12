from __future__ import annotations

import sys

from filestemdiff import FileDiffer


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    if argv and argv[0] in {"-h", "--help"}:
        print(
            "filestemdiff - structured diff + word-level patch engine\n"
            "\n"
            "Usage:\n"
            "  python -m filestemdiff  # show this help\n"
            "\n"
            "Import example:\n"
            "  from filestemdiff import FileDiffer\n"
            "  d = FileDiffer()\n"
            "  d.add_patch('--- a/file\\n+++ b/file\\n@@ -1 +1 @@\\n-old\\n+new')\n"
            "  print(d.summary())\n"
        )
        return 0
    print("filestemdiff: use a script or import FileDiffer for real work.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
