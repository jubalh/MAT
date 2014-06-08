''' Base exceptions for MAT
'''


class UnableToRemoveFile(Exception):
    '''This exception is raised when a file could not be removed
    '''
    pass

class UnableToWriteFile(Exception):
    '''This exception is raised when a file
        can could not be chmod +w
    '''
    pass
