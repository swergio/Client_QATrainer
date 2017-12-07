"""
This script runs the QAGenerator Client on an infinit loop.
""" 

from QATrainer import QATrainer

def start():
    print('QAGenerator is starting')   
    client = QATrainer()
    client.ListenToSocketIO()
    

if __name__ == '__main__':
    start()