from fastapi import status


class AppException(Exception):
    """
    Exceção personalizada para tratamento de erros da aplicação
    """

    def __init__(self, code: str, message: str, status_code: int):
        self.code = code
        self.message = message
        self.status_code = status_code