# Digikala Search Scraper
This script extracts product data from Digikala, a popular online marketplace. The results are saved as a CSV or file.

# HOW TO USE

1. **Create a Virtual Environment**

   In your working directory, run:

   ```bash
   python3 -m venv scraper_env
   ```

2. **Activate the Virtual Environment**

   - **On Linux/macOS:**
     ```bash
     source scraper_env/bin/activate
     ```
   - **On Windows:**
     ```bash
     scraper_env\Scripts\activate
     ```

3. **Install Dependencies**

   Install the required libraries by running:

   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Installation**

   To verify that all necessary libraries are installed correctly, run:

   ```bash
   python -c "import requests; import pandas; import numpy; print('All libraries are installed correctly')"
   ```

5. **Run the Scraper**

   - **For an English search:**

     ```bash
     python digikala_search_scrape.py -s "iphone" -i 20
     ```

   - **For an English-Persian search:**

     ```bash
     python digikala_search_scrape.py -s "iphone گوشی" -i 20
     ```
