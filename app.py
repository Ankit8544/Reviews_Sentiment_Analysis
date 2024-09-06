# Import Module
from flask import Flask, request,render_template
from flask_cors import CORS, cross_origin
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager  # Ensure this is installed
import time
import pandas as pd
import re
import pandas as pd
import mysql.connector
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import word_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
from transformers import pipeline
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import nltk
nltk.download('punkt')
nltk.download('stopwords')

# Function to Scrap Product Detail
def scrape_product_details(Product_URL):
    options = Options()
    options.add_argument("--headless")  # Run the browser in headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-gpu")
    
    # Set up ChromeDriver with webdriver-manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    # Load the Product URL
    driver.get(Product_URL)
    time.sleep(3)  # Let the page load
    # Scroll down to load more Details (adjust the number of scrolls as needed)
    scrolls = 3
    for _ in range(scrolls):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(2)
    # Get the page source after scrolling
    Product_Page = driver.page_source
    # Close the browser
    driver.quit()
    # Now you can use BeautifulSoup to parse the loaded content
    HTML = bs(Product_Page, 'html.parser')
        
    Product_Name = HTML.find("span",{"class":"VU-ZEz"}).text.replace('\xa0', ' ').strip()
    Product_Image = HTML.find("div",{"class":"_4WELSP _6lpKCl"}).img.get('src')
    Original_Price = float(HTML.find('div', class_=['yRaY8j', 'A6+E6v']).get_text().strip().replace('₹', '').replace(',', '').strip())
    Discount = float(HTML.find('div', class_=['UkUFwK', 'WW8yVX']).text.strip().replace("% off","").strip())
    Special_Price = float(HTML.find('div', class_ = ['Nx9bqj', 'CxhGGd']).text.replace('₹','').replace(',',''))
    Rating = float(HTML.find("div",{"class":"XQDdHH"}).text)
    Total_Number_of_Ratings = int(re.sub(r'[^\d]', '', HTML.find_all("div",{"class":"row j-aW8Z"})[0].div.text))
    Total_Number_of_Reviews = int(re.sub(r'[^\d]', '', HTML.find_all("div",{"class":"row j-aW8Z"})[1].div.text))
    Delivery_Date = HTML.find('span', class_='Y8v7Fl').text.split(",")[0]
    Seller_Name = HTML.find("div",{"class":"yeLeBC"}).span.span.text
    Seller_Rating = float(HTML.find("div",{"class":"yeLeBC"}).div.text)
    Link = HTML.find("div",{"class":"col pPAw9M"}).find_all('a')[-1].get('href')
    
    # Return the product details in a dictionary
    return {
        "Product Name": Product_Name,
        "Product Image": Product_Image,
        "Original Price": Original_Price,
        "Discount %": Discount,
        "Special Price": Special_Price,
        "Rating": Rating,
        "Total Number of Ratings": Total_Number_of_Ratings,
        "Total Number of Reviews": Total_Number_of_Reviews,
        "Delivery Date": Delivery_Date,
        "Seller Name": Seller_Name,
        "Seller Rating": Seller_Rating,
        "Link": Link
    }

# Function to save product details to MySQL
def save_to_mysql(product_details):
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DB')
        )
        cursor = connection.cursor()
        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_details (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_url TEXT,
                product_name TEXT,
                product_image TEXT,
                original_price FLOAT,
                discount FLOAT,
                special_price FLOAT,
                overall_rating FLOAT,
                total_ratings INT,
                total_reviews INT,
                expected_delivery_date TEXT,
                seller_name TEXT,
                seller_rating FLOAT,
                positive_reviews_percentage FLOAT,
                negative_reviews_percentage FLOAT,
                neutral_reviews_percentage FLOAT
            )
        ''')
        # Insert product details into the database
        insert_query = '''
            INSERT INTO product_details (
                product_url, product_name, product_image, original_price, discount, special_price, overall_rating, 
                total_ratings, total_reviews, expected_delivery_date, seller_name, seller_rating, 
                positive_reviews_percentage, negative_reviews_percentage, neutral_reviews_percentage
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(insert_query, (
            product_details["Product URL"], product_details["Product Name"], product_details["Product Image"],
            product_details["Original Price"], product_details["Discount %"], product_details["Special Price"],
            product_details["Overall Rating"], product_details["Total Ratings"], product_details["Total Reviews"],
            product_details["Expected Delivery Date"], product_details["Seller Name"], product_details["Seller Rating"],
            product_details["Positive Reviews %"], product_details["Negative Reviews %"], product_details["Neutral Reviews %"]
        ))
        connection.commit()
        cursor.close()
        connection.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    except Exception as e:
        print(f"Exception: {e}")

# Function to scrape reviews
def scrape_reviews(link):
    Reviews_Page_URL = [f"https://www.flipkart.com{link}&page={i}" for i in range(1, 11)]
    Buyer_Name = []
    Rating = []
    Comment = []

    for page_url in Reviews_Page_URL:
        options = Options()
        options.add_argument("--headless")  # Run the browser in headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--disable-gpu")
        
        # Set up ChromeDriver with webdriver-manager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(page_url)
        time.sleep(2)  # Let the page load
        scrolls = 3
        for _ in range(scrolls):
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(2)
        Page = driver.page_source
        driver.quit()
        Reviews_HTML = bs(Page, 'html.parser')

        for name in Reviews_HTML.find_all("p", {"class": "_2NsDsF AwS1CA"}):
            Buyer_Name.append(name.text)

        for rating_section in Reviews_HTML.find_all("div", {"class": "cPHDOP col-12-12"})[3:-1]:
            first_class = rating_section.find("div", {"class": "XQDdHH Js30Fc Ga3i8K"})
            second_class = rating_section.find("div", {"class": "XQDdHH Ga3i8K"})
            third_class = rating_section.find("div", {"class": "XQDdHH Czs3gR Ga3i8K"})
            if first_class:
                Rating.append(int(first_class.text))
            elif second_class:
                Rating.append(int(second_class.text))
            elif third_class:
                Rating.append(int(third_class.text))

        for comment in Reviews_HTML.find_all("div", {"class": "ZmyHeo"}):
            Comment.append(comment.div.div.text)

    return pd.DataFrame({"Name": Buyer_Name, "Rating": Rating, "Comment": Comment})

# Function to clean text
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text)
    filtered_tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(filtered_tokens)

