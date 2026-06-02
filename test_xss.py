import asyncio
import sys

async def run():
    print("Test started")
    try:
        from playwright.async_api import async_playwright
        print("Imported playwright")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            # Flag to detect alert
            alert_triggered = False

            def handle_dialog(dialog):
                nonlocal alert_triggered
                print(f"Alert triggered with message: {dialog.message}")
                if "XSS" in dialog.message:
                    alert_triggered = True
                asyncio.create_task(dialog.accept())

            page.on("dialog", handle_dialog)

            print("Navigating to local server...")
            await page.goto("http://localhost:8000/index.html")

            print("Injecting XSS payload into cart in localStorage...")
            payload = "<img src=x onerror=alert('XSS')>"
            # Add item to cart and login as guest user to show checkout summary
            await page.evaluate(f"""() => {{
                localStorage.setItem('rithvik_cart_test@example.com', JSON.stringify([{{
                    name: "{payload}",
                    price: 100,
                    qty: 1
                }}]));
                localStorage.setItem('rithvik_current_user', JSON.stringify({{
                    id: '123',
                    name: 'Test',
                    email: 'test@example.com',
                    phone: '1234567890',
                    password: 'pass'
                }}));
            }}""")

            await page.reload()

            # Wait for reload to complete
            await page.wait_for_load_state('networkidle')

            # Open the checkout summary by calling the JS function
            print("Opening checkout modal...")
            await page.evaluate("openOrderModal()")

            # Wait a brief moment for the modal to render and any alerts to fire
            await asyncio.sleep(2)

            if alert_triggered:
                print("VULNERABILITY DETECTED: XSS alert was triggered.")
                await browser.close()
                sys.exit(1)

            print("Checking if the payload is rendered as text...")

            # Check if the payload is rendered as text
            summary_text = await page.locator('#checkoutSummary').inner_text()
            print(f"Summary text: {summary_text}")

            if payload in summary_text:
                print("SUCCESS: Payload rendered as text safely. Vulnerability fixed.")
                await browser.close()
                sys.exit(0)
            else:
                print("WARNING: Payload not found in summary text. Manual verification needed.")
                await browser.close()
                sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run())
