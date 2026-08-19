# Expense Report System

A mobile/web Expense Report System for employees to create, view, and submit their business expenses.

## Technologies Used

* **Frontend:** React Native, Expo, React Native Web
* **Backend:** Python, FastAPI
* **Database:** SQLite
* **Authentication:** JWT
* **API:** REST API

## Project Structure

```text
Expense-Report-System/
├── backend/
│   ├── main.py
│   └── requirements.txt
├── mobile/
│   ├── App.js
│   ├── app.json
│   ├── package.json
│   └── src/
│       ├── api.js
│       └── screens/
│           ├── LoginScreen.js
│           ├── ExpenseListScreen.js
│           ├── NewExpenseScreen.js
│           └── ExpenseDetailScreen.js
├── .gitignore
└── README.md
```

## Features

* Employee login
* View personal expenses
* Create a new expense
* Enter title, amount, category, description, and receipt filename
* Submit expenses
* View expense details
* Employee-specific expense access
* Logout
* JWT-based authentication
* FastAPI backend with SQLite database

## Employee Login

The demo application includes the following employee accounts:

```text
amit@beeja.com
neha@beeja.com
rahul@beeja.com
```

Select the employee role when logging in.

## Backend Setup

Open a terminal and navigate to the backend folder:

```powershell
cd backend
```

Install the required Python packages:

```powershell
pip install -r requirements.txt
```

Start the FastAPI server:

```powershell
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will run on:

```text
http://127.0.0.1:8000
```

FastAPI documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Frontend Setup

Open another terminal and navigate to the mobile folder:

```powershell
cd mobile
```

Install the dependencies:

```powershell
npm install
```

Start the Expo application for web:

```powershell
npx expo start --web
```

The application can then be opened in the browser.

## API Configuration

For local web testing, `mobile/src/api.js` uses:

```javascript
export const API_BASE="http://127.0.0.1:8000";
```

If the application is run on a physical phone using Expo Go, `127.0.0.1` should be replaced with the LAN IP address of the computer running the FastAPI backend.

For example:

```javascript
export const API_BASE="http://192.168.x.x:8000";
```

Both the phone and the computer must be connected to the same network.

## Expense Workflow

The employee can:

1. Log in using an employee email.
2. View existing expenses.
3. Select **New** to create an expense.
4. Enter the expense details.
5. Save the expense.
6. Submit the expense.
7. Select the expense to view its details.
8. Log out.

## Example Expense

```text
Title: Office Travel
Category: Travel
Amount: ₹500
Date: 2026-08-18
Status: Submitted
Description: Travel expense for office work
Receipt: receipt_test.pdf
```

## Notes

The SQLite database is created automatically by the FastAPI backend.

The local database file and dependency folders are excluded from Git using `.gitignore`.
