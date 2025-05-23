# Real Estate Multi-Agent System

This project implements a multi-agent AI system for real estate that includes:

1. **Data Collection Agent**: Gathers and maintains information about real estate properties from various sources
2. **Sales Agent**: Communicates with clients, understands their needs, and matches them with suitable properties

## Project Structure

```
real_estate_agents/
├── data_collector/     # Agent for collecting property data
│   └── scrapers/       # Web scrapers for property websites
├── sales_agent/        # Agent for client interaction and property matching
├── database/           # Storage for property information
├── utils/              # Shared utilities
└── api/                # API for system interaction
```

## Setup

### Quick Start with Docker

1. Clone the repository:
   ```
   git clone https://github.com/Justgrow123213/Justgrow123213.git
   cd Justgrow123213
   ```

2. Create a `.env` file with your OpenAI API key:
   ```
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

3. Run the Docker deployment script:
   ```
   ./docker-run.sh
   ```

4. Access the application at `http://localhost:8000`

### Manual Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure environment variables:
   Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. Run the application:
   ```
   ./run.sh both  # Run both the web app and the scraper
   ```

   Alternatively, you can run them separately:
   ```
   ./run.sh app     # Run only the web app
   ./run.sh scraper # Run only the scraper
   ```

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Usage

### Web Interface

Access the web interface at `http://localhost:8000` to:
- Chat with the sales agent
- Search for properties
- View property recommendations

### API Endpoints

The system provides an API for interacting with the real estate agents:

#### Property Management
- `GET /properties`: Get all properties
- `GET /properties/{property_id}`: Get a specific property
- `POST /add-property`: Add a new property manually
- `GET /search-properties`: Search properties by criteria

#### Agent Interaction
- `POST /chat`: Chat with the sales agent
- `POST /get-recommendations`: Get property recommendations

#### Data Collection
- `POST /scrape-website`: Scrape properties from a specific website
- `POST /scrape-ddproperty`: Scrape properties from DDProperty
- `POST /scrape-m2agent`: Scrape properties from M2Agent
- `GET /available-sources`: Get available scraper sources

### Data Collection Script

You can use the `scrape_properties.py` script to collect property data:

```
python scrape_properties.py --source ddproperty --location bangkok --property-type condo --max-pages 2
```

Options:
- `--source`: Website to scrape (`ddproperty`, `m2agent`, or `both`)
- `--max-pages`: Maximum number of pages to scrape
- `--location`: Location for DDProperty (e.g., bangkok, phuket)
- `--city`: City for M2Agent (e.g., moscow, saint-petersburg)
- `--property-type`: Type of property

### Jupyter Notebook Example

See `scraping_example.ipynb` for a detailed example of using the scrapers programmatically.