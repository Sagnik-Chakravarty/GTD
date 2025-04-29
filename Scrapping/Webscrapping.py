import time
from re import search, IGNORECASE, compile
import pandas as pd
from playwright.sync_api import sync_playwright
from beepy import beep

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


def washingtonpost_data(search_term, filter_date):
    url = 'https://www.washingtonpost.com/search/?query=' + '+'.join(search_term.split(sep=' '))
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(java_script_enabled=True)
        page = context.new_page()

        # Navigate to the target URL
        page.goto(url)

        # Check if "Load more results" button exists
        try:
            page.wait_for_selector('text=Load more results', timeout=60000)
            next_button = page.locator('text=Load more results')

            # Loop to click the button until it's no longer visible
            while next_button.is_visible():
                try:
                    next_button.scroll_into_view_if_needed()
                    next_button.click()
                    time.sleep(2)  # Wait for new content to load
                except Exception as e:
                    print(f"An error occurred while clicking: {e}")
                    break
        except Exception as e:
            print(f"'Load more results' button not found: {e}")

        # Locate elements for headlines, snippets, dates, and links
        headline_element = page.locator('h2.wpds-c-ggDmLr')
        snippet_date_element = page.locator('div.wpds-c-cywVJb')
        link_element = page.locator('a.wpds-c-EDbBA')

        # Initialize lists to store results
        headlines = []
        snippets = []
        dates = []
        links = []

        # Iterate through all located elements and extract data
        for i in range(headline_element.count()):
            try:
                headline = headline_element.nth(i).text_content().strip()

                # Extract snippet and date from the same parent div
                snippet_date_div = snippet_date_element.nth(i)
                snippet = snippet_date_div.locator('span.wpds-c-fnfACo').text_content().strip()
                date = snippet_date_div.locator('span:nth-child(2)').text_content().strip()

                link = link_element.nth(i).get_attribute('href')

                headlines.append(headline)
                snippets.append(snippet)
                dates.append(date)
                links.append(link)
            except Exception as e:
                print(f"Error processing item {i}: {e}")

        # Create a DataFrame from the extracted data
        df = pd.DataFrame({'headline': headlines, 'snippet': snippets, 'date': dates, 'link': links})
        
        # Convert 'date' column to datetime, handling invalid values
        df['date'] = pd.to_datetime(df['date'], format='%B %d, %Y', errors='coerce')

        # Drop rows with invalid dates
        df = df.dropna(subset=['date'])

        # Add the keyword column
        df['keyword'] = search_term

        # Filter and sort the DataFrame
        filter_df = df[df['date'].dt.year >= filter_date]
        df = filter_df.sort_values(by=['date'])

        context.close()
        browser.close()

        return df


# List of keywords
keyword = [
    "Terrorism",
    "Terrorist attack",
    "Militant group",
    "Insurgent",
    "Freedom fighter",
    "Political violence",
    "Civilian casualties",
    "State crackdown",
    "Repression",
    "Extremist group",
    "Radicalization",
    "Armed conflict",
    "Insurgency",
    "State-sponsored violence",
    "Human rights violations",
    "Terrorist organization",
    "Violence against civilians",
    "Revolutionary movement",
    "Security forces",
    "Counter-terrorism operations",
    "War on terror"
]

# # Combine all data into a single DataFrame
# combined_df = pd.DataFrame()

# for key in keyword:
#     print(f"Processing keyword: {key}")
#     df = washingtonpost_data(key, 1970)
#     combined_df = pd.concat([combined_df, df], ignore_index=True)

# # Save the combined DataFrame to a single CSV file
# combined_df.to_csv('washingtonpost_combined.csv', index=False)
# print("Data saved to 'washingtonpost_combined.csv'")

