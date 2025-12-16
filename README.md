# Five-G_Ranking_API_Webscrapping (Lightweight Branch)

This branch provides a lightweight version of the ranking scraper API.  
Unlike the main branch, which uses Python + ChromeDriver + Selenium, this implementation relies on **Flask**, **Requests**, and **BeautifulSoup** to keep things simple and efficient.

## ✨ Features
- Exposes a REST API endpoint `/dados` that returns ranking data in JSON format.
- Performs web scraping directly from [Five-G SchoolKing Ranking](https://fiveg.schoolking.com.br/ranking/).
- Normalizes player records (name, team, points, combo).
- Includes in-memory caching (10 minutes) to avoid repeated scraping and reduce server load.
- Ready for deployment on **Render** or similar platforms (uses `PORT` environment variable).

## 🛠️ Tech Stack
- **Python 3**
- **Flask** (API framework)
- **Requests** (HTTP client)
- **BeautifulSoup4** (HTML parsing)

## 📦 Installation
Clone the repository and install dependencies:

```bash
git clone https://github.com/yourusername/Five-G_Ranking_API_Webscrapping.git
cd Five-G_Ranking_API_Webscrapping
pip install -r requirements.txt

