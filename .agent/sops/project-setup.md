# SOP: Project Setup for New Developers

**version:** v1.0.0
**Created:** 2025-11-14
**Last Updated:** 2025-11-14

## When to Use

When setting up the development environment for the first time on a new machine or for a new team member.

## Prerequisites

- **Python 3.8+** installed
- **pip** package manager
- **Git** installed and configured
- **GitHub access** to repository (if using remote)
- **Text editor or IDE** (VS Code, PyCharm, etc.)

## Process

### 1. Clone Repository

```bash
git clone https://github.com/valoremchemicals/drum-label-generator.git
cd drum-label-generator
```

**Or if setting up locally:**
Navigate to the project folder:
```bash
cd "c:\Users\MarkAnderson\Valorem\Project Hub - Documents\Coding Projects\2511_DOD Labels"
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected packages:**
- reportlab 4.0.7 (PDF generation)
- pandas 2.1.4 (data processing)
- openpyxl 3.1.2 (Excel support)
- python-barcode 0.15.1 (barcode generation)
- qrcode 7.4.2 (QR code generation)
- Pillow 10.1.0 (image processing)

### 4. Download GHS Pictograms

#### Option A: Download from UNECE

1. Visit: https://unece.org/transport/standards/transport-dangerous-goods/ghs-pictograms
2. Download all 9 pictogram PNG files
3. Save to `ghs_pictograms/` folder

#### Option B: Use Company-Approved Versions

Contact Valorem IT/Operations for approved GHS pictogram files.

**Required files:**
- `GHS01.png` - Explosive
- `GHS02.png` - Flammable
- `GHS03.png` - Oxidising
- `GHS04.png` - Compressed Gas
- `GHS05.png` - Corrosive
- `GHS06.png` - Toxic
- `GHS07.png` - Harmful/Irritant
- `GHS08.png` - Health Hazard
- `GHS09.png` - Environmental

**Verify:**
```bash
ls ghs_pictograms/
```

Should show 9 PNG files.

### 5. Configure Company Details (Optional)

Edit `config.py` to customize:

```python
# Line 50-53: Company Details
COMPANY_NAME = "Valorem Chemicals Pty Ltd"
COMPANY_ADDRESS = "Sydney, NSW, Australia"
COMPANY_PHONE = "+61 (0)2 XXXX XXXX"
COMPANY_EMAIL = "info@valoremchemicals.com.au"
```

### 6. Run Tests to Verify Setup

```bash
python test_installation.py
```

**Expected output:**
- ✓ All dependencies installed
- ✓ Folders created
- ✓ GHS pictograms present
- ✓ Sample data valid
- ✓ Test label generated

### 7. Generate Sample Labels

```bash
python drum_label_generator.py sample_data.csv
```

**Expected output:**
```
Loaded 3 records from sample_data.csv
Generated: output/drum_label_VAL-VM-100_LN240815_20251114_103022.pdf
Generated: output/drum_label_VAL-AD-250_KI240722_20251114_103022.pdf
Generated: output/drum_label_VAL-BO-500_EM240910_20251114_103022.pdf

Generation complete. Output saved to 'output/'
```

### 8. Verify Output

Open PDFs in `output/` folder and check:
- Company header displays correctly
- Product information table formatted properly
- GHS pictograms visible (if applicable)
- Barcode readable
- QR code scannable with mobile device
- All text legible

### 9. Configure Git (First Time)

```bash
git config user.name "Your Name"
git config user.email "your.email@valoremchemicals.com.au"
```

### 10. Read Documentation

Review these files:
- `CLAUDE.md` - AI agent documentation and conventions
- `.agent/README.md` - Documentation index
- `README.md` - Quick start guide
- `.agent/sops/git-workflow.md` - Git conventions

## Related Documentation

- [CLAUDE.md](../../CLAUDE.md) - Common commands and conventions
- [git-workflow.md](git-workflow.md) - Git branching and commit guidelines
- [README.md](../../README.md) - Project overview

## Common Mistakes

### Mistake: Python version too old
**Symptom:** Import errors or syntax errors
**Solution:** Ensure Python 3.8 or newer:
```bash
python --version
```

### Mistake: Forgetting to activate virtual environment
**Symptom:** "Module not found" errors
**Solution:**
```bash
# Activate venv first
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### Mistake: Missing GHS pictograms
**Symptom:** "Warning: GHS pictogram 'GHS02' not found"
**Solution:** Download all 9 PNG files to `ghs_pictograms/` folder

### Mistake: Not creating output folder
**Symptom:** File write errors
**Solution:** Folder is auto-created, but verify:
```bash
mkdir output
```

### Mistake: Editing production data files
**Solution:** Always use copies of data files, never edit originals directly

## Troubleshooting

### Issue: pip install fails

**Try:**
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install packages individually
pip install reportlab
pip install pandas
pip install openpyxl
pip install python-barcode
pip install qrcode
pip install Pillow
```

### Issue: Barcode module errors

**Solution:**
```bash
pip uninstall python-barcode
pip install python-barcode[images]
```

### Issue: Permission errors on Windows

**Solution:** Run terminal as Administrator or adjust folder permissions

## Environment Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed via requirements.txt
- [ ] GHS pictograms (9 PNG files) in `ghs_pictograms/`
- [ ] `output/` folder exists
- [ ] test_installation.py passes
- [ ] Sample labels generate successfully
- [ ] PDFs viewable and print correctly
- [ ] Git configured with name and email
- [ ] Documentation reviewed

## Next Steps After Setup

1. **Try generating labels with custom data:**
   - Create a CSV with your own product data
   - Run: `python drum_label_generator.py your_data.csv`

2. **Integrate with Unleashed:**
   - Export product data from Unleashed
   - Format columns to match required schema
   - Generate labels for production

3. **Customize layouts (if needed):**
   - Edit `config.py` for fonts, sizes, margins
   - Modify `drum_label_generator.py` for layout changes
   - Test with sample data before production use

4. **Set up automated workflows:**
   - Schedule weekly label generation
   - Integrate with printing systems
   - Configure archival processes
