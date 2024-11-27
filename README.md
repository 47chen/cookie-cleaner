# Browser Cookie Cleaner

A cross-platform desktop application for managing browser cookies.

## Features

- Clean cookies from multiple browsers (Chrome, Firefox)
- View detailed cookie information
- Verify cleaning success
- Cross-platform support (Windows, macOS, Linux)
- User-friendly interface

## Requirements

- Python 3.8+
- PyQt6
- psutil

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/browser-cookie-cleaner.git
cd browser-cookie-cleaner
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python main.py
```

## Development

### Project Structure

```
browser-cookie-cleaner/
├── src/                    # Source code
│   ├── gui/               # GUI components
│   ├── browsers/          # Browser implementations
│   └── utils/             # Utility functions(Helper tools)
├── logs/                  # Log files
├── main.py               # Entry point
└── requirements.txt      # Dependencies
```

### Running Tests

```bash
pytest
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request