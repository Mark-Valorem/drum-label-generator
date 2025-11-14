# Download All Files - Drum Label Generator

**Click each link to download individual files**

---

## Essential Files (Download These First)

1. **[drum_label_generator.py](computer:///mnt/user-data/outputs/drum_label_generator.py)** ← Main script (15KB)
2. **[config.py](computer:///mnt/user-data/outputs/config.py)** ← Configuration settings
3. **[requirements.txt](computer:///mnt/user-data/outputs/requirements.txt)** ← Python dependencies
4. **[sample_data.csv](computer:///mnt/user-data/outputs/sample_data.csv)** ← Example data format

---

## Documentation Files

5. **[COMPLETE_SETUP_GUIDE.md](computer:///mnt/user-data/outputs/COMPLETE_SETUP_GUIDE.md)** ← Everything in one doc
6. **[README.md](computer:///mnt/user-data/outputs/README.md)** ← Full documentation
7. **[QUICK_REFERENCE.md](computer:///mnt/user-data/outputs/QUICK_REFERENCE.md)** ← Command cheat sheet
8. **[CHANGELOG.md](computer:///mnt/user-data/outputs/CHANGELOG.md)** ← Version history

---

## Optional Files

9. **[setup.sh](computer:///mnt/user-data/outputs/setup.sh)** ← Automated setup (Linux/Mac)
10. **[test_installation.py](computer:///mnt/user-data/outputs/test_installation.py)** ← Installation validator

---

## Complete Project Archives

**[drum-label-generator.zip](computer:///mnt/user-data/outputs/drum-label-generator.zip)** ← Everything in one file (12KB)

**[drum-label-generator.tar.gz](computer:///mnt/user-data/outputs/drum-label-generator.tar.gz)** ← Compressed version

---

## After Downloading

### 1. Create Folder Structure

```
drum-label-generator/
├── drum_label_generator.py    (download file #1)
├── config.py                   (download file #2)
├── requirements.txt            (download file #3)
├── sample_data.csv             (download file #4)
├── ghs_pictograms/            (create this folder)
└── output/                    (create this folder)
```

### 2. Install Python Dependencies

```bash
cd drum-label-generator
pip install -r requirements.txt
```

Or manually:
```bash
pip install reportlab pandas openpyxl python-barcode qrcode Pillow
```

### 3. Download GHS Pictograms

Visit: https://unece.org/transport/standards/transport-dangerous-goods/ghs-pictograms

Download 9 PNG files and save to `ghs_pictograms/` folder:
- GHS01.png through GHS09.png

### 4. Edit Company Details

Open `config.py` and update:
```python
COMPANY_NAME = "Valorem Chemicals Pty Ltd"
COMPANY_PHONE = "+61 (0)2 XXXX XXXX"
```

### 5. Test Run

```bash
python3 drum_label_generator.py sample_data.csv
```

Check `output/` folder for generated PDFs.

---

## Complete Setup Instructions

See **[COMPLETE_SETUP_GUIDE.md](computer:///mnt/user-data/outputs/COMPLETE_SETUP_GUIDE.md)** for:
- Detailed installation steps
- GHS pictogram setup
- Data preparation examples
- Troubleshooting guide
- Customisation options
- Compliance notes

---

**Quick Start:**
1. Download files #1-4 (essential files)
2. Download COMPLETE_SETUP_GUIDE.md
3. Follow the guide

**Alternative:**
Download the ZIP archive for everything in one file.
