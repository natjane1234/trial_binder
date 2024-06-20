import asyncio
import nest_asyncio
from pyppeteer import launch
import base64

def screenshot (url, output_filename, output_html):
    html_path = output_html  # Path to your generated HTML file
    nest_asyncio.apply()

    async def capture_full_page_screenshot(url, output_filename):
        browser = await launch(headless=True, args=['--no-sandbox'])
        page = await browser.newPage()

        # Set the viewport size if necessary (optional)
        await page.setViewport({'width': 1280, 'height': 800})

        await page.goto(url)


        # Zoom in by adjusting the page's CSS
        await page.evaluate('''() => {
            document.body.style.zoom = "150%"
        }''')

        # Wait for any dynamic content (optional, adjust as necessary)
        await asyncio.sleep(2)

        # Capture full-page screenshot
        await page.screenshot({'path': output_filename, 'fullPage': True})

        await browser.close()

    # Run the asynchronous function
    asyncio.get_event_loop().run_until_complete(capture_full_page_screenshot(url, output_filename))

    try:
        with open(output_filename, "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
            
    except FileNotFoundError as e:
        print(f"Error: {e}")



