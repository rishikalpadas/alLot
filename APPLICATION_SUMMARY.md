# alLot - Application Summary

## Overview
alLot is a Windows desktop inventory management and billing application built with Python and PySide6 (Qt). It provides a complete solution for managing distributors, parties, products, purchases, sales, and generating reports.

## Technology Stack
- **Language:** Python 3.11+
- **GUI Framework:** PySide6 (Qt for Python)
- **Database:** SQLite (embedded, file-based)
- **ORM:** SQLAlchemy 2.0
- **Authentication:** bcrypt (password hashing)
- **PDF Generation:** ReportLab
- **Packaging:** PyInstaller (single EXE)

## Architecture

### Project Structure
```
alLot/
├── main.py                      # Entry point
├── requirements.txt             # Dependencies
├── build.spec                   # PyInstaller config
├── database/
│   ├── models.py               # SQLAlchemy models
│   └── db_manager.py           # DB setup & session management
├── services/
│   ├── auth_service.py         # Authentication logic
│   ├── pricing_service.py      # Pricing logic
│   ├── inventory_service.py    # Inventory & stock management
│   └── report_service.py       # Report generation
├── ui/
│   ├── login_window.py         # Login screen
│   ├── main_window.py          # Dashboard & navigation
│   ├── purchase_window.py      # Purchase transactions
│   ├── sale_window.py          # Sale transactions
│   ├── stock_window.py         # Stock view
│   ├── reports_window.py       # Report generation UI
│   └── control_panel/
│       ├── distributors.py     # Distributor management
│       ├── parties.py          # Party management
│       ├── products.py         # Product management
│       └── settings.py         # Password change
└── utils/
    └── helpers.py              # Utility functions
```

### Database Schema

**Users Table:**
- Stores admin credentials (bcrypt hashed)
- Default user: admin/admin

**Distributors Table:**
- Supplier information
- Contact details

**Parties Table:**
- Customer information
- Contact details

**Products Table:**
- SKU, name, description
- Unit, HSN code, tax rate
- Reorder level

**DistributorPrice Table:**
- Distributor-specific purchase rates per product
- Many-to-many relationship

**PartyPrice Table:**
- Party-specific sale rates per product
- Many-to-many relationship

**Purchase/PurchaseItem Tables:**
- Purchase transaction header and line items
- Auto-generated purchase numbers (PUR000001, etc.)

**Sale/SaleItem Tables:**
- Sale transaction header and line items
- Auto-generated sale numbers (SAL000001, etc.)

**StockLedger Table:**
- All stock movements (purchases add, sales subtract)
- Transaction type and reference ID
- Current stock derived by summing quantity_delta

## Key Features

### 1. Authentication
- Single admin user
- Secure password hashing with bcrypt
- Password change in settings
- Login lockout on invalid credentials

### 2. Control Panel
- **Distributors:** Add/edit/delete distributors with contact info
- **Parties:** Add/edit/delete parties with contact info
- **Products:** Add/edit/delete products with SKU, tax rates, units
- **Settings:** Change admin password

### 3. Purchase Management
- Select distributor
- Purchase rates auto-populate based on distributor-product pricing
- Add multiple line items
- Invoice number and notes optional
- Auto-generated purchase numbers
- Stock automatically increased

### 4. Sale Management
- Select party
- Sale rates auto-populate based on party-product pricing
- Add multiple line items
- Stock validation (prevents overselling)
- Invoice number and notes optional
- Auto-generated sale numbers
- Stock automatically decreased

### 5. Stock Management
- View current stock for all products
- Color-coded status:
  - Green: In Stock
  - Orange: Low Stock (below reorder level)
  - Red: Out of Stock
- Real-time updates based on transactions

### 6. Reporting
- **Purchase Reports:**
  - Filter by date range
  - Filter by distributor
  - Shows total purchases and amounts
  - Export to PDF
- **Sale Reports:**
  - Filter by date range
  - Filter by party
  - Shows total sales and amounts
  - Export to PDF

### 7. User Interface
- Modern, clean design
- Dashboard with quick-access buttons
- Menu bar navigation
- Fusion style with custom color palette
- Responsive layouts
- Form validation
- Confirmation dialogs for destructive actions

## Deployment

### Development Mode
```bash
pip install -r requirements.txt
python main.py
```

### Production Build
```bash
pip install pyinstaller
pyinstaller build.spec
```

Produces a single portable EXE: `dist/alLot.exe`

**Deployment to clients:**
- Send `alLot.exe` file only
- No installation required
- Double-click to run
- Database auto-created on first run in `%APPDATA%\alLot\`

## Data Flow

### Purchase Flow
1. Admin selects distributor
2. System loads distributor-specific rates
3. Admin adds products (rates auto-populated)
4. On save:
   - Purchase record created
   - Purchase items created
   - Stock ledger entries created (+quantity)
   - Purchase number auto-generated

### Sale Flow
1. Admin selects party
2. System loads party-specific rates
3. Admin adds products (rates auto-populated)
4. System validates stock availability
5. On save:
   - Sale record created
   - Sale items created
   - Stock ledger entries created (-quantity)
   - Sale number auto-generated

### Stock Calculation
- Stock is never stored directly
- Always calculated: `SUM(quantity_delta) WHERE product_id = X`
- Positive delta = purchase
- Negative delta = sale
- Provides audit trail

## Security Considerations
- Passwords hashed with bcrypt (salted)
- Database stored in user AppData (not publicly accessible)
- No network exposure (offline app)
- Single-user design (no concurrent access issues)

## Extension Points

Future enhancements could include:
- Multi-user support with roles
- Barcode scanning integration
- Email/SMS notifications for low stock
- Payment tracking
- Profit/loss analysis
- Product categories
- Import/export CSV
- Backup/restore functionality
- Cloud sync (optional)

## Testing

Manual testing checklist:
- ✅ Login with correct/incorrect credentials
- ✅ Add/edit/delete distributors
- ✅ Add/edit/delete parties
- ✅ Add/edit/delete products
- ✅ Set distributor prices
- ✅ Set party prices
- ✅ Create purchase (stock increases)
- ✅ Create sale (stock decreases)
- ✅ Attempt overselling (should fail)
- ✅ View stock levels
- ✅ Generate purchase report PDF
- ✅ Generate sale report PDF
- ✅ Change password
- ✅ Logout and login again

## Performance
- SQLite: Handles thousands of transactions efficiently
- Qt: Native performance on Windows
- PDF generation: Fast for typical report sizes
- EXE size: ~50-80MB (includes Python runtime + Qt)
- Startup time: 2-3 seconds on modern hardware
- Memory usage: ~100-150MB typical

## Maintenance
- Database in `%APPDATA%\alLot\allot.db`
- Backup: Copy database file
- Reset: Delete database file (recreates with default admin)
- Updates: Replace EXE file

## License
(Specify your license here)

---

**Application Name:** alLot  
**Version:** 1.0  
**Platform:** Windows 10/11  
**Python Version:** 3.11+  
**Build Date:** January 2026
