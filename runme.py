import os
import sys

# Adjust the module path so relative imports work correctly after packaging
if getattr(sys, 'frozen', False):
    # If running as a PyInstaller bundled app
    base_path = sys._MEIPASS  # Temporary folder used by PyInstaller
else:
    # If running in development
    base_path = os.path.dirname(os.path.abspath(__file__))


sys.path.insert(0, os.path.join(base_path, "overwatch_time"))

# Import and run your main script
from overwatch_time.main import main  # Assuming your main script has a function called main

if __name__ == "__main__":
    main()  # Run the main function or entry point of your application
