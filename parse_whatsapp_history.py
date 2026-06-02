import re
import csv
import os

def parse_whatsapp_chat(file_path):
    print(f"Reading chat history from {file_path}...")
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found! Please place your exported WhatsApp chat text file at: {os.path.abspath(file_path)}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split the file by WhatsApp message headers
    # Matches patterns like:
    # [02/06/26, 11:44:04] Name:
    # 02/06/26, 11:44 - Name:
    message_pattern = re.compile(
        r'(?:\r?\n|^)(?:\[?(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)[\]\s]*-\s*|(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)\s*-\s*([^:]+):\s*|\[?(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)[\]\s]*([^:]+):\s*)'
    )
    
    # We will use a simpler approach: split by lines and accumulate messages
    lines = content.split('\n')
    messages = []
    current_msg = {"date": "", "time": "", "text": ""}
    
    # Check if line starts with a date pattern
    # e.g., "[02/06/26, 11:44:04]" or "02/06/26, 11:44 - "
    date_regex = re.compile(r'^\[?(\d{1,2}/\d{1,2}/\d{2,4})[,\s]+(\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)[\]\s-]*')

    for line in lines:
        match = date_regex.match(line)
        if match:
            # If we had a previous message, save it
            if current_msg["text"]:
                messages.append(current_msg)
            
            # Clean message text line (remove header)
            header_len = match.end()
            msg_body = line[header_len:]
            # If there's a sender (e.g. "Rithvik Foods: "), strip it
            sender_match = re.match(r'^([^:]+):\s*', msg_body)
            if sender_match:
                msg_body = msg_body[sender_match.end():]
                
            current_msg = {
                "date": match.group(1),
                "time": match.group(2),
                "text": msg_body
            }
        else:
            if current_msg["text"]:
                current_msg["text"] += "\n" + line
            else:
                current_msg["text"] = line
                
    if current_msg["text"]:
        messages.append(current_msg)

    print(f"Parsed {len(messages)} total messages. Scanning for order requests...")

    orders = []
    order_items = []
    customers = {}

    for msg in messages:
        text = msg["text"]
        # Look for messages containing "*New Order Request*"
        if "*New Order Request*" in text or "New Order Request" in text:
            # Parse Order ID
            order_id_match = re.search(r'ID:\s*([A-Z0-9\-]+)', text)
            order_id = order_id_match.group(1) if order_id_match else "RF-" + msg["date"].replace("/", "") + msg["time"].replace(":", "").replace(" ", "")[:4]

            # Parse Customer ID
            cust_id_match = re.search(r'Customer ID:\*\s*(\w+)', text)
            cust_id = cust_id_match.group(1) if cust_id_match else "GUEST"

            # Parse Payment
            payment_match = re.search(r'Payment:\*\s*([^\n]+)', text)
            payment = payment_match.group(1) if payment_match else "Unknown"

            # Parse Customer Details
            name_match = re.search(r'Name:\s*([^\n]+)', text, re.IGNORECASE)
            phone_match = re.search(r'Phone:\s*([^\n]+)', text, re.IGNORECASE)
            address_match = re.search(r'Address:\s*([^\n]+)', text, re.IGNORECASE)
            delivery_match = re.search(r'(?:Pref\. Delivery|Delivery):\s*([^\n]+)', text, re.IGNORECASE)

            name = name_match.group(1).strip() if name_match else "Unknown"
            phone = phone_match.group(1).strip() if phone_match else ""
            address = address_match.group(1).strip() if address_match else ""
            delivery_date = delivery_match.group(1).strip() if delivery_match else ""

            # Parse Financials
            subtotal_match = re.search(r'Subtotal:\*\s*₹?\s*(\d+)', text, re.IGNORECASE)
            shipping_match = re.search(r'Shipping:\*\s*₹?\s*(\d+)', text, re.IGNORECASE)
            total_match = re.search(r'(?:Grand Total|Total):\*\s*₹?\s*(\d+)', text, re.IGNORECASE)

            subtotal = float(subtotal_match.group(1)) if subtotal_match else 0.0
            shipping = float(shipping_match.group(1)) if shipping_match else 0.0
            total = float(total_match.group(1)) if total_match else 0.0

            # Parse Items
            # Items section is between "*Items:*" and "*Subtotal:*" or "*Customer Details:*"
            items_section_match = re.search(r'\*Items:\*\s*\n(.*?)(?=\n\*Subtotal|\n\*Customer Details|\nName:|\Z)', text, re.DOTALL | re.IGNORECASE)
            
            item_count = 0
            parsed_items = []
            if items_section_match:
                items_text = items_section_match.group(1)
                # Find each item (e.g. "1. Amla Juice Powder (x2) - ₹318")
                # Pattern: digit. Item Name (xQuantity) - Price
                item_lines = items_text.strip().split('\n')
                for line in item_lines:
                    line = line.strip()
                    if not line:
                        continue
                    # Remove list number if present
                    line_clean = re.sub(r'^\d+[\.\)\s]+', '', line).strip()
                    # Match quantity in parenthesis
                    qty_match = re.search(r'\(x(\d+)\)', line_clean)
                    qty = int(qty_match.group(1)) if qty_match else 1
                    
                    # Match item total price
                    price_match = re.search(r'(?:-|₹)\s*₹?\s*(\d+)', line_clean)
                    item_total = float(price_match.group(1)) if price_match else 0.0
                    
                    # Clean item name
                    item_name = re.sub(r'\s*\(x\d+\).*', '', line_clean).strip()
                    unit_price = item_total / qty if qty > 0 else item_total
                    
                    item_count += qty
                    parsed_items.append({
                        "name": item_name,
                        "qty": qty,
                        "unit_price": unit_price,
                        "total": item_total
                    })

            # If no items found but we have total, add fallback item
            if not parsed_items and total > 0:
                parsed_items.append({
                    "name": "Generic Order Item",
                    "qty": 1,
                    "unit_price": total - shipping,
                    "total": total - shipping
                })
                item_count = 1

            date_str = f"{msg['date']} {msg['time']}"

            # Append to Orders
            orders.append({
                "Date": date_str,
                "Order ID": order_id,
                "Customer ID": custId,
                "Customer Name": name,
                "Phone": phone,
                "Address": address,
                "Delivery Date": delivery_date,
                "Subtotal": subtotal if subtotal > 0 else (total - shipping),
                "Shipping": shipping,
                "Total": total,
                "Item Count": item_count,
                "Payment Mode": payment,
                "Order Status": "Placed"
            })

            # Append to Order Items
            for item in parsed_items:
                order_items.append({
                    "Date": date_str,
                    "Order ID": order_id,
                    "Item Name": item["name"],
                    "Quantity": item["qty"],
                    "Unit Price": item["unit_price"],
                    "Item Total": item["total"]
                })

            # Append/Update Customers
            phone_clean = re.sub(r'\D', '', phone)
            if phone_clean:
                if phone_clean in customers:
                    customers[phone_clean]["Total Orders"] += 1
                    customers[phone_clean]["Total Spent"] += total
                    customers[phone_clean]["Last Order Date"] = date_str
                    # Update details if they were empty
                    if name and customers[phone_clean]["Customer Name"] == "Unknown":
                        customers[phone_clean]["Customer Name"] = name
                    if address and not customers[phone_clean]["Address"]:
                        customers[phone_clean]["Address"] = address
                else:
                    customers[phone_clean] = {
                        "Customer ID": custId,
                        "Customer Name": name,
                        "Phone": phone,
                        "Address": address,
                        "Last Order Date": date_str,
                        "Total Orders": 1,
                        "Total Spent": total
                    }

    # Write CSV Files
    write_csv("orders_import.csv", ["Date", "Order ID", "Customer ID", "Customer Name", "Phone", "Address", "Delivery Date", "Subtotal", "Shipping", "Total", "Item Count", "Payment Mode", "Order Status"], orders)
    write_csv("order_items_import.csv", ["Date", "Order ID", "Item Name", "Quantity", "Unit Price", "Item Total"], order_items)
    write_csv("customers_import.csv", ["Customer ID", "Customer Name", "Phone", "Address", "Last Order Date", "Total Orders", "Total Spent"], list(customers.values()))

    print("\nParsing Complete!")
    print(f"Extracted {len(orders)} orders, {len(order_items)} items, and {len(customers)} customer profiles.")
    print("CSV files generated successfully:")
    print("1. orders_import.csv")
    print("2. order_items_import.csv")
    print("3. customers_import.csv")
    print("\nYou can now open Google Sheets and import these CSV files into their respective sheets!")

def write_csv(filename, headers, rows):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            # Format phone number for csv to prevent Excel stripping leading zeroes
            if "Phone" in row and row["Phone"]:
                row["Phone"] = f"'{row['Phone']}"
            writer.writerow(row)

if __name__ == "__main__":
    import sys
    chat_file = "whatsapp_history.txt"
    if len(sys.argv) > 1:
        chat_file = sys.argv[1]
    parse_whatsapp_chat(chat_file)
