import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/climate_policy")
    
    # Data Sources
    IPCC_BASE_URL = "https://www.ipcc.ch/reports/"
    UNFCCC_API = "https://unfccc.int/api/"
    WORLD_BANK_API = "https://api.worldbank.org/v2/"
    IEA_DATA_URL = "https://www.iea.org/data-and-statistics"
    CLIMATE_WATCH_API = "https://www.climatewatchdata.org/api/v1/"
    
    # Data Paths
    RAW_DATA_PATH = Path("../data/raw")
    PROCESSED_DATA_PATH = Path("../data/processed")
    EMBEDDINGS_PATH = Path("../data/embeddings")
    
    # Processing
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    BATCH_SIZE = 32
    
    # API Settings
    API_RATE_LIMIT = 10  # requests per second
    SCRAPING_DELAY = 2  # seconds between scraping requests
    
    # Vector Database (for Phase 2)
    VECTOR_DB_TYPE = "pinecone"  # or "weaviate"
    VECTOR_DIMENSION = 768
    
    # LLM Settings (for Phase 3)
    LLM_MODEL = "gpt-3.5-turbo"
    MAX_TOKENS = 2000
    TEMPERATURE = 0.7