def article_scrape(df_links,
                   element,
                   filename,
                   headless_state=False,
                   script_state=False,
                   sleep_time=0.5):
    """
    Scrape articles from a list of links using Playwright.

    Parameters:
        df_links (list): List of URLs to scrape.
        element (str): CSS selector for the article body.
        filename (str): Name of the output CSV file (without extension).
        headless_state (bool): Whether to run the browser in headless mode.
        script_state (bool): Enable or disable JavaScript execution.
        sleep_time (float): Time to wait between requests in seconds.

    Returns:
        pd.DataFrame: DataFrame containing scraped articles and their corresponding links.
    """
    with sync_playwright() as p:
        # Launch browser and create context
        browser = p.chromium.launch(headless=headless_state)
        context = browser.new_context(java_script_enabled=script_state)
        page = context.new_page()

        # Initialize DataFrame with predefined columns
        df_art = pd.DataFrame(columns=['article', 'links'])

        for link in df_links:
            time.sleep(sleep_time)
            try:
                # Navigate to the link
                page.goto(link, timeout=30000)  # Adjust timeout as needed
                page.wait_for_selector(element, timeout=10000)  # Wait for the element
                time.sleep(sleep_time)
                # Extract all matching elements
                article_elements = page.query_selector_all(element)
                articles = [art.text_content().strip() for art in article_elements]

                # Create a DataFrame with one row per article
                df = pd.DataFrame({'article': '\n'.join(articles), 'links': [link]})

                # Concatenate results into the main DataFrame
                df_art = pd.concat([df_art, df], ignore_index=True)

            except Exception as e:
                print(f"Error scraping link: {link}")
                print(f"Exception: {e}")

                # Append a row with None for failed links
                df_failed = pd.DataFrame({'article': [None], 'links': [link]})
                df_art = pd.concat([df_art, df_failed], ignore_index=True)

        # Close browser and context
        context.close()
        browser.close()

        # Save results to CSV
        output_filename = f"{filename}_art.csv"
        df_art.to_csv(output_filename, index=False)

        print(f"Scraping completed. Results saved to {output_filename}")
        beep(sound = 'success')

        return df_art
    
# df = pd.read_csv('washingtonpost_combined.csv')
# df_art = article_scrape(df['link'],
#                         filename='washingtonpost_combined_articles',
#                         element = 'div.wpds-c-PJLV.article-body',
#                         sleep_time=0.5)
# pd.merge(df, df_art, on='links', how='left').drop('link', axis=1).to_csv('washingtonpost_combined_articles.csv', index=False)

def al_jazeera(key):
    url = "https://www.aljazeera.com/search/" + '%20'.join(key.split(sep=' ')) + "/"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(java_script_enabled=True)
        page = context.new_page()

        try:
            print(f"Navigating to URL: {url}")
            page.goto(url, timeout=60000)
            time.sleep(2)

            # Click on the "Show more" button until it is no longer visible
            try:
                page.wait_for_selector('button[data-testid="show-more-button"]', timeout=60000)
                while True:
                    try:
                        load_more_button = page.locator('button[data-testid="show-more-button"]')
                        if load_more_button.is_visible():
                            load_more_button.click()
                            time.sleep(2)  # Wait for new content to load
                        else:
                            break
                    except Exception as e:
                        print(f"Error clicking 'Show more' button: {e}")
                        break
            except Exception as e:
                print(f"'Show more' button not found: {e}")

            # Extract headlines, links, dates, and snippets
            try:
                headline_elements = page.locator('h3.gc__title a')
                headlines = headline_elements.all_text_contents()
                links = headline_elements.evaluate_all("elements => elements.map(el => el.href)")
            except Exception as e:
                print(f"Error extracting headlines or links: {e}")
                headlines, links = [], []

            try:
                date_elements = page.locator('div.gc__date span[aria-hidden="true"]')
                dates = date_elements.all_text_contents()
            except Exception as e:
                print(f"Error extracting dates: {e}")
                dates = []

            try:
                snippet_elements = page.locator('div.gc__excerpt p')
                snippets = snippet_elements.all_text_contents()
            except Exception as e:
                print(f"Error extracting snippets: {e}")
                snippets = []

            # Align the lengths of the lists
            max_length = max(len(headlines), len(links), len(dates), len(snippets))
            headlines += [None] * (max_length - len(headlines))
            links += [None] * (max_length - len(links))
            dates += [None] * (max_length - len(dates))
            snippets += [None] * (max_length - len(snippets))

            # Create a DataFrame from the extracted data
            df = pd.DataFrame({
                'headline': headlines,
                'link': links,
                'date': dates,
                'snippet': snippets,
                'keyword': key
            })

        finally:
            context.close()
            browser.close()

        return df

