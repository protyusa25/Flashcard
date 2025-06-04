import mysql.connector
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ttkbootstrap import Style

# creating database tables if it has no existence
def create_tables(conn):
    cursor=conn.cursor()

    # creating flashcard_sets table
    cursor.execute('''
         CREATE TABLE IF NOT EXISTS flashcard_sets(
            id INT AUTO_INCREMENT PRIMARY KEY ,
            name TEXT NOT NULL           
        )
''')
    
    # creating flashcards table with foreign key reference to flashcard_sets
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flashcards(
            id INTEGER AUTO_INCREMENT PRIMARY KEY ,
            set_id INTEGER NOT NULL,
            word TEXT NOT NULL,
            definition TEXT NOT NULL,
            FOREIGN KEY (set_id) REFERENCES flashcard_sets(id)           
        )
''')
    
# adding a new flashcard
def add_set(conn,name):
    cursor=conn.cursor()

    # inserting the set name into flashcard_sets table
    cursor.execute('''
        INSERT INTO flashcard_sets (name)
        VALUES (%s)
''',(name,))
    
    set_id=cursor.lastrowid
    conn.commit()

    return set_id

# function for adding a flashcard in the database
def add_card(conn,set_id,word,definition):
    cursor=conn.cursor()

    # executing SQL query for inserting a new flashcard in the database
    cursor.execute('''
        INSERT INTO flashcards (set_id,word,definition)
        VALUES (%s,%s,%s)
''',(set_id,word,definition))
    
    # to get the "id" of a newly inserted card
    card_id=cursor.lastrowid
    conn.commit()

    return card_id


# function for retrieving all flashcard sets from the database
def get_sets(conn):
    cursor=conn.cursor()

    # executing SQL query for fetching all flashcard sets
    cursor.execute('''
        SELECT id,name FROM flashcard_sets
''')
    
    rows=cursor.fetchall()
    sets={row[1]: row[0] for row in rows} # creating a dictionary of sets (name: id)

    return sets

# function for retrieving all flashcards of a specific set
def get_cards(conn,set_id):
    cursor=conn.cursor()

    cursor.execute('''
        SELECT word,definition FROM flashcards
        WHERE  set_id=%s
''',(set_id,))
    
    rows=cursor.fetchall()
    cards=[(row[0],row[1]) for row in rows] # creating a list of cards (word,definition)

    return cards

# funtion for deleting a flashcard set from the database
def delete_set(conn,set_id):
    cursor=conn.cursor()

    # executing SQL query for deleting a flashcard set
    cursor.execute('''
        DELETE FROM flashcard_sets
        WHERE id= %s
