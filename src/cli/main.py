"""gpower-clone: argv → {alan: metin} → engine.run → tek satır JSON (CONTRACT §2).

Burada hesap ya da doğrulama kuralı yoktur; yalnızca `--alan değer` çiftleri ayrılır.
"""
import json
import sys

import engine
from engine import EngineError


def parse_args(argv):
    params = {}
    i = 0
    while i < len(argv):
        tok = argv[i]
        if not tok.startswith("--") or len(tok) == 2:
            raise EngineError("INVALID_VALUE", None, f"expected --<field>, got {tok!r}")
        name = tok[2:]
        if i + 1 >= len(argv):
            raise EngineError("INVALID_VALUE", name, f"no value given for --{name}")
        if name in params:
            raise EngineError("INVALID_VALUE", name, f"--{name} given more than once")
        params[name] = argv[i + 1]
        i += 2
    return params


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        if argv == ["--version"]:
            out, code = engine.version(), 0
        else:
            out, code = engine.run(parse_args(argv)), 0
    except EngineError as e:
        out, code = e.to_json(), e.exit_code
    except Exception as e:  # beklenmeyen durum → iç hata
        print(repr(e), file=sys.stderr)
        out, code = {"error": f"internal error: {e}", "code": "INTERNAL", "field": None}, 1
    sys.stdout.write(json.dumps(out, allow_nan=False) + "\n")
    return code


if __name__ == "__main__":
    sys.exit(main())
