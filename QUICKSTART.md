# alLot - Quick Start Guide

## Installation & Running

### Prerequisites
- Python 3.11 or higher
- Windows OS

### Setup Steps

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python main.py
   ```

3. **Default login credentials:**
   - Username: `admin`
   - Password: `admin`
   
   **Important:** Change the password immediately after first login via Control Panel > Settings.

## Building Portable EXE

To create a standalone executable that can be distributed:

1. **Install PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Build the executable:**
   ```bash
   pyinstaller build.spec
   ```

3. **Find the executable:**
   - The portable EXE will be in `dist/alLot.exe`
   - Send this single file to clients
   - No installation required - just double-click to run

## Application Flow

### First-Time Setup (Control Panel)

1. **Add Distributors:**
   - Go to Control Panel > Distributors
   - Add your suppliers/distributors
   - Set purchase rates for each product per distributor

2. **Add Parties:**
   - Go to Control Panel > Parties
   - Add your customers/parties
   - Set sale rates for each product per party

3. **Add Products:**
   - Go to Control Panel > Products
   - Add product catalog (SKU, name, unit, tax rate, etc.)

### Daily Operations

1. **Recording Purchases:**
   - Go to Transactions > Purchase
   - Select distributor (rates auto-populate)
   - Add products with quantities
   - Save transaction
   - Stock automatically increases

2. **Recording Sales:**
   - Go to Transactions > Sale
   - Select party (rates auto-populate)
   - Add products with quantities
   - System checks stock availability
   - Save transaction
   - Stock automatically decreases

3. **View Stock:**
   - Go to View > Stock
   - See current stock levels for all products
   - Color-coded status (In Stock, Low Stock, Out of Stock)

4. **Generate Reports:**
   - Go to View > Reports
   - Choose report type (Purchase or Sale)
   - Set date range and filters
   - Generate PDF report
   - Can be printed directly

## Database Location

The SQLite database is stored in:
- **Windows:** `%APPDATA%\alLot\allot.db`

This ensures data persists between runs and is stored securely in the user's app data folder.

## Features Summary

✅ Single admin user with password change capability
✅ Distributor management with product-specific purchase rates
✅ Party management with product-specific sale rates
✅ Product catalog with SKU, tax rates, units
✅ Purchase transactions with auto-rate population
✅ Sale transactions with stock validation
✅ Real-time stock tracking (purchases add, sales subtract)
✅ PDF report generation (purchase reports, sale reports)
✅ Date range filtering for reports
✅ Distributor/party filtering for reports
✅ Professional GUI with modern design
✅ Offline operation (no internet required)
✅ Portable single-EXE deployment

## Troubleshooting

**Issue:** Application won't start
- **Solution:** Ensure Python 3.11+ is installed and dependencies are installed via `pip install -r requirements.txt`

**Issue:** Can't login
- **Solution:** Default credentials are `admin`/`admin`. If changed and forgotten, delete the database file to reset.

**Issue:** Stock not updating
- **Solution:** Check that products are added to control panel first, and distributor/party price lists are configured.

**Issue:** PDF generation fails
- **Solution:** Ensure reportlab is installed: `pip install reportlab`

## Support

For issues or questions, refer to the codebase documentation in each module.
