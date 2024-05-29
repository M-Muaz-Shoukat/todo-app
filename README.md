# Todo List Project

This project is a simple Todo List application built with Django. It allows users to manage their tasks and categories.

## Features

- Create, read, update, and delete tasks
- Categorize tasks into different categories
- Mark tasks as completed
- Simple and intuitive user interface

## Usage

To run this project locally, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/M-Muaz-Shoukat/todo-app.git
2. Navigate to the project directory:

   ```bash
   cd todo-list
3. Create a virtual environment (optional but recommended):
   ```
   python3 -m venv venv
4. Activate the virtual environment:
   ```bash
   source venv/bin/activate  # On Linux/Mac
   venv\Scripts\activate  # On Windows
5. Install the dependencies:
   ```bash
   pip install -r requirements.txt
6. Set up environment variables for PostgreSQL:
   Rename the .env.example file to .env in the project root directory and fill the mentioned environment variables.
7. Apply database migrations:
   ```bash
   python manage.py migrate
8. Run the development server:
   ```bash
   python manage.py runserver
9. Open your web browser and navigate to http://127.0.0.1:8000/todo/categories to access the application.




