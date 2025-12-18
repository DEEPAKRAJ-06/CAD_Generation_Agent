"""
Custom exception handling for CAD Agent from Scratch.

This module provides:
- Consistent error formatting
- File name and line number tracing
- Centralized logging integration
"""

import sys
from cad_agent_from_scratch.logger import logging


def error_message_detail(error: Exception, error_detail: sys) -> str:
    """
    Extract detailed error information including file name and line number.
    """
    _, _, exc_tb = error_detail.exc_info()

    file_name = exc_tb.tb_frame.f_code.co_filename
    line_number = exc_tb.tb_lineno

    error_message = (
        f"Error occurred in python script "
        f"[{file_name}] "
        f"at line number [{line_number}] "
        f"with error message [{str(error)}]"
    )

    return error_message


class CustomException(Exception):
    """
    Custom exception class that logs detailed error information.
    """

    def __init__(self, error: Exception, error_detail: sys):
        detailed_message = error_message_detail(error, error_detail)
        super().__init__(detailed_message)
        self.error_message = detailed_message

        # Log immediately when exception is created
        logging.error(self.error_message)

    def __str__(self) -> str:
        return self.error_message
