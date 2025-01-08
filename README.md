# Chat Message Management System

## Project Description
A Python-based web application for managing and storing chat messages across multiple GitHub repositories.

## Key Features
- Local message database
- Multi-repository message synchronization
- Simple HTTP server interface
- GitHub repository integration

## Quick Start

### Prerequisites
- Python 3.8+
- GitHub Personal Access Token

### Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure `.env` file with GitHub credentials

### Running the Server
```bash
python -m server.app
```

## Full Project Specification
See `PROJECT_SPEC.md` for detailed project requirements and design considerations.

## Contributing
Please read the project specification and follow the guidelines for contributions.

## Tech Stack

- Backend:
  - Python (Standard Library)
  - SQLite3 for local database
  - GitHub API for Git operations
- Frontend:
  - Pure HTML5
  - CSS3
  - Vanilla JavaScript
- Version Control:
  - Git
  - GitHub API

## Prerequisites

- Python 3.8 or higher
- Git installed locally
- GitHub account
- SQLite3
- Modern web browser
- GitHub Personal Access Token (for API access)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/chat4IAP.git
cd chat4IAP
```

2. Install the required Python packages:
```bash
pip install python-dotenv PyGithub
```

3. Set up your GitHub Personal Access Token:
   - Go to GitHub Settings → Developer Settings → Personal Access Tokens
   - Generate a new token with `repo` scope
   - Save the token securely

4. Configure your environment:

The project includes a setup utility to manage your environment variables. Here's how to use it:

```bash
# Create initial .env file (if it doesn't exist)
python3 setup.py list

# View current environment variables
python3 setup.py view

# Set a specific variable (interactive mode)
python3 setup.py set --var GITHUB_TOKEN

# Set a specific variable (direct mode)
python3 setup.py set --var GITHUB_TOKEN --value your_token_here

# List all available variables with descriptions
python3 setup.py list
```

Common environment setup tasks:

```bash
# Set up GitHub credentials
python3 setup.py set --var GITHUB_TOKEN
python3 setup.py set --var GITHUB_USERNAME

# Configure primary repository
python3 setup.py set --var PRIMARY_REPO_OWNER
python3 setup.py set --var PRIMARY_REPO_NAME

# Configure secondary repository (optional)
python3 setup.py set --var SECONDARY_REPO_OWNER
python3 setup.py set --var SECONDARY_REPO_NAME
```

5. Create your environment file:
```bash
cp .env.template .env
```

6. Edit the `.env` file with your settings:
```env
# GitHub Configuration
GITHUB_TOKEN=your_github_personal_access_token_here
GITHUB_USERNAME=your_github_username

# Repository Configuration
PRIMARY_REPO_OWNER=owner_of_primary_repo
PRIMARY_REPO_NAME=primary_repo_name
PRIMARY_REPO_BRANCH=main
PRIMARY_REPO_PATH=messages

# Optional Secondary Repository
SECONDARY_REPO_OWNER=owner_of_secondary_repo
SECONDARY_REPO_NAME=secondary_repo_name
SECONDARY_REPO_BRANCH=main
SECONDARY_REPO_PATH=messages

# Server Configuration
PORT=8080
```

## Repository Setup

1. Create a new repository on GitHub for storing messages
2. Make sure you have write access to the repository
3. The repository should have a `messages` directory (or whatever you specified in `PRIMARY_REPO_PATH`)
4. If using multiple repositories, repeat the above steps for each repository

## Project Structure

```
chat4IAP/
├── server/
│   ├── app.py              # Main application server
│   ├── database.py         # SQLite database operations
│   └── repository_manager.py # Multi-repository manager
├── static/
│   └── index.html          # Main application page
├── .env                    # Environment variables (git-ignored)
├── .env.template           # Environment template
├── .gitignore             # Git ignore file
├── schema.sql             # Database schema
└── README.md              # This file
```

## Development Setup

1. Initialize the SQLite database:
```bash
python3 -c "from server.database import Database; db = Database()"
```

2. Start the development server:
```bash
python3 -m server.app
```

3. Access the application:
```
http://localhost:8080
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_TOKEN` | Your GitHub Personal Access Token | Yes |
| `GITHUB_USERNAME` | Your GitHub username | Yes |
| `PRIMARY_REPO_OWNER` | Owner of the primary repository | Yes |
| `PRIMARY_REPO_NAME` | Name of the primary repository | Yes |
| `PRIMARY_REPO_BRANCH` | Branch to use (default: main) | No |
| `PRIMARY_REPO_PATH` | Path for messages (default: messages) | No |
| `SECONDARY_REPO_*` | Same as above for secondary repo | No |
| `PORT` | Server port (default: 8080) | No |

## Security Notes

1. Never commit your `.env` file to version control
2. Keep your GitHub token secure and rotate it regularly
3. Use environment-specific `.env` files for different deployments
4. Consider using GitHub's fine-grained tokens for better security

## Troubleshooting

1. **Messages not appearing:**
   - Check your GitHub token permissions
   - Verify repository access
   - Check the server logs for errors

2. **Can't connect to GitHub:**
   - Verify your internet connection
   - Check if GitHub is accessible
   - Verify your token is valid

3. **Database errors:**
   - Ensure SQLite is installed
   - Check file permissions
   - Verify schema.sql exists

## License

This project is licensed under the MIT License - see the LICENSE file for details.
