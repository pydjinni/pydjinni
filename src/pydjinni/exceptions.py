
class ApplicationException(Exception):
    """PyDjinni application exceptions superclass"""
    code = -1


class FileNotFoundException(ApplicationException):
    """Exception raised when a required input file is not found"""
    code = 2


class ParsingException(ApplicationException):
    """Exception related to a parsing error in some input file"""
    code = 150
