def get_integer_input(prompt):
    """ Get a valid integer input from the user. """
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("⚠️ Invalid input! Please enter an integer.")