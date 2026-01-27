import pyttsx3

if __name__ == '__main__':
    print("welcome to Robo Speaker 1.1 Created by Talib Iconic... ")
    x = input("Enter What you want to speak: ")
    command = (f"say {x}")
    pyttsx3.system(command)
    