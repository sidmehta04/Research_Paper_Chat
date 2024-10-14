# Research Paper Downloader, Summarizer, and Chat

This application allows users to download research papers from Hugging Face, generate summaries using AI, and engage in a Q&A session about the papers. It combines web scraping, PDF processing, and natural language processing to provide a comprehensive tool for researchers and students.

## Features

- Download research papers from Hugging Face for a specific date
- Process and summarize PDF papers using AI
- Interactive Q&A system for downloaded papers
- User-friendly web interface

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.7+
- pip (Python package manager)
- Google Chrome browser (for web scraping)
- ChromeDriver (compatible with your Chrome version)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/sidmehta04/Research_Paper_Chat.git
   cd research-paper-tool
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Configuration

1. Create a `.env` file in the project root directory and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

2. Ensure ChromeDriver is in your system PATH or specify its location in the `setup_driver` function in `paper_downloader.py`.

## Usage

1. Start the Flask application:
   ```
   python app.py
   ```

2. Open a web browser and navigate to `http://localhost:5000`.

3. Use the interface to:
   - Download papers by selecting a date and specifying the number of papers
   - Select and process downloaded PDFs
   - View AI-generated summaries
   - Ask questions about the papers

## File Structure

- `app.py`: Main Flask application
- `paper_downloader.py`: Contains functions for downloading papers from Hugging Face
- `templates/index.html`: HTML template for the web interface
- `static/style.css`: CSS styles for the web interface
- `static/script.js`: JavaScript for handling user interactions and AJAX requests

## Contributing

Contributions to this project are welcome. Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to the branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Your Name - [@sidmeht04](https://github.com/sidmehta04)

Project Link: [https://github.com/yourusername/research-paper-tool](https://github.com/yourusername/research-paper-tool)