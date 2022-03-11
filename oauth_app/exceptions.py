class GlobalException(Exception):
    def __init__(self, status_code: int, error: str, error_description: str):
        self.status_code = status_code
        self.error = error
        self.error_description = error_description