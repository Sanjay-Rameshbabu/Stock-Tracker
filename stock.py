import tkinter as tk
from tkinter import ttk, messagebox,filedialog
import customtkinter as ctk
import mysql.connector
import matplotlib.pyplot as plt
# import login

from fpdf import FPDF

ctk.set_appearance_mode("dark")  # setting mode for the window
ctk.set_default_color_theme("green")  # sets the colors for the objects

open_to_edit = 1

def generate():
    open_to_edit = 0
    rows = table.get_children()
    for row in rows:
        table.delete(row)
    mydb = mysql.connector.connect(host="localhost", user="root", passwd="root", database="stocks")
    mycursor = mydb.cursor()
    mycursor.execute("select * from stock_info")
    i = 0
    for row in mycursor:
        if (row[7] > 0):
            my_tag = 'profit_con'
        else:
            my_tag = 'loss_con'
        table.insert("", i, values=(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]), tags=my_tag)
        i += 1
    mydb.commit()
    mydb.close()
    messagebox.showinfo("Successful", "All records generated")


# generate graph
def generate_graph():
    open_to_edit = 1
    mydb = mysql.connector.connect(host="localhost", user="root", passwd="root", database='stocks')
    mycursor = mydb.cursor()

    query1 = "select stock_name from stock_info "
    mycursor.execute(query1)
    values1 = [row[0] for row in mycursor]

    query2 = "select profit from stock_info where profit is not null"
    mycursor.execute(query2)
    values2 = [row[0] for row in mycursor]

    # Separate positive and negative values
    positive_values = [val if val > 0 else 0 for val in values2]
    negative_values = [val if val < 0 else 0 for val in values2]

    # Plot positive values
    plt.bar(values1, positive_values, color='green', alpha=0.5, label='Profit')

    # Plot negative values below the x-axis
    plt.bar(values1, negative_values, color='red', alpha=0.5, label='Loss')

    plt.xlabel('Stock Name')
    plt.ylabel('Profit/Loss')
    plt.title('Stocks Vs Sales')
    plt.legend()

    plt.show()
    mydb.commit()
    mydb.close()
    messagebox.showinfo("Success", "Graph has been generated")


# Function Definitions
from datetime import datetime

def insert():
    mydb = mysql.connector.connect(host="localhost", user="root", passwd="root", database='stocks')
    mycursor = mydb.cursor()

    # Check if any required input is missing
    if not all((name_entry.get(), price_entry.get(), quantity_entry.get(), total_entry.get(),
                buy_date_entry.get(), sell_price_entry.get(), sell_date_entry.get(), profit_entry.get())):
        messagebox.showinfo("Warning", "Please fill in all the required fields.")
        return

    # Validate and format the dates
    try:
        buy_date = datetime.strptime(buy_date_entry.get(), "%d/%m/%Y").strftime("%Y-%m-%d")
        sell_date = datetime.strptime(sell_date_entry.get(), "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Error", "Invalid date format. Please use DD/MM/YYYY.")
        return
    
    # Validate numeric inputs
    try:
        price = float(price_entry.get())
        quantity = int(quantity_entry.get())
        sell_price = float(sell_price_entry.get())

        if price < 0 or quantity < 0 or sell_price < 0:
            messagebox.showerror("Error", "Price, Quantity, and Selling Price cannot be negative.")
            return
    except ValueError:
        messagebox.showerror("Error", "Invalid numeric input for Price, Quantity, or Selling Price.")
        return
    
    # Insert into the database
    try:
        mycursor.execute("INSERT INTO stock_info VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (
            name_entry.get(),
            price_entry.get(),
            quantity_entry.get(),
            total_entry.get(),
            buy_date,
            sell_price_entry.get(),
            sell_date,
            profit_entry.get(),
        ))
        mydb.commit()
        messagebox.showinfo("Success", "Record has been inserted")
        generate()
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Database error: {err}")
    finally:
        mydb.close()

