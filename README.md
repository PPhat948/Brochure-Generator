# AI Brochure Generator 🚀

## Overview

The AI Brochure Generator is a Python application that automatically creates company brochures by scraping content from a company's landing page and using a Generative AI model (Google's Gemini via an OpenAI-compatible API) to synthesize the information. The application provides a user-friendly web interface built with Gradio, allowing users to input a company name, its landing page URL, and select the desired language (English or Thai) for the brochure.

## Features

-   **Web Scraping:** Fetches and parses content from the provided company landing page URL.
-   **AI-Powered Content Generation:** Utilizes Google's Gemini model to analyze website content and generate an engaging brochure.
-   **Multi-language Support:** Can generate brochures in English or Thai.
-   **Streaming Output:** The generated brochure is streamed to the user interface for a responsive experience.
-   **User-Friendly Interface:** Built with Gradio for easy interaction.

## Project Structure


.
├── brochure_generator.py   # Main Python script for the application
├── .env                    # File to store environment variables (e.g., API key) - (You need to create this)
└── README.md               # This file


## Prerequisites

Before you begin, ensure you have met the following requirements:

-   Python 3.7 or higher installed.
-   Access to Google's Generative AI (Gemini) and an API key.
-   `pip` (Python package installer).

## Setup and Installation

1.  **Clone the repository (if applicable, otherwise download the files):**
    ```bash
    # If you have a git repository
    # git clone <your-repository-url>
    # cd <your-repository-name>
    ```

2.  **Create a Python virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```
    Activate the virtual environment:
    * On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    * On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```

3.  **Install the required Python libraries:**
    ```bash
    pip install requests beautifulsoup4 python-dotenv openai gradio
    ```

4.  **Create a `.env` file:**
    In the root directory of the project, create a file named `.env` and add your Google API key:
    ```env
    GOOGLE_API_KEY=your_actual_google_api_key_here
    ```
    Replace `your_actual_google_api_key_here` with your valid API key.

## Running the Application

1.  **Ensure your virtual environment is activated.**
2.  **Navigate to the project directory in your terminal.**
3.  **Run the Python script:**
    ```bash
    python brochure_generator.py
    ```
4.  The script will output `Launching Gradio App...` and should automatically open the web interface in your default browser. If not, open your browser and go to the local URL provided in the terminal (usually `http://127.0.0.1:7860` or similar).

## How to Use

1.  Open the web interface in your browser.
2.  Enter the **Company Name** in the designated field.
3.  Enter the full **Landing Page URL** (including `http://` or `https://`).
4.  Select the desired **Language Version** (English or Thai) from the dropdown.
5.  Click the "Generate Brochure" button.
6.  The AI-generated brochure will appear in the "Generated Brochure" section in Markdown format.

## Demo
