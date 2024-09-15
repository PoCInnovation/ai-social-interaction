class DataConfig:
    SERVER_HOST = '127.0.0.1'
    SERVER_PORT = 12346
    BUFFER_SIZE = 1024
    MAX_CLIENTS = 20

    INVALID_ACTION = "The action you sent is not valid"
    INVALID_DISCUSSION_GROUP = "The discussion group you sent is invalid"
    INVALID_LOCATION = "The location you sent is invalid"
    INVALID_SENDER = "The sender is invalid or missing"
    MISSING_ARGUMENTS = "The message is missing required arguments"
    ERROR_MESSAGE = "There is one or multiple errors in the message you sent"
    ZONE_ERROR = "There is an error with your current zone"
    PERSON_ERROR = "The person you are trying to talk to does not exist or is currently not in your zone"