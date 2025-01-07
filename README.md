# Git-Backed Messaging Application

A lightweight, Git-backed messaging application that allows users to communicate through a web interface while storing messages in a Git repository. This application combines the simplicity of a chat system with the version control capabilities of Git.

## Features

- Message persistence using Git repository
- SQLite database for efficient message querying
- GitHub API integration for repository management
- Real-time message updates
- Simple and clean web interface
- No framework dependencies
- Message history with Git versioning
- Lightweight and easy to deploy

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
pip install requests PyGithub
```

3. Set up your GitHub Personal Access Token:
   - Go to GitHub Settings → Developer Settings → Personal Access Tokens
   - Generate a new token with `repo` scope
   - Save the token securely

4. Create a `.env` file in the project root:
```
GITHUB_TOKEN=your_personal_access_token
GITHUB_USERNAME=your_github_username
REPOSITORY_NAME=chat4IAP
```

## Project Structure

```
chat4IAP/
├── server/
│   ├── app.py           # Main application server
│   ├── database.py      # SQLite database operations
│   ├── git_manager.py   # Git operations handler
│   └── github_api.py    # GitHub API integration
├── static/
│   ├── css/
│   │   └── style.css    # Application styles
│   └── js/
│       └── main.js      # Frontend JavaScript
├── templates/
│   └── index.html       # Main application page
├── .env                 # Environment variables (git-ignored)
├── .gitignore          # Git ignore file
├── schema.sql          # Database schema
└── README.md           # This file
```

## Development Setup

1. Initialize the SQLite database:
```bash
python server/database.py
```

2. Start the development server:
```bash
python server/app.py
```

3. Access the application:
```
http://localhost:8080
```

## How It Works

1. Messages are stored locally in SQLite for quick access and querying
2. Periodically, messages are committed to the Git repository
3. Git commits are pushed to GitHub for persistence
4. The frontend polls for new messages and updates in real-time
5. All operations are performed without any heavy frameworks

## Security Considerations

- Store your GitHub token securely
- Never commit the `.env` file
- Use HTTPS for GitHub API communications
- Implement proper input sanitization
- Follow secure coding practices

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add YourFeature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Last Updated

2025-01-07

## Support

For issues and feature requests, please use the GitHub Issues section of this repository.