# Function to perform sentiment analysis using NLTK
def get_sentiment(text, sia):
    sentiment = sia.polarity_scores(text)
    if sentiment['compound'] >= 0.05:
        return 'positive'
    elif sentiment['compound'] <= -0.05:
        return 'negative'
    else:
        return 'neutral'

# Function to classify sentiment using the Huggingface pipeline
def classify_sentiment(text, sentiment_pipeline):
    result = sentiment_pipeline(text)
    return result[0]['label']

# Main function to handle the entire process
def analyze_flipkart_reviews(link):
    # Step 1: Scrape the reviews
    df = scrape_reviews(link)

    # Step 2: Clean the review comments
    df['cleaned_review'] = df['Comment'].apply(clean_text)

    # Step 3: Tokenize cleaned reviews
    df['tokens'] = df['cleaned_review'].apply(word_tokenize)

    # Step 4: Initialize sentiment analyzers
    sia = SentimentIntensityAnalyzer()
    sentiment_pipeline = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')

    # Step 5: Perform sentiment analysis
    df['sentiment'] = df['Comment'].apply(lambda x: classify_sentiment(x, sentiment_pipeline))

    # Step 6: Calculate the percentages of sentiment
    positive_review_percentage = round(((df[df['sentiment'] == 'POSITIVE'].shape[0]) / df.shape[0]) * 100, 2)
    negative_review_percentage = round(((df[df['sentiment'] == 'NEGATIVE'].shape[0]) / df.shape[0]) * 100, 2)
    neutral_review_percentage = round(((df[df['sentiment'] == 'NEUTRAL'].shape[0]) / df.shape[0]) * 100, 2)

    return {
        "Positive Reviews %": positive_review_percentage,
        "Negative Reviews %": negative_review_percentage,
        "Neutral Reviews %": neutral_review_percentage,
    }

app = Flask(__name__)
CORS(app)  # Enable CORS for your app

# Create a route for the index page
@app.route('/', methods=['GET'])
@cross_origin()
def home_page():
    return render_template('index.html')

# Create a route for your API
@app.route('/scrape_product', methods=['POST', 'GET'])
@cross_origin()
def scrape_product():
    try:
        if request.method == 'POST':
            Product_URL = request.form['Product URL']
            Detail = scrape_product_details(Product_URL=Product_URL)
            results = analyze_flipkart_reviews(Detail['Link'])
            
            # Product Details 
            Product_Details_List = {
                "Product URL": Product_URL,
                "Product Name": Detail['Product Name'],
                "Product Image": Detail['Product Image'],
                "Original Price": Detail['Original Price'],
                "Discount %": Detail['Discount %'],
                "Special Price": Detail['Special Price'],
                "Overall Rating": Detail['Rating'],
                "Total Ratings": Detail['Total Number of Ratings'],
                "Total Reviews": Detail['Total Number of Reviews'],
                "Expected Delivery Date": Detail['Delivery Date'],
                "Seller Name": Detail['Seller Name'],
                "Seller Rating": Detail['Seller Rating'],
                "Positive Reviews %": results['Positive Reviews %'],
                "Negative Reviews %": results['Negative Reviews %'],
                "Neutral Reviews %": results['Neutral Reviews %']
            }
            
            # Save product details to MySQL
            save_to_mysql(Product_Details_List)
            
            # Render the report.html with product details
            return render_template('report.html', product=Product_Details_List)
        
        return render_template('index.html')
    
    except Exception as e:
        return f"An error occurred: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
