# Da Nang Tourism Data - Setup Guide

## Quick Start

### 1. Clone Repository
```bash
git clone <repo-url>
cd GrabTheBeyound2
```

### 2. Setup Environment

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Configure Environment Variables
Copy the example file and add your credentials:
```bash
cp .env.example .env
```

Edit `.env` with your Neo4j AuraDB credentials:
```ini
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password-here
```

### 3. Run Pipeline

#### Option A: Crawl New Data
```bash
# Crawl all locations from all_urls.json
python crawl_all.py

# Or crawl specific URL
python crawl_gmaps_production.py
```

#### Option B: Use Existing Data
If `data/places/` already exists, skip to import.

#### Import to Neo4j
```bash
# Merge crawled data with Excel sheets
python merge_data.py

# Import to Neo4j AuraDB
python import_to_neo4j.py --uri $NEO4J_URI --user $NEO4J_USERNAME --password $NEO4J_PASSWORD --clear

# Create spatial relationships
python create_spatial_cypher.py
```

### 4. Test & Query
```bash
# Run example queries
python neo4j_examples.py

# Run use case demonstrations
python neo4j_use_cases.py
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEO4J_URI` | Neo4j connection URI | Required |
| `NEO4J_USERNAME` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | Required |
| `DATA_DIR` | Directory with merged data | `data/places` |
| `PHOTOS_BASE_DIR` | Photos storage | `data/photos` |
| `SPATIAL_DISTANCE_KM` | Distance for NEAR relationships | `2.0` |

## Security Notes

⚠️ **Never commit `.env` to Git!**
- `.env` is already in `.gitignore`
- Use `.env.example` as template for team members
- Keep production credentials secure

## requirements.txt

All dependencies are listed in `requirements.txt`:
- `neo4j==6.0.3` - Neo4j Python driver
- `python-dotenv==1.0.0` - Environment variable management
- `openpyxl==3.1.2` - Excel file processing
- `selenium==4.15.2` - Web scraping

## Project Structure

```
GrabTheBeyound2/
├── .env                        # Your credentials (not in Git)
├── .env.example                # Template for .env
├── requirements.txt            # Python dependencies
├── crawl_all.py               # Batch crawler
├── import_to_neo4j.py         # Neo4j importer
├── neo4j_use_cases.py         # Query examples
├── sheet/                     # Excel data files
└── data/                      # Crawled data (ignored by Git)
```

## Troubleshooting

### Missing python-dotenv
```bash
pip install python-dotenv==1.0.0
```

### Connection Errors
Check your `.env` file has correct Neo4j credentials:
```bash
cat .env
```

### Import Issues
Make sure to run `merge_data.py` before importing to Neo4j.
