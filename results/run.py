import subprocess
import sys


def run_scripts() :
    try :
        # Use the same Python interpreter for both scripts
        python_executable = sys.executable

        # Run create.py
        print("Running create.py...")
        result = subprocess.run([python_executable, 'create.py'], check=True)
        print("create.py finished successfully.")

        # Run analysis.py
        print("Running analysis.py...")
        result = subprocess.run([python_executable, 'analysis.py'], check=True)
        print("analysis.py finished successfully.")

    except subprocess.CalledProcessError as e :
        print(f"An error occurred while running the scripts: {e}")


if __name__ == "__main__" :
    run_scripts()
