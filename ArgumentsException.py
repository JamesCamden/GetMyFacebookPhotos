class ArgumentsException(Exception):
    def __init__(self):
	    self.value = "Invalid arguments: 2 arguments expected: username + password"

    def __str__(self):
	    return repr(self.value)
