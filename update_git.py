import os
from time import sleep

path = os.path.dirname(os.path.realpath(__file__))
sleep(5)
os.system("git pull")
sleep(5)
os.system(f"python3 {os.path.join(path, 'main.py')}")