def search():
    open_to_edit = 0
    mydb = mysql.connector.connect(host="localhost", user="root", passwd="root", database='stocks')
    mycursor = mydb.cursor()

    # Search for records matching the stock name
    mycursor.execute("SELECT * FROM stock_info WHERE stock_name = %s", (name_entry.get(),))
    result = mycursor.fetchall()

    if not result:
        messagebox.showinfo("Warning", "No records found")
        return

    # If multiple records are found, let the user select one
    if len(result) > 1:
        # Create a selection dialog
        def select_record():
            selected_index = listbox.curselection()
            if selected_index:
                populate_fields(result[selected_index[0]])
                selection_window.destroy()
            else:
                messagebox.showinfo("Info", "Please select a record.")

        # Create a new window to display options
        selection_window = tk.Toplevel()
        selection_window.title("Select a Record")
        selection_window.geometry("400x700")

        tk.Label(selection_window, text="Multiple records found. Select one:").pack(pady=10)
        listbox = tk.Listbox(selection_window, width=50, height=15)
        listbox.pack(padx=10, pady=10)

        # Populate listbox with details of records
        for idx, row in enumerate(result):
            listbox.insert(tk.END, f"Record {idx + 1}: {row}")

        tk.Button(selection_window, text="Select", command=select_record).pack(pady=10)
    else:
        # Only one record, directly populate the fields
        populate_fields(result[0])

def populate_fields(row):
    # Clear and populate the entry fields with the selected record's data
    price_entry.delete(0, tk.END)
    price_entry.insert(0, row[1])

    quantity_entry.delete(0, tk.END)
    quantity_entry.insert(0, row[2])

    total_entry.delete(0, tk.END)
    total_entry.insert(0, row[3])

    buy_date_entry.delete(0, tk.END)
    buy_date_entry.insert(0, row[4])

    sell_price_entry.delete(0, tk.END)
    sell_price_entry.insert(0, row[5])

    sell_date_entry.delete(0, tk.END)
    sell_date_entry.insert(0, row[6])

    profit_entry.delete(0, tk.END)
    profit_entry.insert(0, row[7])


def update():
    open_to_edit = 0
    mydb = mysql.connector.connect(host="localhost", user="root", passwd="root", database='stocks')
    mycursor = mydb.cursor()
    update_query = """
        UPDATE stock_info
        SET 
            stock_name = %s,
            price = %s,
            quantity = %s,
            total = %s,
            buy_date = %s,
            sell_price = %s,
            sell_date = %s,
            profit = %s
        WHERE stock_name = %s AND buy_date = %s
    """
    if not all((name_entry.get(), price_entry.get(), quantity_entry.get(), total_entry.get(),
                buy_date_entry.get(), sell_price_entry.get(), sell_date_entry.get(), profit_entry.get())):
        messagebox.showinfo("Warning", "Please fill in all the required fields.")
        return
    mycursor.execute(update_query, (name_entry.get(),
                                    price_entry.get(),
                                    quantity_entry.get(),
                                    total_entry.get(),
                                    buy_date_entry.get(),
                                    sell_price_entry.get(),
                                    sell_date_entry.get(),
                                    profit_entry.get(),
                                    name_entry.get(),  # Used in WHERE clause
                                    buy_date_entry.get()  # Used in WHERE clause
                                    ))
    mydb.commit()
    mydb.close()
    messagebox.showinfo("Success", "Updated successfully")
    generate()

def clear():
    name_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)
    quantity_entry.delete(0, tk.END)
    total_entry.delete(0, tk.END)
    buy_date_entry.delete(0, tk.END)
    sell_price_entry.delete(0, tk.END)
    sell_date_entry.delete(0, tk.END)
    profit_entry.delete(0, tk.END)

def delete():
    mydb = mysql.connector.connect(host="localhost", user="root", passwd="root", database='stocks')
    mycursor = mydb.cursor()
    name = name_entry.get()
    buydate=buy_date_entry.get()
    
    if not name:
        messagebox.showinfo("Warning", "No input found")
    else:
        try:
            del_query = "DELETE FROM stock_info WHERE stock_name = %s AND buy_date =%s"
            # Pass the variable as a tuple
            mycursor.execute(del_query, (name,buydate))
            mydb.commit()
            messagebox.showinfo("Deleted", "The record is deleted successfully")
            generate()  # Ensure generate() is defined elsewhere
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            mycursor.close()
            mydb.close()


def calculate_total(*args):
        try:
            quantity = float(quantity_var.get())
            price = float(price_var.get())
            total = quantity * price
            total_var.set(f"{total:.2f}")
        except ValueError:
            total_var.set("")

