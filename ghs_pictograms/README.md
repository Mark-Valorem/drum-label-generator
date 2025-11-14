# GHS Pictogram Reference

Place PNG files in this folder with the following naming convention:

## Required Files

| Code   | Name                    | Hazard Category                          |
|--------|-------------------------|------------------------------------------|
| GHS01  | Explosive               | Explosives, Self-reactive substances     |
| GHS02  | Flammable               | Flammables, Pyrophorics, Self-heating    |
| GHS03  | Oxidising               | Oxidisers                                |
| GHS04  | Compressed Gas          | Gases under pressure                     |
| GHS05  | Corrosive               | Corrosives                               |
| GHS06  | Toxic                   | Acute toxicity (severe)                  |
| GHS07  | Harmful                 | Irritant, Skin sensitiser, Acute toxicity (harmful), Narcotic |
| GHS08  | Health Hazard           | Respiratory sensitiser, Carcinogen, Reproductive toxicity, STOT |
| GHS09  | Environmental           | Aquatic toxicity                         |

## Naming Convention

Files must be named **exactly** as:
- `GHS01.png`
- `GHS02.png`
- etc.

(Case-insensitive: GHS01.png, ghs01.png, or Ghs01.png all work)

## Image Specifications

- **Format:** PNG with transparent background
- **Recommended size:** 500×500 pixels minimum
- **Aspect ratio:** 1:1 (square)
- **Background:** White diamond with red border and black pictogram

## Download Source

Official GHS pictograms available from:

**UNECE (United Nations Economic Commission for Europe):**
https://unece.org/transport/standards/transport-dangerous-goods/ghs-pictograms

**Safe Work Australia:**
https://www.safeworkaustralia.gov.au/safety-topic/hazards/chemicals/ghs

**Note:** Ensure you use GHS Revision 7 (current in Australia) pictograms.

## Usage in CSV

Reference multiple pictograms with comma-separated codes:

```csv
ghs_pictograms
"GHS02,GHS07"
"GHS05,GHS06,GHS09"
"GHS07"
```

Leave blank if no GHS classification applies.
