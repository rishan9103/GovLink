# GovAssist Frontend

Vanilla HTML, CSS, and JavaScript frontend for the GovAssist Flask API.

## Run

From the repository root:

```powershell
cd C:\Users\acer\GovAssist\frontend
python -m http.server 5500
```

Open <http://localhost:5500>.

Start the backend separately from `backend`:

```powershell
cd C:\Users\acer\GovAssist\backend
.\.venv\Scripts\Activate.ps1
python app.py
```

## API integration

`js/app.js` uses one configurable value:

```js
const API_BASE_URL = "http://localhost:5000";
```

The live mode calls:

- `GET /api/services`
- `GET /api/categories`
- `POST /api/chat`

Chat requests include `message`, `language`, and a session ID stored in `sessionStorage`. Returned `sources` are rendered beneath assistant answers.

`USE_MOCK_DATA` is `false` by default. Set it to `true` in `js/app.js` only for an intentionally offline UI demo.
