import os
import threading
import time

def create_test_file(file_path, content):
    with open(file_path, 'w') as f:
        f.write(content)
    print(f"Created test file: {file_path}")

def create_virus_file_1():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "Raw Folder")
    os.makedirs(desktop_path, exist_ok=True)
    file_path = os.path.join(desktop_path, "virus_file_1.txt")
    # EICAR test string
    content = "X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
    create_test_file(file_path, content)

def create_virus_file_2():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "Raw Folder")
    os.makedirs(desktop_path, exist_ok=True)
    file_path = os.path.join(desktop_path, "virus_file_2.txt")
    # EICAR test string
    content = "X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
    create_test_file(file_path, content)

def create_virus_file_3():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "Raw Folder")
    os.makedirs(desktop_path, exist_ok=True)
    file_path = os.path.join(desktop_path, "virus_file_3.txt")
    # EICAR test string
    content = "X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
    create_test_file(file_path, content)

if __name__ == "__main__":
    # Create threads for each test file
    thread1 = threading.Thread(target=create_virus_file_1)
    thread2 = threading.Thread(target=create_virus_file_2)
    thread3 = threading.Thread(target=create_virus_file_3)

    # Start the threads
    thread1.start()
    thread2.start()
    thread3.start()

    # Wait for all threads to complete
    thread1.join()
    thread2.join()
    thread3.join()

    print("All test files created.")