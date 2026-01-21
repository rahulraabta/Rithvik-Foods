# Rithvik Foods

Rithvik Foods is a static e-commerce website designed to showcase and sell authentic, homemade Indian masala powders and spices. The website features a user-friendly interface for browsing products, managing a shopping cart, and placing orders via WhatsApp.

## Features

-   **Responsive Design**: Optimized for both desktop and mobile devices, featuring a custom mobile navigation menu.
-   **Product Catalog**: Categorized display of products (Health Powder, Premix, Masala Powder, Chutney Powder, and Combo Offers).
-   **Shopping Cart**:
    -   Add products with adjustable quantities.
    -   View cart summary with subtotal and shipping calculations.
    -   Persistent cart storage using `localStorage`.
-   **User Authentication (Simulated)**:
    -   Sign Up and Login functionality using `localStorage` as a database.
    -   Session management for user details.
    -   Order history tracking for logged-in users.
-   **Order Processing**:
    -   Checkout form with validation.
    -   Integration with **WhatsApp** to send pre-formatted order details directly to the business owner.
    -   Integration with **Google Sheets** (via Google Apps Script) for backend order logging.
-   **Payment Integration**:
    -   Support for Cash on Delivery (COD).
    -   QR Code generation for UPI payments during checkout.

## Technologies Used

-   **HTML5**: Semantic structure of the application.
-   **CSS3**: Custom styling, variables, flexbox/grid layouts, and responsive media queries.
-   **JavaScript (Vanilla)**: DOM manipulation, cart logic, state management, and API interactions.
-   **LocalStorage**: Client-side data persistence for users, cart, and order history.
-   **Google Apps Script**: Used as a lightweight backend for logging orders to Google Sheets.

## Project Structure

```
.
├── index.html              # Main application file containing structure and logic
├── main.css                # Global stylesheets and responsive definitions
├── GITHUB_INSTRUCTIONS.md  # Instructions for pushing the code to GitHub
├── logo_v3.webp            # Website Logo
├── hero-bg.png             # Hero section background image
└── *.webp / *.png          # Product images (e.g., cat_health.webp, ragi_premix.webp)
```

## Setup and Usage

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/rithvik-foods.git
    ```
2.  **Open the project:**
    Navigate to the project folder and open `index.html` in any modern web browser.
    ```bash
    cd rithvik-foods
    # On macOS
    open index.html
    # On Linux
    xdg-open index.html
    # On Windows
    start index.html
    ```

## Customization

-   **Product Data**: Products are currently hardcoded in the HTML structure. To modify products, edit the `Product-card` divs within the `#products` section in `index.html`.
-   **Contact Info**: Update the phone number and links in the `addToCart` and `submitOrder` functions in `index.html` to redirect to your own WhatsApp number.
-   **Backend**: The Google Sheets integration uses a specific deployment URL. You will need to set up your own Google Apps Script and update the `scriptURL` variable in `index.html`.

## License

This project is available for personal and educational use.
