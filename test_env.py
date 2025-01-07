from dotenv import load_dotenv
import os

load_dotenv()

# Check if variables exist (without printing their values)
required_vars = ['GITHUB_TOKEN', 'GITHUB_USERNAME', 'REPOSITORY_NAME']
for var in required_vars:
    if var in os.environ:
        print(f"{var} is set")
    else:
        print(f"{var} is NOT set")
