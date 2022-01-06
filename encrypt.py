import cryptocode
import sqlite3
import hashlib
import os
from time import sleep
def enc(string,key1,key2):
    return cryptocode.encrypt(cryptocode.encrypt(string,key1),key2)
def dec(string,key1, key2):
    return cryptocode.decrypt(cryptocode.decrypt(string,key2),key1)
def dec_arr(arr,key1,key2):
    new_arr = []
    for item in arr:
        new_arr.append(cryptocode.decrypt(cryptocode.decrypt(item,key2),key1))
    return new_arr
#return list of files in parent directory which has a '.db' extension
def find_db():
    databases = []
    for item in os.listdir():
        if item.endswith('.db'):
            databases.append(item[:item.find('.')])
    return databases
#show all notes from database to user
def show_services(name,login,password):
    con = sqlite3.connect(name+".db")
    cursor = con.cursor()
    with con:
        cursor.execute("SELECT * FROM PASSWORDS")
        data = cursor.fetchall()
        counter = 0
        for item in data:
            x = dec_arr(item, login, password)
            print(x)
            counter+=1
#next 3 methods just operations on notes
def append_note(name,login,password):
    con = sqlite3.connect(name+".db")
    with con:
        service = input("\tEnter name of service:\t")
        url = input("Enter url (optionaly):\t")
        log_in = input("Enter login:\t")
        pass_word = input("Enter password:\t")
        addition = input("Enter some addition:\t")
        sql = 'INSERT INTO PASSWORDS (service, url, login, password, addition) values (?,?,?,?,?)'
        data = [(enc(service,login,password), enc(url,login,password), enc(log_in, login, password), enc(pass_word, login, password), enc(addition, login, password))]
        con.executemany(sql,data)
        print("Запись успешно добавлена")
def rewrite_note(name,login,password):
    pass
def delete_note(name,login,password):
    pass
#name of methods speak about itself
def choose_actions(name,login,password):
    while(True):
        print("Choose actions:\n\t1. Show services\n\t2. Append note\n\t3. Rewrite note\n\t4. Delete note\n\t\tAnother Char -> Exit")
        match input():
            case "1":
                show_services(name,login,password)
            case "2":
                append_note(name,login,password)
            case "3":
                rewrite_note(name,login,password)
            case "4":
                delete_note(name,login,password)
            case _:
                exit()
#This method enters the database by checking login and password hashes
def enter_db(name, login, password):
    print("\tPlease waiting...",end='')
    con = sqlite3.connect(name+".db")
    with con:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM USER")
        data = cursor.fetchone()
        log_in =  hashlib.pbkdf2_hmac('sha256',login.encode('utf-8'),data[2],5000000)  
        pass_word =  hashlib.pbkdf2_hmac('sha256',password.encode('utf-8'),data[2],5000000) 
        if (log_in == data[0] and pass_word == data[1]):
            print(("\b"*17)+"Access Allowed       ")
            return True
        else:
            print(("\b"*17)+"Access Denied         ")
            return False
#Database creation and password and login hashing
def create_db(name, login, password):
    con = sqlite3.connect(name+".db")
    salt = os.urandom(32)
    log_in = hashlib.pbkdf2_hmac('sha256', login.encode('utf-8'), salt, 5000000)
    pass_word = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 5000000)
    with con:
        con.execute("""
            CREATE TABLE USER (
                login BLOB,
                password BLOB,
                salt BLOB
                );
            """)
        sql = 'INSERT INTO USER (login, password, salt) values (?,?,?)'
        data = [(log_in, pass_word, salt)]
        con.executemany(sql,data)
        con.execute("""
            CREATE TABLE PASSWORDS (
                service TEXT,
                url TEXT,
                login TEXT,
                password TEXT,
                addition TEXT
                );
                """)
        print("База данных создана, пользователь создан!")
    return True

if __name__ == "__main__": 
    print('Choose what to do next:\n\t1. Enter Database\n\t2. Create Database\n\t')
    match input():
        case "1":
            print("Choose database")
            dbs = find_db()
            counter = 1
            for item in dbs:
                print("\t"+str(counter)+" "+item)
                counter += 1
            choose = input() 
            print('Enter Login:')
            login = input()
            print('Enter Password:')
            password = input()
            if(enter_db(dbs[int(choose)-1],login,password)):
                choose_actions(dbs[int(choose)-1],login,password)
            else:
                exit()
            pass
        case "2":
            print('Choose database name:')
            name = input()
            print('Enter Login:')
            login = input()
            print('Enter Password:')
            password = input()
            if(create_db(name, login, password)):
                if(enter_db(name, login, password)):
                    choose_actions(name,login,password)
                else:
                    exit()
            pass
