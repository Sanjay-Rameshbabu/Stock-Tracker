import customtkinter as ctk
from tkinter import messagebox
import mysql.connector
import hashlib

# User registration function
def register():
    def submit_registration():
        username = username_entry.get()
        password = password_entry.get()
        confirm_password = confirm_password_entry.get()

        if not username or not password or not confirm_password:
            messagebox.showwarning("Warning", "Please fill in all fields")
            return
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        try:
            mydb = mysql.connector.connect(host="localhost", user="root", passwd="root", database="stocks")
            mycursor = mydb.cursor()
            mycursor.execute("INSERT INTO login (username, password) VALUES (%s, %s)", (username,password))
            mycursor.execute("INSERT INTO register (username, password) VALUES (%s, %s)",
                             (username, password))
            mydb.commit()
            mydb.close()
            messagebox.showinfo("Success", "Registration successful! Please log in.")
            register_window.destroy()  # Close the register window
            login_window.deiconify()  # Show the login window again

        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error: {err}")
            mydb.close()

    login_window.withdraw()  # Hide the login window

    # Create the registration window
    register_window = ctk.CTkToplevel(login_window)
    register_window.title("Register")
    register_window.geometry("400x400")

    # # Ensure the register window is always on top of the login window
    register_window.grab_set()

    # # Creating a frame for card look
    frame = ctk.CTkFrame(register_window, width=350, height=350, corner_radius=15, fg_color="white")
    frame.place(relx=0.5, rely=0.5, anchor="center")

    # # Title label inside the frame
    ctk.CTkLabel(frame, text="Register", font=("Arial", 25, "bold"), text_color="black").pack(pady=20)

    # Username input field with rounded borders
    ctk.CTkLabel(frame, text="Username:", font=("Arial", 14, "bold"), text_color="black").pack(pady=5)
    username_entry = ctk.CTkEntry(frame, width=300, font=("Arial", 14), border_width=2, corner_radius=10, fg_color="black", text_color="white")
    username_entry.pack(pady=10)

    # Password input field with rounded borders
    ctk.CTkLabel(frame, text="Password:", font=("Arial", 14, "bold"), text_color="black").pack(pady=5)
    password_entry = ctk.CTkEntry(frame, show="*", width=300, font=("Arial", 14), border_width=2, corner_radius=10, fg_color="black", text_color="white")
    password_entry.pack(pady=10)

    # Confirm Password input field with rounded borders
    ctk.CTkLabel(frame, text="Confirm Password:", font=("Arial", 14, "bold"), text_color="black").pack(pady=5)
    confirm_password_entry = ctk.CTkEntry(frame, show="*", width=300, font=("Arial", 14), border_width=2, corner_radius=10, fg_color="black", text_color="white")
    confirm_password_entry.pack(pady=10)

    # Register button with rounded borders
    ctk.CTkButton(frame, text="Register", command=submit_registration, width=200, height=40, font=("Arial", 14), fg_color="green", hover_color="lightgreen", corner_radius=10).pack(pady=20)
    register_window.protocol("WM_DELETE_WINDOW", lambda: (register_window.destroy(), login_window.deiconify()))  # Handle 'X' button


# User login function
def login():
    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        messagebox.showwarning("Warning", "Please fill in all fields")
        return

    try:
        mydb = mysql.connector.connect(host="localhost", user="root", passwd="root", database="stocks")
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM login WHERE username = %s AND password = %s", (username,password))
        user = mycursor.fetchone()
        mydb.close()
        if user:
            messagebox.showinfo("Success", "Login successful!")
            login_window.destroy()
            import stock # Call your function to launch the stock tracker here
        else:
            messagebox.showerror("Error", "Invalid username or password")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error: {err}")


# Login window
login_window = ctk.CTk()
login_window.title("Login")
login_window.geometry("400x400")

# Creating a frame for card look
frame = ctk.CTkFrame(login_window, width=350, height=350, corner_radius=15, fg_color="white")
frame.place(relx=0.5, rely=0.5, anchor="center")

# Title label inside the frame
ctk.CTkLabel(frame, text="Login", font=("Arial", 25, "bold"), text_color="black").pack(pady=20)

# Username input field with rounded borders
ctk.CTkLabel(frame, text="Username:", font=("Arial", 14, "bold"), text_color="black").pack(pady=5)
username_entry = ctk.CTkEntry(frame, width=300, font=("Arial", 14), border_width=2, corner_radius=10, fg_color="black", text_color="white")
username_entry.pack(pady=10)

# Password input field with rounded borders
ctk.CTkLabel(frame, text="Password:", font=("Arial", 14, "bold"), text_color="black").pack(pady=5)
password_entry = ctk.CTkEntry(frame, show="*", width=300, font=("Arial", 14), border_width=2, corner_radius=10, fg_color="black", text_color="white")
password_entry.pack(pady=10)

# Login and Register buttons
ctk.CTkButton(frame, text="Login", command=login, width=200, height=40, font=("Arial", 14), fg_color="blue", hover_color="green", corner_radius=10).pack(pady=10)
ctk.CTkButton(frame, text="Register", command=register, width=200, height=40, font=("Arial", 14), fg_color="blue", hover_color="green", corner_radius=10).pack(pady=10)

login_window.mainloop()
