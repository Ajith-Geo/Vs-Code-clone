import asyncio
import time
from playwright.async_api import async_playwright
# import gemini

async def flipkart(url: str):
    async with async_playwright() as p:
        start = time.time()
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
        await page.goto(url=url, timeout=60000, wait_until='load')
        priceTitle = await price_title(page)
        partial = await page.locator('//html/body/div[1]/div/div[3]/div[1]/div[2]/div[7]/div[5]/div/a').get_attribute('href')
        comp_url = "https://www.flipkart.com" + partial
        reviews = await review_scrapper(page, comp_url,browser)
        await browser.close()
        stop = time.time()
        print(stop-start)
        return {
            'priceTitle': priceTitle,
            'reviews': reviews
        }

async def price_title(page: object):
    try:
        title = await page.locator('//html/body/div[1]/div/div[3]/div[1]/div[2]/div[2]/div/div[1]/h1/span').inner_text()
        if await page.locator('//html/body/div[1]/div/div[3]/div[1]/div[2]/div[2]/div/div[4]/div[1]/div/div[1]').is_visible():
            price = await page.locator('//html/body/div[1]/div/div[3]/div[1]/div[2]/div[2]/div/div[4]/div[1]/div/div[1]').inner_text()
        else:
            price = await page.locator('//html/body/div[1]/div/div[3]/div[1]/div[2]/div[2]/div/div[3]/div[1]/div/div[1]').inner_text()
        if "," in price or '₹' in price:
            price = (price.replace(',', '')).replace('₹', '')
        price = int(price)
        return [price, title]

    except Exception as e:
        print(e)

async def scrape_page_reviews(page, comp_url, i,browser):
    try:
        # Navigate to the review page i
        page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
        await page.goto(comp_url + f'&page={i}', wait_until='load', timeout=60000)
        lis = await page.locator('.ZmyHeo').all()
        reviews = []
        for j in range(len(lis)):
            review = await lis[j].locator('//div/div').inner_text()
            reviews.append(review)
        return reviews
    except Exception as e:
        print(e)
        return []

async def review_scrapper(page: object, comp_url: str,browser: object):
    try:
        review_count = await page.locator('//html/body/div[1]/div/div[3]/div[1]/div[2]/div[7]/div[5]/div/div[2]/div[1]/div/div[1]/div/div[3]/div/span').inner_text()
        count = int((review_count.split(' '))[0])
        num_of_pages = count // 10 + 1

        # Create tasks for scraping reviews from multiple pages concurrently
        tasks = [scrape_page_reviews(page, comp_url, i,browser) for i in range(1, num_of_pages + 1)]
        
        # Run all the tasks concurrently and gather results
        results = await asyncio.gather(*tasks)

        # Flatten the list of lists into a single list of reviews
        all_reviews = [review for sublist in results for review in sublist]
        return all_reviews

    except Exception as e:
        print(e)

# Run the flipkart function with asyncio
url = "https://www.flipkart.com/iqoo-z9s-pro-5g-luxe-marble-128-gb/p/itm2f76190f198f6?pid=MOBH42A5GHBGGMFY&lid=LSTMOBH42A5GHBGGMFYZ6HFZC&marketplace=FLIPKART&cmpid=content_mobile_8965229628_gmc"
output = asyncio.run(flipkart(url))
print(output)
