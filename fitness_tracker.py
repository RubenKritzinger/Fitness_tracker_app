import sqlite3
from sqlite3 import Error
from datetime import datetime
import os

# Function to create a SQLite database connection


def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print("Error creating database connection:", e)
        return None

# Function to create database tables


def create_tables(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exercise_logs (
                log_id INTEGER PRIMARY KEY,
                username TEXT,
                exercise_name TEXT,
                date TEXT,
                duration INTEGER,
                sets INTEGER,
                reps INTEGER,
                weight REAL,
                notes TEXT,
                completed BOOLEAN DEFAULT 0,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workout_categories (
                category_id INTEGER PRIMARY KEY,
                category_name TEXT UNIQUE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workout_goals (
                goal_id INTEGER PRIMARY KEY,
                username TEXT,
                goal_name TEXT,
                progress REAL,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        """)
        connection.commit()
        cursor.close()
    except Error as e:
        print("Error creating tables:", e)

# Function to validate password


def validate_password(password):
    return len(password) >= 7 and any(char.isupper() for char in password) and any(char in "!@#$%^&*()-_+=<>,.?/:;{}[]|\\~" for char in password)

# Function to create a user account


def create_account(connection):
    try:
        username = input("Enter your desired username: ")
        if len(username) < 5:
            print("Username must be at least 5 characters long.")
            return
        password = input("Enter your password: ")
        if not validate_password(password):
            print("Password must be at least 7 characters long, contain at least 1 uppercase letter, and 1 special character.")
            return
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        connection.commit()
        cursor.close()
        print("Account created successfully.")
    except Error as e:
        print("Error creating account:", e)

# Function to log in


def login(connection):
    try:
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        cursor.close()
        if user:
            print("Login successful.")
            return username
        else:
            print("Invalid username or password.")
            return None
    except Error as e:
        print("Error logging in:", e)
        return None

# Function to display menu options and get user input


def display_menu():
    try:
        print("Fitness Tracker Menu:")
        print("1. Log Exercise")
        print("2. View Exercise Log")
        print("3. Mark Exercise as Completed")
        print("4. Manage Workout Categories")
        print("5. Manage Workout Goals")
        print("6. View Progress towards Fitness Goals")
        print("9. Quit")
        choice = input("Enter your choice: ")
        return choice
    except KeyboardInterrupt:
        print("\nExiting...")
        return "9"  # Return quit option on keyboard interrupt

# Function to handle user choice


def handle_choice(connection, choice, username):
    try:
        if choice == "1":
            log_exercise(connection, username)
        elif choice == "2":
            view_exercise_log(connection, username)
        elif choice == "3":
            mark_exercise_completed(connection, username)
        elif choice == "4":
            manage_workout_categories(connection)
        elif choice == "5":
            manage_workout_goals(connection, username)
        elif choice == "6":
            view_progress(connection, username)
        else:
            print("Invalid choice. Please try again.")
    except Error as e:
        print("Error handling choice:", e)

# Function to log exercise


def log_exercise(connection, username):
    try:
        cursor = connection.cursor()
        exercise_name = input("Enter the name of the exercise: ")
        date = input("Enter the date (YYYY-MM-DD): ")
        duration = int(input("Enter the duration (minutes): "))
        sets = int(input("Enter the number of sets: "))
        reps = int(input("Enter the number of reps per set: "))
        weight = float(input("Enter the weight (kg): "))
        notes = input("Enter any notes (optional): ")
        cursor.execute("""
            INSERT INTO exercise_logs (username, exercise_name, date, duration, sets, reps, weight, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (username, exercise_name, date, duration, sets, reps, weight, notes))
        connection.commit()
        cursor.close()
        print("Exercise logged successfully.")
    except (Error, ValueError) as e:
        print("Error logging exercise:", e)

# Function to view exercise log


def view_exercise_log(connection, username):
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM exercise_logs WHERE username = ?", (username,))
        exercise_logs = cursor.fetchall()
        cursor.close()
        if exercise_logs:
            print("Exercise Logs:")
            for log in exercise_logs:
                log_id, _, exercise_name, date, duration, sets, reps, weight, notes, completed = log
                print(f"Log ID: {log_id}")
                print(f"Exercise Name: {exercise_name}")
                print(f"Date: {date}")
                print(f"Duration: {duration} minutes")
                print(f"Sets: {sets}")
                print(f"Reps per Set: {reps}")
                print(f"Weight: {weight} kg")
                print(f"Notes: {notes}")
                print(f"Completed: {'Yes' if completed else 'No'}")
                print()
        else:
            print("No exercise logs found.")
    except Error as e:
        print("Error viewing exercise log:", e)

# Function to mark exercise as completed


def mark_exercise_completed(connection, username):
    try:
        cursor = connection.cursor()
        log_id = int(
            input("Enter the Log ID of the exercise to mark as completed: "))
        cursor.execute(
            "UPDATE exercise_logs SET completed = 1 WHERE log_id = ? AND username = ?", (log_id, username))
        connection.commit()
        if cursor.rowcount > 0:
            print("Exercise marked as completed successfully.")
        else:
            print("No exercise log found with the provided Log ID.")
        cursor.close()
    except (Error, ValueError) as e:
        print("Error marking exercise as completed:", e)

# Function to manage workout categories


def manage_workout_categories(connection):
    try:
        print("Workout Categories:")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM workout_categories")
        categories = cursor.fetchall()
        cursor.close()
        if categories:
            for category in categories:
                print(f"Category ID: {category[0]}, Name: {category[1]}")
            print("\n1. Add New Category")
            print("2. Update Category")
            print("3. Delete Category")
            choice = input("Enter your choice: ")
            if choice == "1":
                add_workout_category(connection)
            elif choice == "2":
                update_workout_category(connection)
            elif choice == "3":
                delete_workout_category(connection)
            else:
                print("Invalid choice. Please try again.")
        else:
            print("No workout categories found.")
    except Error as e:
        print("Error managing workout categories:", e)

# Function to add a new workout category


def add_workout_category(connection):
    try:
        category_name = input("Enter the name of the new category: ")
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO workout_categories (category_name) VALUES (?)", (category_name,))
        connection.commit()
        cursor.close()
        print("New category added successfully.")
    except Error as e:
        print("Error adding workout category:", e)

# Function to update a workout category


def update_workout_category(connection):
    try:
        category_id = input("Enter the ID of the category to update: ")
        new_name = input("Enter the new name for the category: ")
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE workout_categories SET category_name = ? WHERE category_id = ?", (new_name, category_id))
        connection.commit()
        cursor.close()
        print("Category name updated successfully.")
    except Error as e:
        print("Error updating workout category:", e)

# Function to delete a workout category


def delete_workout_category(connection):
    try:
        category_id = input("Enter the ID of the category to delete: ")
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM workout_categories WHERE category_id = ?", (category_id,))
        connection.commit()
        cursor.close()
        print("Category deleted successfully.")
    except Error as e:
        print("Error deleting workout category:", e)

# Function to manage workout goals


def manage_workout_goals(connection, username):
    try:
        print("Workout Goals:")
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM workout_goals WHERE username = ?", (username,))
        goals = cursor.fetchall()
        cursor.close()
        if goals:
            for goal in goals:
                print(f"Goal ID: {goal[0]}")
                print(f"Goal: {goal[2]}")
                print(f"Progress: {goal[3]}%")
                print()
        else:
            print("No workout goals found.")

        print("\n1. Add New Goal")
        print("2. Update Goal Progress")
        print("3. Delete Goal")
        choice = input("Enter your choice: ")

        if choice == "1":
            add_workout_goal(connection, username)
        elif choice == "2":
            update_goal_progress(connection)
        elif choice == "3":
            delete_workout_goal(connection)
        else:
            print("Invalid choice. Please try again.")
    except Error as e:
        print("Error managing workout goals:", e)

# Function to add a new workout goal


def add_workout_goal(connection, username):
    try:
        goal_name = input("Enter the description of the new goal: ")
        progress = float(input("Enter the current progress (in percentage): "))
        cursor = connection.cursor()
        cursor.execute("INSERT INTO workout_goals (username, goal_name, progress) VALUES (?, ?, ?)",(username, goal_name, progress))
        connection.commit()
        cursor.close()
        print("New goal added successfully.")
    except Error as e:
        print("Error adding workout goal:", e)

# Function to update goal progress


def update_goal_progress(connection):
    try:
        goal_id = int(input("Enter the ID of the goal to update: "))
        new_progress = float(input("Enter the new progress (in percentage): "))
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE workout_goals SET progress = ? WHERE goal_id = ?", (new_progress, goal_id))
        connection.commit()
        cursor.close()
        print("Goal progress updated successfully.")
    except Error as e:
        print("Error updating goal progress:", e)

# Function to delete a workout goal


def delete_workout_goal(connection):
    try:
        goal_id = int(input("Enter the ID of the goal to delete: "))
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM workout_goals WHERE goal_id = ?", (goal_id,))
        connection.commit()
        cursor.close()
        print("Goal deleted successfully.")
    except Error as e:
        print("Error deleting workout goal:", e)

# Function to view progress towards fitness goals


def view_progress(connection, username):
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM workout_goals WHERE username = ?", (username,))
        goals = cursor.fetchall()
        cursor.close()
        if goals:
            print("Fitness Goals Progress:")
            for goal in goals:
                print(f"Goal: {goal[2]}")
                print(f"Progress: {goal[3]}%")
                print()
        else:
            print("No workout goals found.")
    except Error as e:
        print("Error viewing progress towards fitness goals:", e)

# Main function


def main():
    database = "fitness_tracker.db"  # SQLite database file

    # Delete the existing database file if it exists
    if os.path.exists(database):
        os.remove(database)

    # Create a database connection
    connection = create_connection(database)
    if connection is None:
        print("Error: Unable to connect to the database.")
        return

    # Create necessary tables if they don't exist
    create_tables(connection)

    # Main loop
    while True:
        print("\nWelcome to Fitness Tracker!")
        print("1. Log In")
        print("2. Create Account")
        print("3. Quit")
        choice = input("Enter your choice: ")

        if choice == "1":
            username = login(connection)
            if username:
                while True:
                    choice = display_menu()
                    if choice == "9":
                        print("Exiting...")
                        break
                    handle_choice(connection, choice, username)

        elif choice == "2":
            create_account(connection)

        elif choice == "3":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
