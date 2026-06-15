# 🩸 Blood Bank Management System

A decoupled, full-stack Blood Bank Management System designed to handle blood donations, inventory tracking, hospital requests, and automated distributions.

This project utilizes a modern architecture with a **FastAPI** backend for high-performance API routing and a **Django** frontend serving as an API client to render a responsive, Bootstrap-powered user interface.

## 🏗️ System Architecture

This project is split into two completely separate services that communicate via HTTP:

1. **Backend (FastAPI):** Acts as the core REST API, managing the SQLite database, handling business logic, and issuing JWT (JSON Web Tokens) for secure authentication.
2. **Frontend (Django):** Acts as the UI layer. It consumes the FastAPI endpoints using the Python `requests` library, stores the JWT securely in user sessions, and renders HTML templates using Bootstrap 5.

## ✨ Features

### 🔐 Authentication & Roles

* **Role-Based Access Control (RBAC):** Distinct roles for `Admin`, `Donor`, and `Hospital`.
* **JWT Security:** Stateless authentication ensuring secure API calls.

### 👨‍⚕️ Admin Features (Blood Bank Staff)

* **Dashboard Analytics:** Visual overview of total donors, hospitals, pending requests, and low stock (powered by Chart.js).
* **Manage Donors:** Add new donors and view their history.
* **Record Donations:** Automatically updates the blood inventory upon logging a new donation.
* **Manage Requests:** Approve or reject blood requests from hospitals. Approving automatically deducts from the inventory and generates a distribution record.
* **Reports:** View expired blood units, low stock alerts, and download system-wide PDF reports.

### 🏥 Hospital Features

* **Account Creation:** Register a hospital account in the system.
* **Request Blood:** Submit formal requests for specific blood groups and unit quantities.
* **Track Requests:** View the real-time status (Pending, Approved, Rejected) of their submitted requests.

## 🛠️ Tech Stack

**Backend:**

* Python 3.x
* FastAPI
* SQLAlchemy (ORM)
* SQLite (Database)
* Passlib / Jose (JWT & Password Hashing)

**Frontend:**

* Django (Templates & Session Management)
* Python `requests` (API Client)
* Bootstrap 5 (CSS Framework)
* Chart.js (Data Visualization)
* ReportLab (PDF Generation)

---

## 🚀 Installation & Setup

Because this is a decoupled application, you will need to run the backend and frontend simultaneously in separate terminal windows.

### Prerequisites

* Python 3.8+ installed
* `pip` installed

### Step 1: Setup the FastAPI Backend

1. Open a terminal and navigate to your backend directory.
2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

```


3. Install the required packages:
```bash
pip install fastapi uvicorn sqlalchemy passlib python-jose[cryptography] python-multipart

```


4. Start the FastAPI server on port 8000:
```bash
uvicorn main:app --reload --port 8000

```


5. The API documentation (Swagger UI) is now available at `http://127.0.0.1:8000/docs`.

### Step 2: Setup the Django Frontend

1. Open a **new** terminal and navigate to your Django project directory (`bloodbank_frontend`).
2. Activate your virtual environment (or create a new one).
3. Install the required packages:
```bash
pip install django requests reportlab

```


4. Apply the initial Django migrations (for session management):
```bash
python manage.py migrate

```


5. Start the Django development server on port 8001 (to avoid conflict with FastAPI):
```bash
python manage.py runserver 8001

```


6. Access the web interface at `http://127.0.0.1:8001/`.

---

## 🚦 Usage Workflow

1. **Create an Admin:** Since the frontend requires an account, go to `http://127.0.0.1:8000/docs`, find the `/register` endpoint, and create an account with the role `"admin"`.
2. **Log In:** Go to `http://127.0.0.1:8001/` and log in with the admin credentials.
3. **Add Data:** Navigate to the "Hospitals" and "Donors" tabs to populate the database.
4. **Record a Donation:** Click "Record Donation" next to a donor to add units to the `BloodInventory`.
5. **Process a Request:** Create a hospital account, submit a blood request, log back in as an admin, and approve it to see the inventory automatically decrease!

## 🔮 Future Enhancements

* Transition from SQLite to PostgreSQL for production readiness.
* Implement asynchronous HTTP requests (e.g., `httpx` or `aiohttp`) in Django for faster API consumption.
* Add automated email notifications for approved blood requests.

---

*Developed as a decoupled academic project to demonstrate RESTful API integration.*