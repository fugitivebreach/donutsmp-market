print("HELLO FROM PYTHON!")
print("This is a basic test")
import sys
print("Python version:", sys.version)
print("Python executable:", sys.executable)
print("Current working directory:", __import__('os').getcwd())
print("Files in current directory:", __import__('os').listdir('.'))
print("TEST COMPLETE - Python is working!")