def calculate_profit(*args):
        try:
            quantity = float(quantity_var.get())
            sell_price = float(sell_var.get())
            price = float(price_var.get())
            profit = (sell_price * quantity) - (price * quantity)
            profit_var.set(f"{profit:.2f}")
        except ValueError:
            profit_var.set("")


def generatepdf():
    mydb = mysql.connector.connect(host="localhost", user="root", passwd="root", database="stocks")
    mycursor = mydb.cursor()
    
    # Initialize FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Fetch data from database
    mycursor.execute('SELECT * FROM stock_info')
    rows = mycursor.fetchall()

    for row in rows:
        pdf.cell(200, 10, txt=f"Stock Name: {row[0]}", ln=True, align='L')
        pdf.cell(200, 10, txt=f"Buy Price: {row[1]}", ln=True, align='L')
        pdf.cell(200, 10, txt=f"Quantity: {row[2]}", ln=True, align='L')
        pdf.cell(200, 10, txt=f"Total Price: {row[3]}", ln=True, align='L')
        pdf.cell(200, 10, txt=f"Buy Date: {row[4]}", ln=True, align='L')
        pdf.cell(200, 10, txt=f"Sell Price: {row[5]}", ln=True, align='L')
        pdf.cell(200, 10, txt=f"Sell Date: {row[6]}", ln=True, align='L')
        pdf.cell(200, 10, txt=f"Profit: {row[7]}", ln=True, align='L')
        pdf.cell(200, 10, txt="---------------------------------------", ln=True, align='L')
    
    # Save dialog
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    save_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        title="Save PDF Report"
    )

    if save_path:
        try:
            pdf.output(save_path)
            messagebox.showinfo("Success", "Report PDF is generated")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
    else:
        messagebox.showwarning("Warning", "No file selected")

    mydb.close()

# App creation
app = ctk.CTk()
app.title("Stock Tracker")
app.geometry("1200x500")
app.resizable()

# frame creation
side_frame = ctk.CTkFrame(app, width=300,
                          height=500,
                          border_color='gray',
                          border_width=3,
                          corner_radius=10)
side_frame.pack(side='left', expand=0)

# tab view
menu = ctk.CTkTabview(side_frame,
                      width=500,
                      height=500,
                      fg_color='black',
                      segmented_button_fg_color='black',
                      segmented_button_selected_hover_color='green',
                      segmented_button_unselected_color='black')
tab1 = menu.add("View mode")

menu.pack(fill='both', expand=1)

# Search mode frame

name_label = ctk.CTkLabel(tab1, text='Stock Name', font=('Ex 2.0', 15, 'bold')).place(x=10, y=10)
name_entry = ctk.CTkEntry(tab1)
name_entry.place(x=150, y=10)

price_label = ctk.CTkLabel(tab1, text='Price', font=('Ex 2.0', 15, 'bold')).place(x=10, y=40)
price_var = tk.StringVar()
price_entry = ctk.CTkEntry(tab1, textvariable=price_var)
price_entry.place(x=150, y=40)

quantity_label = ctk.CTkLabel(tab1, text='Quantity', font=('Ex 2.0', 15, 'bold')).place(x=10, y=70)
quantity_var = tk.StringVar()
quantity_entry = ctk.CTkEntry(tab1, textvariable=quantity_var)
quantity_entry.place(x=150, y=70)

total_label = ctk.CTkLabel(tab1, text='Total Price', font=('Ex 2.0', 15, 'bold')).place(x=10, y=100)
total_var = tk.StringVar()
total_entry = ctk.CTkEntry(tab1, textvariable=total_var)
total_entry.place(x=150, y=100)

buy_date_label = ctk.CTkLabel(tab1, text='Buy date', font=('Ex 2.0', 15, 'bold')).place(x=10, y=130)
buy_date_entry = ctk.CTkEntry(tab1)
buy_date_entry.place(x=150, y=130)

sell_price_label = ctk.CTkLabel(tab1, text='Sell Price', font=('Ex 2.0', 15, 'bold')).place(x=10, y=160)
sell_var = tk.StringVar()
sell_price_entry = ctk.CTkEntry(tab1, textvariable=sell_var)
sell_price_entry.place(x=150, y=160)

