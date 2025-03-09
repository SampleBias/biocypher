# bi0cyph3r - DNA Cryptography System

A sophisticated yet minimal Flask web application that allows users to encode and decode messages using DNA cryptography.

## Features

- Secure user authentication system
- Dedicated pages for encoding messages and decoding DNA sequences
- Clean, intuitive, futuristic user interface
- Real-time validation and error handling
- Advanced DNA cryptography algorithms
- Contact page for requesting access

## How It Works

bi0cyph3r uses the four nucleotide bases (A, T, C, G) to represent binary data:
- A = 00
- T = 01
- C = 10
- G = 11

The application converts text to ASCII, then to binary, and finally maps the binary values to DNA bases.

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python app.py
   ```
4. Open your browser and navigate to `http://127.0.0.1:5000/`
5. Login with the demo credentials:
   - Username: `demo`
   - Password: `password123`

## Application Structure

- **Login Page**: Secure authentication system
- **Dashboard**: Central navigation hub
- **Encode Page**: Convert text messages to DNA sequences
- **Decode Page**: Translate DNA sequences back to text
- **Contact Page**: Request access or get support

## Example

- Input: "HELLO WORLD"
- Encoded DNA Sequence: "ACTACAAGTAGTATGCGGCCGATGCACAGTAAT"

## Security Notice

This application is for demonstration purposes only. In a production environment, you would want to implement proper user authentication, database storage, and additional security measures.

## Setting Up a Virtual Environment

It's recommended to use a virtual environment for this project:

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```
   - On Windows:
     ```
     venv\Scripts\activate
     ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python app.py
   ``` 