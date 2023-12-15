# Amirreza alasti - sina Mokhtari
import getpass
from typing import List
from enum import Enum
import abc


class Resource(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_name(self) -> str:
        pass

    @abc.abstractmethod
    def read(self) -> None:
        pass

    @abc.abstractmethod
    def write(self, content: str) -> None:
        pass


class Operation(Enum):
    READ = "read"
    WRITE = "write"


def get_operation_from_user() -> (Operation, str | None):
    user_input: str = input("Enter requested operation (read/write): ")
    while True:
        if user_input.lower() == Operation.READ.value:
            return (Operation.READ, None)
        elif user_input.lower() == Operation.WRITE.value:
            text: str = input("Enter the text you want to write: ")
            return (Operation.WRITE, text)
        else:
            user_input = input('Wrong input! Enter either "read" or "write": ')

class File(Resource):
    def __init__(self, name: str) -> None:
        self.name: str = name
        
    def get_name(self) -> str:
        return self.name

    def read(self) -> None:
        try:
            with open(self.name, "r") as file:
                print(file.read())
        except FileNotFoundError:
            print(f"File: {self.name} not found.")

    def write(self, content: str) -> None:
        with open(self.name, "w") as file:
            file.write(content)
        print(f"Written to file: {self.name}")


class Permission:
    def __init__(self, resource: Resource, allowed_operations: List[Operation]) -> None:
        self.resource: Resource = resource
        self.allowed_operations: List[Operation] = allowed_operations

    def check_resource(self, res: Resource):
        return res.get_name() == self.resource.get_name()

    def check_permission(self, res: Resource, operation: Operation) -> bool:
        if not res.get_name() == self.resource.get_name():
            return False

        return operation in self.allowed_operations

    def check_operation(self, operation: Operation) -> bool:
        return operation in self.allowed_operations

    def allow_operation(self, operation: Operation) -> None:
        if operation not in self.allowed_operations:
            self.allowed_operations.append(operation)

    def disallow_operation(self, operation: Operation) -> None:
        if operation in self.allowed_operations:
            self.allowed_operations.remove(operation)

class Role:
    def __init__(
        self, name: str, permissions: List[Permission], parent: "Role" = None
    ) -> None:
        self.name: str = name
        self.permissions: List[Permission] = permissions
        if parent:
            self.permissions += parent.permissions

class User:
    def __init__(self, username: str, password: str, roles: List[Role] = None) -> None:
        self.username: str = username
        self.password: str = password
        self.roles: List[Role] = roles

    def add_role(self, role: Role) -> None:
        self.roles.append(role)

    def remove_role(self, role: Role) -> None:
        if role in self.roles:
            self.roles.remove(role)

    def perform_operation(
        self, resource: Resource, operation: Operation, text: str = None
    ) -> bool:
        for role in self.roles:
            for perm in role.permissions:
                if perm.check_permission(resource, operation):
                    if operation == Operation.READ:
                        resource.read()
                        return True
                    elif operation == Operation.WRITE:
                        resource.write(text)
                        return True
                    else:
                        print("UNDEFINED OPERATION!")
                        return False
        print("Access denied!")
        return False

def login(users: List[User]) -> User:
    username: str = ""
    password: str = ""

    while True:
        username = input("Enter username: ")
        password = getpass.getpass("Enter password: ")

        for user in users:
            if user.username == username and user.password == password:
                print(f"Logged in successfully as {user.username}.")
                return user

        print("Invalid username or password. Try again.")



def main() -> None:
    public_file_1: File = File("pub_f1.txt")
    public_file_2: File = File("pub_f2.txt")
    secret_file_1: File = File("sec_f1.txt")

    users_list: List[User] = []

    user_role = Role(
        "user",
        [
            Permission(public_file_1, [Operation.READ]),
            Permission(public_file_2, [Operation.READ]),
        ],
    )
    admin_role = Role(
        "admin",
        [
            Permission(public_file_1, [Operation.WRITE]),
            Permission(public_file_2, [Operation.WRITE]),
            Permission(secret_file_1, [Operation.READ]),
            Permission(secret_file_1, [Operation.WRITE]),
        ],
        user_role,
    )

    users_list.append(User("alasti", "pass1", [user_role]))
    users_list.append(User("mokhtari", "pass2", [user_role]))
    users_list.append(User("user3", "pass3", [user_role]))
    users_list.append(User("user4", "pass4", [admin_role]))

    logged_in_user: User = login(users_list)

    while True:
        filename = input("Enter the name of the file: ")
        file = File(filename)

        operation, text = get_operation_from_user()

        logged_in_user.perform_operation(file, operation, text)


if __name__ == "__main__":
    main()
