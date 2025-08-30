"""
Enhanced configuration with data source settings
"""
import os
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Existing configuration...
    HOST: str = os.getenv("HOST", "localhost")
    PORT: int = int(os.getenv("PORT", 8000))
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    VECTOR_DIMENSION: int = int(os.getenv("VECTOR_DIMENSION", 384))
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 200))
    
    # Paths
    DATA_DIR: str = "data"
    RAW_DATA_DIR: str = os.path.join(DATA_DIR, "raw")
    PROCESSED_DATA_DIR: str = os.path.join(DATA_DIR, "processed")
    VECTORSTORE_DIR: str = os.path.join(DATA_DIR, "vectorstore")
    CACHE_DIR: str = os.path.join(DATA_DIR, "cache")
    
    # Data Source Configuration
    ENABLE_AUTO_UPDATES: bool = os.getenv("ENABLE_AUTO_UPDATES", "true").lower() == "true"
    UPDATE_FREQUENCY_HOURS: int = int(os.getenv("UPDATE_FREQUENCY_HOURS", 24))
    MAX_DOCUMENTS_PER_SOURCE: int = int(os.getenv("MAX_DOCUMENTS_PER_SOURCE", 50))
    
    # Data Sources Configuration
    DATA_SOURCES = {
        "ipcc": {
            "enabled": True,
            "base_url": "https://www.ipcc.ch",
            "reports_url": "https://www.ipcc.ch/reports/",
            "priority": 1
        },
        "unfccc": {
            "enabled": True,
            "base_url": "https://unfccc.int",
            "documents_url": "https://unfccc.int/documents",
            "ndc_registry": "https://www4.unfccc.int/sites/ndcstaging/Pages/All.aspx",
            "priority": 1
        },
        "world_bank": {
            "enabled": True,
            "base_url": "https://www.worldbank.org",
            "climate_portal": "https://climateknowledgeportal.worldbank.org",
            "api_base": "https://api.worldbank.org/v2",
            "priority": 2
        },
        "iea": {
            "enabled": True,
            "base_url": "https://www.iea.org",
            "reports_url": "https://www.iea.org/reports",
            "data_url": "https://www.iea.org/data-and-statistics",
            "priority": 2
        },
        "oecd": {
            "enabled": True,
            "base_url": "https://www.oecd.org",
            "environment_url": "https://www.oecd.org/environment",
            "api_base": "https://stats.oecd.org/restsdmx/sdmx.ashx",
            "priority": 3
        },
        "climate_watch": {
            "enabled": True,
            "base_url": "https://www.climatewatchdata.org",
            "api_base": "https://www.climatewatchdata.org/api/v1",
            "priority": 2
        },
        "our_world_data": {
            "enabled": True,
            "base_url": "https://ourworldindata.org",
            "climate_url": "https://ourworldindata.org/climate-change",
            "github_data": "https://github.com/owid/owid-datasets",
            "priority": 2
        },
        "nasa_climate": {
            "enabled": True,
            "base_url": "https://climate.nasa.gov",
            "data_url": "https://climate.nasa.gov/climate_resources",
            "api_base": "https://api.nasa.gov",
            "priority": 3
        },
        "arxiv": {
            "enabled": True,
            "base_url": "https://arxiv.org",
            "api_base": "http://export.arxiv.org/api",
            "climate_categories": ["physics.ao-ph", "econ.GN", "cs.CY"],
            "priority": 4
        }
    }
    
    # Web scraping settings
    REQUEST_DELAY: float = float(os.getenv("REQUEST_DELAY", 1.0))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", 3))
    TIMEOUT: int = int(os.getenv("TIMEOUT", 30))
    USER_AGENT: str = "Climate-Policy-Intelligence-Platform/2.0"
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        for dir_path in [cls.RAW_DATA_DIR, cls.PROCESSED_DATA_DIR, 
                        cls.VECTORSTORE_DIR, cls.CACHE_DIR]:
            os.makedirs(dir_path, exist_ok=True)

config = Config()