### README.md

# Flipkart Product Scraper and Review Sentiment Analyzer

This is a Flask-based web application that scrapes product details and customer reviews from Flipkart and performs sentiment analysis on the reviews. The application saves the product information and sentiment percentages to a MySQL database. The sentiment analysis is performed using both NLTK's `SentimentIntensityAnalyzer` and Huggingface's `distilbert-base-uncased-finetuned-sst-2-english` model.

The live version of this project is available [here](https://reviews-sentiment-analysis.onrender.com).

## Features

- **Product Scraping**: Scrapes details such as product name, image, price, discount, ratings, seller details, etc.
- **Review Scraping**: Extracts customer reviews from Flipkart.
- **Sentiment Analysis**: Classifies reviews as positive, negative, or neutral using state-of-the-art NLP models.
- **MySQL Integration**: Saves the product details and sentiment analysis results to a MySQL database.
- **Flask Frontend**: Provides a simple user interface for scraping products and viewing detailed reports.

## Tech Stack

- **Backend**: Flask, Python
- **Frontend**: HTML, CSS, Jinja2
- **Database**: MySQL
- **Web Scraping**: Selenium, BeautifulSoup
- **NLP**: NLTK, Huggingface Transformers
- **Deployment**: Render.com (Live [here](https://reviews-sentiment-analysis.onrender.com))

## Setup Instructions

### Prerequisites

- Python 3.x
- MySQL Server
- ChromeDriver (for Selenium)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/flipkart-sentiment-analysis.git
   cd flipkart-sentiment-analysis
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Setup MySQL database:
   - Create a MySQL database.
   - Update your MySQL credentials in the `.env` file (or configure environment variables).

4. Run the Flask app:
   ```bash
   python app.py
   ```

5. Visit the application on `http://localhost:5000/`.

### Environment Variables

Set up the following environment variables:

```
MYSQL_HOST=your_mysql_host
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=your_database_name
```

### Example Usage

1. On the homepage, enter the Flipkart product URL you want to analyze.
2. The application will scrape the product details and customer reviews.
3. Sentiment analysis will be performed on the reviews.
4. The product details and sentiment results will be displayed on a report page.
5. Data is saved to the MySQL database for further analysis.

## Files Structure

```bash
flipkart-sentiment-analysis/
│
├── templates/
│   ├── index.html  # Input form for scraping products
│   ├── report.html  # Displays product details and sentiment results
│
├── app.py  # Main application logic
├── requirements.txt  # Required Python packages
└── README.md  # Project documentation
```

## Deployment

The application is deployed on Render.com. You can access it via the following link:  
[https://reviews-sentiment-analysis.onrender.com](https://reviews-sentiment-analysis.onrender.com).

To deploy the project:

1. Create a new web service on Render and connect your GitHub repository.
2. Specify the following build command in the Render setup:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up the necessary environment variables (MySQL credentials) on Render.
4. Deploy the web service and your application will be live!

## Contributing

Feel free to open issues or submit pull requests. Contributions are welcome to improve functionality, fix bugs, or enhance documentation.