''',(set_id))
    
    conn.commit()
    sets_combobox.set('')
    clear_flashcard_display()
    populate_sets_combobox()

    # clearing the current_cards list and resetting card_index
    global current_cards,card_index
    current_cards=[]
    card_index=0

# function for creating a new flashcard set
def create_set():
    set_name=set_name_var.get()
    if set_name:
        if set_name not in get_sets(conn):
            populate_sets_combobox()
            set_name_var.set('')

            # clearing the input fields
            set_name_var.set('')
            word_var.set('')
            definition_var.set('')

def add_word():
    set_name=set_name_var.get()
    word=word_var.get()
    definition=definition_var.get()

    if set_name and word and definition:
        if set_name not in get_sets(conn):
            set_id=add_set(conn,set_name)
        else:
            set_id=get_sets(conn) [set_name]

        add_card(conn,set_id,word,definition)

        word_var.set('')
        definition_var.set('')

        populate_sets_combobox()

def populate_sets_combobox():
    sets_combobox['values']=tuple(get_sets(conn).keys())

# function for deleting a selected flashcard set
def delete_selected_set():
    set_name=sets_combobox.get()

    if set_name:
        result=messagebox.askyesno(
            'Confirmation', f'Are you sure you want to delete the "{set_name}" set?'
        )

        if result == tk.YES:
            set_id=get_sets(conn)[set_name]
            delete_set(conn,set_id)
            populate_sets_combobox()
            clear_flashcard_display()

def select_set():
    set_name=sets_combobox.get()

    if set_name:
        set_id=get_sets(conn)[set_name]
        cards=get_cards(conn,set_id)

        if cards:
            display_flashcards(cards)
        else:
            word_label.config(text="No cards in this set")
            definition_label.config(text='')

    else:
        # clearing the current cards list and resetting card index
        global current_cards,card_index
        current_cards=[]
        card_index=0
        clear_flashcard_display()

def display_flashcards(cards):
        global card_index
        global current_cards

        card_index=0
        current_cards=cards

        # clearing the display
        if not cards:
            clear_flashcard_display()
        else:
            show_card()

        show_card()
        # which showcard to remove??
    
def clear_flashcard_display():
    word_label.config(text='')
    definition_label.config(text='')

# function to display the current cards word
def show_card():
    global card_index
    global current_cards

    if current_cards:
        if 0<= card_index< len(current_cards):
            word,_=current_cards[card_index]
            word_label.config(text=word)
        else:
            clear_flashcard_display()
    else:
        clear_flashcard_display()

# function for flipping the current card and displaying its definition
def flip_card():
    global card_index
    global current_cards

    if current_cards:
        _,definition=current_cards[card_index]
        definition_label.config(text=definition)

# function for moving to the next card
def next_card():
    global card_index
    global current_cards

    if current_cards:
        card_index=min(card_index+1,len(current_cards)-1)
        show_card()

# function for moving to the previous card     
def prev_card():
    global card_index
    global current_cards

    if current_cards:
        card_index=max(card_index-1,0)
        show_card()   

if __name__=='__main__':
    # connecting to the database and creating tables
    conn=mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="flashcards"
    )
    create_tables(conn)

    # creating the main GUI window
    root=tk.Tk()
    root.title('Flashcards App')
    root.geometry('500x400')

    # applying styles to GUI elements
    style=Style(theme='superhero')
    style.configure('TLabel',font=('TkDefaultFont',18))
    style.configure('TButton',font=('TkDefaultFont',16))

    # setting up variables for collecting user input
    set_name_var=tk.StringVar()
    word_var=tk.StringVar()
    definition_var=tk.StringVar()

    # creating a notebook widget to manage tasks
    notebook=ttk.Notebook(root)
    notebook.pack(fill='both',expand=True)

    # creating the 'Create Set' tab and its content
    create_set_frame=ttk.Frame(notebook)
    notebook.add(create_set_frame,text='Create Set')

    # Label and Entry widgets for entering set name,word and definition
    ttk.Label(create_set_frame,text='Set Name:').pack(padx=5,pady=5)
    ttk.Entry(create_set_frame,textvariable=set_name_var,width=30).pack(padx=5,pady=5)

    ttk.Label(create_set_frame,text='Word:').pack(padx=5,pady=5)
    ttk.Entry(create_set_frame,textvariable=word_var,width=30).pack(padx=5,pady=5)

    ttk.Label(create_set_frame,text='Definition:').pack(padx=5,pady=5)
    ttk.Entry(create_set_frame,textvariable=definition_var,width=30).pack(padx=5,pady=5)

    # button for adding word to the set
    ttk.Button(create_set_frame,text='Add Word',command=add_word).pack(padx=5,pady=10)

    # button for saving the set
    ttk.Button(create_set_frame,text='Save Set',command=create_set).pack(padx=5,pady=10)

    # creating the 'Select Set' tab and its content
    select_set_frame=ttk.Frame(notebook)
    notebook.add(select_set_frame,text='Select Set')

    # combobox widget for choosing existing sets
    sets_combobox=ttk.Combobox(select_set_frame,state='readonly')
    sets_combobox.pack(padx=5,pady=40)

    # button for selecting
    ttk.Button(select_set_frame,text='Select Set',command=select_set).pack(padx=5,pady=5)

    # button for deleting a set
    ttk.Button(select_set_frame,text='Delete Set',command=delete_selected_set).pack(padx=5,pady=5)

    # creating the 'Learn Mode' tab and its content
    flashcards_frame=ttk.Frame(notebook)
    notebook.add(flashcards_frame,text='Learn Mode')

    # initializing variables for tracking card index and current cards
    card_index=0
    current_cards=[]

    # labeling to display words on flashcards
    word_label=ttk.Label(flashcards_frame,text='',font=('TkDefaultFont',24))
    word_label.pack(padx=5,pady=40)

    # labeling to display definitions on flashcards
    definition_label=ttk.Label(flashcards_frame,text='')
    definition_label.pack(padx=5,pady=5)   

    # button for flipping the card
    ttk.Button(flashcards_frame,text='Flip',command=flip_card).pack(side='left',padx=5,pady=5)

    # button for viewing the next card
    ttk.Button(flashcards_frame,text='Next',command=next_card).pack(side='right',padx=5,pady=5)

    # button for viewing the previous card
    ttk.Button(flashcards_frame,text='Previous',command=prev_card).pack(side='right',padx=5,pady=5)

    populate_sets_combobox()

    root.mainloop()