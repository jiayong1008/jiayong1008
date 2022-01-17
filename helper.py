def get_int(message, positive=False):
    while True:
        try:
            number = int(input(message))
            if positive and number < 1:
                raise ValueError
            return number
        except ValueError:
            print("Invalid Input")

def get_float(message):
    while True:
        try:
            decimal = float(input(message))
            return decimal
        except ValueError:
            print("Invalid Input")

# Helper function - Function that reprompts user if choice entered is invalid
def choice(message, options):
    while True:
        choice = get_int(message)
        if (choice in options):
            print()
            return choice
        print("Invalid Input.")