# class bankAccount: 
#     def __init__(self, acc_number, name, balance = 500):
#         self.acc_number = acc_number
#         self.name = name 
#         self.balance = balance
#         self.is_active = True

# acc = bankAccount
# acc.acc_open()
# import random
# class Bank_Account:
#     def __init__(self):
#         self.active = True 

#     def acc_open():
#         name = input("Enter Account holder name : ")
#         print(f"Hi {name} welcome to may finance service !!! ")

#         acc_type = input("Enter Acc Type Saving or Current ? ")
#         if acc_type == "saving":
#             type = "Saving"
#         else:
#             type = "Current"
#         print("Account Type", type) 

#         acc_number = random.randint(100000000000, 120000000000)
#         print(f"New Account Number : {acc_number}")   

    # def close_acc(self):
    #     if not self.active : 
    #         print("Account not Active ")
    #     else:
    #         self.active = False
    #         print(f"Account is Already close for {__name__}")

#     def deposit(self, amount):
#         if not self.active :
#             a = amount
#             print(a)
#             print("Account is not active can'not deposit")


# acc = Bank_Account
# acc.acc_open()
# acc.close_acc()
# acc.deposit()


# from ast import Name
import random
class bank_Account:
    def __init__(self, Name, Account_no, balance = 0):
        self.Name = Name
        self.Account_No = Account_no
        self.balance = balance
        self.is_active = True

    def user_data():
        Name = input("Enter Your Name: ")
        print(f"Hi welcome {Name}")
        Account_no = random.randint(1000, 4000)
        print(f"Account Number is {Account_no}")


class close_accoont:
    def close(self):
        if not self.is_active:
            print("Account is not Active. ")
        else:
            self.is_active = False
            print(f"Account is Already Close for {self.Name}")



class Account_type (bank_Account):
    @user_data
    def saving_account(self):
        def deposit(self, amount):
            if not self.is_active:
                print("Cannot deposit. Account is closed.")
                return
            if amount > 0:
                self.balance += amount
                print(f"Deposited ₹{amount}. New balance: ₹{self.balance}")
            else:
                print("Invalid deposit amount.")

        def withdraw(self, amount):
            if not self.is_active :
                print("cannot withdraw account is closed. ")
                return
            if amount < 0 :
                print("Please Maintain minimum Amount in your Account...")
            elif amount > 0 - self.balance:
                self.balance = amount
                print(f"Withdraw{amount} current Balance is {self.balance}")

    def current_account(self, amount):
        def deposit(self, amount):
            if not self.is_active:
                print("Cannot deposit. Account is closed.")
                return
            if amount > 0:
                self.balance += amount
                print(f"Deposited ₹{amount}. New balance: ₹{self.balance}")
            else:
                print("Invalid deposit amount.")

        def withdraw(self, amount):
            if not self.is_active :
                print("cannot withdraw account is closed. ")
                return
            if amount <= 5000 :
                print("Please Maintain minimum Amount in your Account...")
            elif amount > 5000 - self.balance:
                self.balance = amount
                print(f"Withdraw{amount} current Balance is {self.balance}")

def manu():
    account = 0
    while (account< 10):
        print(account)
        account +=1

    while True:
        print("\n========Bank Manu========")
        print("1. create Bank Account ")
        print("2 Deposit ")
        print("3 current Account ")
        print("4. deposit Amount. ")
        print("5. Withdraw Amount.")
        print("6. Show Balance. ")
        print("7 for Exit. ")
        choice = int(input("Enter your choice : "))

        if choice == "1":
            if account is 0:
                Account_no = int(input("Enter your Account Number : "))
                Name = input("Enter Your name : ")
                account = bank_Account(Account_no, Name)
                account.user_data()
            else:
                print("Account Already Exist ! ")
        elif choice == "2":

            
        


        


    


