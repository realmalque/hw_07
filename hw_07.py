
from datetime import datetime
from collections import UserDict
# import pickle

# def save_data(book, filename="addressbook.pkl"):
#     with open(filename, "wb") as f:
#         pickle.dump(book, f)

# def load_data(filename="addressbook.pkl"):
#     try:
#         with open(filename, "rb") as f:
#             return pickle.load(f)
#     except FileNotFoundError:
#         return AddressBook()

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, name):
        if not name:
            raise ValueError("Name must not be empty.")
        super().__init__(name)

class Phone(Field):
    def __init__(self, phone):
        if not phone.isdigit() or len(phone) != 10:
            raise ValueError("Phone number must have 10 digits.")
        super().__init__(phone)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for ph in self.phones:
            if ph.value == phone:
                self.phones.remove(ph)

    def edit_phone(self, old_phone, new_phone):
        for ph in self.phones:
            if ph.value == old_phone:
                if not new_phone.isdigit() or len(new_phone) != 10:
                    raise ValueError("New phone number must be a 10-digit number.")
                ph.value = new_phone
                return
        raise ValueError("Phone number to edit does not exist.")

    def __str__(self):
        birthday_str = str(self.birthday.value.strftime("%d.%m.%Y")) if self.birthday else 'Not specified'
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []
        for user in self.data.values():
            if user.birthday:
                birthday_this_year = datetime(today.year, user.birthday.value.month, user.birthday.value.day).date()
                if birthday_this_year < today:
                    continue
                elif (birthday_this_year - today).days < 7:
                    if birthday_this_year.weekday() == 5:  # Saturday
                        birthday_this_year = datetime(birthday_this_year.year, birthday_this_year.month, birthday_this_year.day + 2).date()  # Changing the day to Monday
                    elif birthday_this_year.weekday() == 6:  # Sunday
                        birthday_this_year = datetime(birthday_this_year.year, birthday_this_year.month, birthday_this_year.day + 1).date()  # Changing the day to Monday
                    user_info = {"name": user.name.value, "congratulation_date": birthday_this_year.strftime("%d.%m.%Y")}
                    upcoming_birthdays.append(user_info)
        return upcoming_birthdays

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "This command cannot be executed."
        except ValueError:
            return "Give me name and phone please."
        except IndexError:
            return "There is no such information."
        except Exception as e:
            return f"Error: {e}"
    return inner

@input_error
def add_birthday(args, book):
    name, birthday = args
    try:
        record = book.find(name)
        if record:
            record.add_birthday(birthday)
            print(f"Birthday added for {name}.")
        else:
            print(f"Contact {name} not found.")
    except ValueError as e:
        print(e)

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        print(f"{name}'s birthday: {record.birthday.value}")
    elif record and not record.birthday:
        print(f"{name} does not have a birthday specified.")
    else:
        print(f"Contact {name} not found.")

@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        print("Upcoming birthdays:")
        for record in upcoming_birthdays:
            print(f"The congratulation date for {record['name']} is {record['congratulation_date']}")
    else:
        print("No upcoming birthdays.")

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

def main():
    # book = load_data()
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            # save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            if len(args) < 2:
                print("Invalid number of arguments.")
                continue
            name, *phones = args
            record = book.find(name)
            if not record:
                record = Record(name)
                book.add_record(record)
            for phone in phones:
                record.add_phone(phone)
            print(f"Added new contact: {name} - {', '.join(phones)}")

        elif command == "change":
            if len(args) != 3:
                print("Invalid number of arguments.")
                continue
            name, old_phone, new_phone = args
            record = book.find(name)
            if record:
                record.edit_phone(old_phone, new_phone)
                print(f"Phone number changed for {name}.")
            else:
                print(f"Contact {name} not found.")

        elif command == "phone":
            if len(args) != 1:
                print("Invalid number of arguments.")
                continue
            name = args[0]
            record = book.find(name)
            if record:
                print(f"Phone numbers for {name}: {', '.join(p.value for p in record.phones)}")
            else:
                print(f"Contact {name} not found.")

        elif command == "all":
            print("All contacts:")
            for record in book.data.values():
                print(record)

        elif command == "add-birthday":
            if len(args) != 2:
                print("Invalid number of arguments.")
                continue
            add_birthday(args, book)

        elif command == "show-birthday":
            if len(args) != 1:
                print("Invalid number of arguments.")
                continue
            show_birthday(args, book)

        elif command == "birthdays":
            birthdays(args, book)

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
