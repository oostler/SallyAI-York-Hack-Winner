import random
import utils

def play_game():
    print("🎯 Welcome to the Guessing Game!")
    number_to_guess = random.randint(1, 100)
    attempts = 0

    while True:
        guess = utils.get_integer_input("Enter your guess (1-100): ")
        attempts += 1

        if guess < number_to_guess:
            print("📉 Too low! Try again.")
        elif guess > number_to_guess:
            print("📈 Too high! Try again.")
        else:
            print(f"🎉 Congrats! You guessed the number {number_to_guess} in {attempts} attempts.")
            break