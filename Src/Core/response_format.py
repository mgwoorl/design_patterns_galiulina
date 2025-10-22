from enum import Enum


class ResponseFormat(Enum):
    CSV = "csv"
    MARKDOWN = "markdown"
    JSON = "json"
    XML = "xml"

    @staticmethod
    def csv() -> str:
        return "csv"

    @staticmethod
    def markdown() -> str:
        return "markdown"

    @staticmethod
    def json() -> str:
        return "json"

    @staticmethod
    def xml() -> str:
        return "xml"