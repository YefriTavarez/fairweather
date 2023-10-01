# Copyright (c) 2023, Yefri Tavarez and contributors
# For license information, please see license.txt


class InvalidContactEmailConfigurationError(Exception):
    """
        Raised when the contact email configuration is invalid.
        Error code: 0 corresponds to an unknown error.
        Error code: 1 corresponds to a not found contact person.
        Error code: 2 corresponds to a not found customer.
        Error code: 3 corresponds to a not found contact email.
    """
    error_code: str = 0
    error_message: str = "Unknown Error"

    def __init__(self, error_code: int, error_message: str):
        self.error_code = error_code
        self.error_message = error_message

        super().__init__(self.error_message)

    def __str__(self):
        return f"{self.error_code}: {self.error_message}"

    def __repr__(self):
        return f"{self.error_code}: {self.error_message}"
