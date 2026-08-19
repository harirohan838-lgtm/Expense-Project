# Expense Report Employee Mobile App

This project contains the React Native + Expo employee application.

Before running, edit:
mobile/src/api.js

Replace YOUR_LOCAL_IP with the LAN IP address of the computer running the FastAPI backend.

Then:
npm install
npx expo start

## Backend

The project now includes a self-contained FastAPI backend in `backend/`.

### Start the backend

From the `backend` folder:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

The API documentation is available at:

`http://127.0.0.1:8000/docs`

Test employee logins:
- amit@beeja.com
- neha@beeja.com
- rahul@beeja.com

The backend uses SQLite (`expense_db.sqlite3`) so it can run without a separate MySQL installation. The mobile app should point `mobile/src/api.js` to the computer's LAN IP, for example `http://192.168.1.105:8000`.
