"""Motorun tek hata türü. Kodlar CONTRACT §2.4'teki tablodan."""

# Girdi hataları çıkış kodu 2, hesap yapılamayan durumlar 1 (CONTRACT §2.4).
EXIT_CODES = {
    "MISSING_PARAM": 2,
    "UNKNOWN_PARAM": 2,
    "INVALID_VALUE": 2,
    "OUT_OF_RANGE": 2,
    "INCONSISTENT": 2,
    "UNSUPPORTED": 2,
    "NO_SOLUTION": 1,
    "INTERNAL": 1,
}


class EngineError(Exception):
    def __init__(self, code, field, message):
        super().__init__(message)
        self.code = code
        self.field = field
        self.message = message

    @property
    def exit_code(self):
        return EXIT_CODES[self.code]

    def to_json(self):
        return {"error": self.message, "code": self.code, "field": self.field}
