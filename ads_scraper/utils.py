def clean_data(ad_info):
    """Clean and format ad data."""
    # Example cleaning function (you can add more data cleaning logic as needed)
    ad_info['Description'] = ad_info['Description'].replace('\n', ' ').strip()
    return ad_info
