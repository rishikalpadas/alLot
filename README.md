# alLot - Inventory Management & Billing

Windows desktop application for inventory management and billing.

## Setup

1. Install Python 3.11+
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`

## Building Portable EXE

```bash
pip install pyinstaller
pyinstaller build.spec
```

The executable will be in `dist/alLot.exe`

## Default Login

- Username: `admin`
- Password: `admin`

Change password in Control Panel > Settings after first login.