sell_date_label = ctk.CTkLabel(tab1, text='Sell date', font=('Ex 2.0', 15, 'bold')).place(x=10, y=190)
sell_date_entry = ctk.CTkEntry(tab1)
sell_date_entry.place(x=150, y=190)

profit_label = ctk.CTkLabel(tab1, text='Profit gained', font=('Ex 2.0', 15, 'bold')).place(x=10, y=220)
profit_var = tk.StringVar()
profit_entry = ctk.CTkEntry(tab1, textvariable=profit_var)
profit_entry.place(x=150, y=220)

quantity_var.trace_add("write", calculate_total)
price_var.trace_add("write", calculate_total)
sell_var.trace_add("write", calculate_profit)
quantity_var.trace_add("write", calculate_profit)
price_var.trace_add("write", calculate_profit)

# Buttons
generate_btn = ctk.CTkButton(tab1, text='GENERATE DATA', font=('sans', 15, 'bold'), fg_color='blue', width=10,
                             command=generate).place(x=0, y=400)
generate_graph_btn = ctk.CTkButton(tab1, text='GENERATE GRAPH', font=('sans', 15, 'bold'), fg_color='blue', width=10,
                                   command=generate_graph).place(x=150, y=400)
generate_report_btn = ctk.CTkButton(tab1, text='GENERATE REPORT', font=('sans', 15, 'bold'), fg_color='blue', width=10,
                                    command=generatepdf).place(x=310, y=400)
update_btn = ctk.CTkButton(tab1, text='UPDATE', font=('sans', 15, 'bold'), fg_color='blue', width=10,
                           command=update).place(x=300, y=300)
insert_btn = ctk.CTkButton(tab1, text='INSERT', font=('sans', 15, 'bold'), fg_color='blue', width=10,
                           command=insert).place(x=0, y=300)
search_btn = ctk.CTkButton(tab1, text='SEARCH', font=('sans', 15, 'bold'), fg_color='blue', width=10,
                           command=search).place(x=100, y=300)
delete_btn = ctk.CTkButton(tab1, text='DELETE', font=('sans', 15, 'bold'), fg_color='blue', width=10,
                           command=delete).place(x=200, y=300)
clear_btn = ctk.CTkButton(tab1, text='CLEAR', font=('sans', 15, 'bold'), fg_color='blue', width=20,
                          command=clear).place(x=300, y=250)

# table
table = ttk.Treeview(app)
table['columns'] = ("Stock_Name", "Price", "Quantity", "Total_Price", "Buy_Date", "Sell_Price", "Sell_Date", "Profit")
table.column("#0", width=0, stretch='NO')
table.column("Stock_Name", width=100, minwidth=100, anchor=tk.CENTER)
table.column("Price", width=100, minwidth=100, anchor=tk.CENTER)
table.column("Quantity", width=100, minwidth=100, anchor=tk.CENTER)
table.column("Total_Price", width=100, minwidth=100, anchor=tk.CENTER)
table.column("Buy_Date", width=100, minwidth=100, anchor=tk.CENTER)
table.column("Sell_Price", width=100, minwidth=100, anchor=tk.CENTER)
table.column("Sell_Date", width=100, minwidth=100, anchor=tk.CENTER)
table.column("Profit", width=100, minwidth=100, anchor=tk.CENTER)

table.heading("Stock_Name", text='Stock Name', anchor=tk.CENTER)
table.heading("Price", text='Price per stock', anchor=tk.CENTER)
table.heading("Quantity", text='Quantity', anchor=tk.CENTER)
table.heading("Total_Price", text='Total price', anchor=tk.CENTER)
table.heading("Buy_Date", text='Buying date', anchor=tk.CENTER)
table.heading("Sell_Price", text='Selling Price', anchor=tk.CENTER)
table.heading("Sell_Date", text='Selling Date', anchor=tk.CENTER)
table.heading("Profit", text='Profit gained', anchor=tk.CENTER)

table.tag_configure("profit_con", background="lightgreen", font=('Ex 2.0', 12), foreground="black")
table.tag_configure("loss_con", background="red", font=('Ex 2.0', 12), foreground='yellow')
my_tag = 'profit_con'

table.pack(fill='both', expand=1)

app.mainloop()