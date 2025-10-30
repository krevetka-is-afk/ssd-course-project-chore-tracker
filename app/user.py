class User:

    def __init__(self, user_name: str, user_email: str, user_password: str):
        self.user_name = user_name
        self.user_email = user_email
        self.user_password = user_password

    def get_user_info(self):
        return {
            "name": self.user_name,
            "email": self.user_email,
            "password": self.user_password,
        }

    def change_user_name(self, new_user_name: str) -> None:
        self.user_name = new_user_name

    def change_user_email(self, new_user_email: str) -> None:
        self.user_email = new_user_email