# combined_df = pd.DataFrame()
# for key in keyword:
#     try:
#         print(f"Processing keyword: {key}")
#         df = al_jazeera(key)
#         if not df.empty:
#             combined_df = pd.concat([combined_df, df], ignore_index=True)
#         else:
#             print(f"No data found for keyword: {key}")
#     except Exception as e:
#         print(f"Error processing keyword '{key}': {e}")

# # Remove duplicates before saving
# combined_df = combined_df.drop_duplicates()

# # Save the combined DataFrame to a CSV file
# combined_df.to_csv('aljazeera_combined.csv', index=False)
# print("Data saved to 'aljazeera_combined.csv'")

def reuters(key):
    i = 0
    combined_df = pd.DataFrame()  # Initialize an empty DataFrame to store results
    while True:
        url = "https://www.reuters.com/site-search/?query=" + '+'.join(key.split(sep=' ')) + "&offset=" + str(i)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(java_script_enabled=True)
            page = context.new_page()

            try:
                print(f"Navigating to URL: {url}")
                page.goto(url, timeout=60000)
                time.sleep(2)

                # Extract headlines and links
                try:
                    headline_elements = page.locator('div.title__title__29EfZ a[data-testid="TitleLink"]')
                    headlines = headline_elements.all_text_contents()  # Extract headline text
                    links = headline_elements.evaluate_all("elements => elements.map(el => el.href)")  # Extract links
                except Exception as e:
                    print(f"Error extracting headlines or links: {e}")
                    headlines, links = [], []

                # Extract dates
                try:
                    date_elements = page.locator('span.SearchResults_date')  # Update this selector if needed
                    dates = date_elements.all_text_contents()
                except Exception as e:
                    print(f"Error extracting dates: {e}")
                    dates = []

                # Extract snippets
                try:
                    snippet_elements = page.locator('p.SearchResults_snippet')  # Update this selector if needed
                    snippets = snippet_elements.all_text_contents()
                except Exception as e:
                    print(f"Error extracting snippets: {e}")
                    snippets = []

                # Align the lengths of the lists
                max_length = max(len(headlines), len(links), len(dates), len(snippets))
                headlines += [None] * (max_length - len(headlines))
                links += [None] * (max_length - len(links))
                dates += [None] * (max_length - len(dates))
                snippets += [None] * (max_length - len(snippets))

                # Create a DataFrame from the extracted data
                df = pd.DataFrame({
                    'headline': headlines,
                    'link': links,
                    'date': dates,
                    'snippet': snippets,
                    'keyword': key
                })

                # Append the current DataFrame to the combined DataFrame
                combined_df = pd.concat([combined_df, df], ignore_index=True)

                # Check if there are no more results to load
                if len(headlines) == 0:
                    print("No more results found. Exiting loop.")
                    break

                # Increment the offset for the next page
                i += 20

            except Exception as e:
                print(f"Error processing URL: {url}")
                print(f"Exception: {e}")
                break

            finally:
                context.close()
                browser.close()

    # Save the combined DataFrame to a CSV file
    file_name = f"reuters_{key.replace(' ', '_')}.csv"
    combined_df.to_csv(file_name, index=False)
    print(f"Data saved to {file_name}")

    return combined_df

combined_df = pd.DataFrame()
for key in keyword:
    try:
        print(f"Processing keyword: {key}")
        df = reuters(key)
        if not df.empty:
            combined_df = pd.concat([combined_df, df], ignore_index=True)
        else:
            print(f"No data found for keyword: {key}")
    except Exception as e:
        print(f"Error processing keyword '{key}': {e}")

# Remove duplicates before saving
combined_df = combined_df.drop_duplicates()
# Save the combined DataFrame to a CSV file
combined_df.to_csv('reuters_combined.csv', index=False)
print("Data saved to 'reuters_combined.csv'")