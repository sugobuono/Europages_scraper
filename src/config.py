class PipelineConfig:
    def __init__(self, sector, base_search_url, output_dir, headless=True, max_pages=25):
        self.sector = sector
        self.base_search_url = base_search_url
        self.output_dir = output_dir
        self.headless = headless
        self.max_pages = max_pages


DEFAULT_CONFIG = PipelineConfig(
    "wine",
    "https://www.europages.co.uk/en/search?q=wine+producers",
    "data",
    True,
    25
)
