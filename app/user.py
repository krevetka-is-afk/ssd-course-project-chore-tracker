class User:

    def __init__(self, user_name: str, user_email: str, user_password: str):
        self.user_name = user_name
        self.user_email = user_email
        self.user_password = user_password

    # change user info methods
    def change_user_name(self, new_user_name: str) -> None:
        self.user_name = new_user_name

    def change_user_email(self, new_user_email: str) -> None:
        self.user_email = new_user_email

    # business logic methods
    def create_chore(self):
        pass

    def assign_chore(self):
        pass

    def complete_chore(self):
        pass
