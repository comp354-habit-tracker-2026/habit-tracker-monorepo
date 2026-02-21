# Group 04 – MyWhoosh Integration

### Description:
This module handles integration with MyWhoosh API.

---

### Tech Stack
- Django
- pytest
- pytest-django

---

### Project Structure
- mywhoosh_service/ – Django project configuration
- mywhoosh_integration/ – Django app for MyWhoosh logic
- pytest.ini – pytest configuration
- requirements.txt – project dependencies

---

### Setup Instructions

#### 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

#### 2. Install dependencies
pip install -r requirements.txt

#### 3. Run the Server
python manage.py runserver

#### 4. Go to health check endpoint
http://127.0.0.1:8000/health/

#### 5. When ready: Run tests
pytest