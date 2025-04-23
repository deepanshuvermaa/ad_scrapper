from flask import Flask, jsonify, request, send_file, render_template
from ads_scraper.scraper import extract_facebook_ad_data
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from datetime import datetime
import os

app = Flask(__name__)

def save_to_excel(ad_data, filename=None):  
    """Save ad data to Excel with embedded image URLs and video URLs."""
    if not ad_data:
        return None

    if not filename:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"facebook_ads_data_{timestamp}.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = "Facebook Ads"

    headers = ['Library ID', 'Description', 'Image URL', 'Video URL', 'Backlink URL']
    ws.append(headers)

    column_widths = [33, 50, 65, 45, 45]
    for i, width in enumerate(column_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = width

    for ad in ad_data:
        image_url = ad.get('Image URL', '')
        video_url = ad.get('Video URL', '')
        backlink_url = ad.get('Backlink URL', '')

        row = [
            ad.get('Library ID', ''),
            ad.get('Description', ''),
            image_url,
            video_url,
            backlink_url
        ]
        ws.append(row)

    file_path = f"./{filename}"
    wb.save(file_path)
    return file_path


@app.route('/')
def home():
    # Render the HTML form for URL input
    return render_template('index.html')


@app.route('/scrape', methods=['POST'])
def scrape_ads():
    # Get the URL parameter from the form
    url = request.form.get('url')
    
    if not url:
        return jsonify({"error": "Please provide a URL parameter"}), 400

    # Extract ad data using the scraper
    ad_data = extract_facebook_ad_data(url)
    
    if ad_data:
        filename = save_to_excel(ad_data)
        
        if filename:
            # Return the generated Excel file as a downloadable file
            return send_file(filename, as_attachment=True)
        else:
            return jsonify({"error": "Failed to generate Excel file"}), 500
    else:
        return jsonify({"error": "No data was extracted"}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.getenv('PORT', 5000))
