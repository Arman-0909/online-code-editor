# CodeRunner: A Modern Online Code Editor

CodeRunner is a web-based Integrated Development Environment (IDE) that allows users to write and execute code in various programming languages directly from their browser. The application features a clean, modern frontend powered by the same editor as VS Code (Monaco) and a robust Django backend for secure code execution.

This project is designed as a foundational boilerplate for building more complex online coding platforms, educational tools, or interview platforms.

![CodeRunner Screenshot](https://i.imgur.com/your-screenshot-url.png)
*(Note: You can take a screenshot of your running application and upload it to a service like Imgur to replace the link above.)*

## Features

- **Real-time Code Editing:** A responsive, feature-rich editor with syntax highlighting, autocompletion, and theming, powered by Monaco Editor.
- **Multi-Language Support:** Out-of-the-box support for both backend and frontend languages:
    - **Backend Execution:** C, C++, Java, Python, PHP, JavaScript (Node.js)
    - **Frontend Rendering:** HTML, CSS, JavaScript (rendered live in an iframe)
- **Separated I/O:** Clear panels for providing standard input (stdin) and viewing standard output (stdout) or error messages.
- **Secure Backend API:** A Django REST Framework API handles code execution requests.
- **Safe Execution (within limits):** Implements timeouts to prevent infinite loops and uses temporary, isolated directories for each execution.

## Tech Stack

- **Frontend:**
    - HTML5
    - CSS3
    - Vanilla JavaScript
    - **Monaco Editor:** The core engine of VS Code, providing a professional editing experience.

- **Backend:**
    - **Python 3.8+**
    - **Django:** A high-level Python web framework for rapid development.
    - **Django REST Framework (DRF):** A powerful toolkit for building Web APIs.

- **Execution Runtimes/Compilers:**
    - GCC (for C), G++ (for C++)
    - OpenJDK (for Java)
    - Python
    - PHP CLI
    - Node.js

## Prerequisites

Before you begin, ensure you have the following installed on your system:

1.  **Python 3.8+** and **pip**.
2.  **Git** (for cloning the repository).
3.  **Compilers and Runtimes:**
    - **For C/C++:**
        - On Linux (Ubuntu/Debian): `sudo apt-get install build-essential`
        - On Windows: Install [MinGW-w64](https://www.mingw-w64.org/) and ensure `gcc` and `g++` are in your system's PATH.
    - **For Java:**
        - On Linux: `sudo apt-get install default-jdk`
        - On Windows: Install the Java Development Kit (JDK) from Oracle or use an open-source alternative like Adoptium.
    - **For PHP:**
        - On Linux: `sudo apt-get install php-cli`
        - On Windows: Download and install from the official [PHP for Windows](https://www.php.net/downloads.php) page.
    - **For Node.js:**
        - On Linux: `sudo apt-get install nodejs`
        - On Windows: Download and install from the [Node.js website](https://nodejs.org/).

## Installation & Setup

Follow these steps to get your local development environment running.

**1. Clone the Repository**
```bash
git clone https://github.com/your-username/code_editor_project.git
cd code_editor_project
```

**2. Create a `requirements.txt` File**
This file lists the Python dependencies. Create a file named `requirements.txt` in the root of the project with the following content:
```
django
djangorestframework
```

**3. Install Python Dependencies**
It is highly recommended to use a virtual environment.
```bash
# Create a virtual environment (optional but recommended)
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install the dependencies
pip install -r requirements.txt
```

**4. Apply Database Migrations**
This will set up the necessary database tables for Django.
```bash
python manage.py migrate
```

**5. Run the Development Server**
```bash
python manage.py runserver
```

**6. Open the Application**
Navigate to `http://127.0.0.1:8000/` in your web browser. You should now see the code editor interface.

---

## API Documentation

The backend exposes a single API endpoint for code execution.

### Execute Code

- **URL:** `/api/execute/`
- **Method:** `POST`
- **Description:** Receives code, language, and optional input, then executes it and returns the output.
- **Headers:**
    - `Content-Type: application/json`
    - `X-CSRFToken`: (Handled automatically by the frontend JavaScript)

- **Request Body (JSON):**
```json
{
  "code": "print(f'Hello, {input()}!')",
  "language": "python",
  "input": "World"
}```

- **Success Response (200 OK):**
```json
{
  "output": "Hello, World!\n",
  "error": ""
}
```

- **Compilation Error Response (200 OK):**
```json
{
  "output": "",
  "error": "main.cpp: In function 'int main()':\nmain.cpp:4:5: error: 'cout' is not a member of 'std'\n    std::cout << \"Hello, C++!\";\n    ^~~~\n..."
}
```

- **Bad Request Response (400 Bad Request):**
```json
{
  "error": "Code or language not provided."
}
```

---

## 🚨 Security Considerations

**This project is intended for educational and development purposes. Running it in a public production environment without further security measures is extremely dangerous.**

Executing arbitrary code from users is a major security risk. Here are the measures taken in this project and what is **required** for a production deployment:

#### Implemented Safety Measures
1.  **Execution Timeouts:** The `subprocess.run` command is configured with a `timeout` of 10 seconds. This prevents code with infinite loops from hogging server resources indefinitely.
2.  **Temporary Directories:** Each code execution happens within a unique, temporary directory that is deleted immediately after the run. This prevents one script from accessing files created by another.

#### CRITICAL Production Requirements
The current setup **DOES NOT** provide true sandboxing. A malicious script could still potentially access the filesystem or network of the host machine.

For a real-world, public-facing application, you **MUST** containerize the execution environment. This is non-negotiable.
- **Docker:** The industry standard for containerization. Each code execution should be run inside a new, short-lived Docker container with strict resource limits (CPU, memory) and no network access unless explicitly required.
- **Micro-VMs:** Technologies like **gVisor** or **Firecracker** provide even stronger kernel-level isolation and are used by major cloud providers for running untrusted code.

## Project Structure
```
code_editor_project/
├── code_editor_project/    # Django project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py         # Project settings
│   ├── urls.py             # Project-level URL routing
│   └── wsgi.py
├── editor/                 # The main Django app
│   ├── static/             # Frontend assets
│   │   ├── css/style.css
│   │   └── js/script.js
│   ├── templates/          # HTML templates
│   │   └── editor/index.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── execution_engine.py # CORE LOGIC for running code
│   ├── models.py
│   ├── tests.py
│   ├── urls.py             # App-level URL routing
│   └── views.py            # API and template views
├── manage.py               # Django's command-line utility
└── README.md
```

## Future Improvements

- [ ] **Full Dockerization:** Implement code execution inside isolated Docker containers.
- [ ] **User Accounts:** Allow users to register, log in, and save their code snippets.
- [ ] **More Languages:** Extend the `execution_engine.py` to support languages like Go, Rust, or Swift.
- [ ] **UI/UX Enhancements:** Add themes, font size controls, and a more responsive layout.
- [ ] **Project/File System:** Allow users to create and manage multiple files instead of a single snippet.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
