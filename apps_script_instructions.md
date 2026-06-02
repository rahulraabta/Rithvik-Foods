# Google Apps Script Code for Multi-Table Order Processing

Please copy the following code into your Google Apps Script project (Extensions > Apps Script in your Google Sheet).

### **Deployment Instructions:**
1.  Open your Google Sheet.
2.  Click **Extensions** > **Apps Script**.
3.  Delete any existing code in the editor and paste the code below.
4.  Click **Save** (💾 icon).
5.  Click **Deploy** > **New deployment**.
6.  Click the gear icon (Select type) and select **Web app**.
7.  Fill in the configuration details:
    *   **Description:** `Rithvik Foods Multi-Table Orders API`
    *   **Execute as:** `Me` (your account)
    *   **Who has access:** `Anyone` (this allows the website to send order details anonymously)
8.  Click **Deploy**.
9.  Copy the **Web App URL** (ends with `/exec`). It should match this URL format:
    `https://script.google.com/macros/s/AKfycbwbAydCjIAHyEYQ8tbHZ48Qr9f6i3yATirFTwINcDry8RBmxpVXeG74Xamu0LOL0GfA/exec`

---

## 📊 How the Data is Organized in the Google Sheet

The script automatically sets up **3 separate sheets (tables)** inside your Google Spreadsheet to organize order data clean and professionally:

1. **`Orders` Table (Order Summaries):**
   * Storing high-level metadata of each order (one row per order).
   * **Columns:** `Date`, `Order ID`, `Customer ID`, `Customer Name`, `Phone`, `Address`, `Delivery Date`, `Subtotal`, `Shipping`, `Total`, `Item Count`, `Payment Mode`, `Order Status`, `Cancel Token`

2. **`OrderItems` Table (Line Items Breakdown):**
   * Storing individual items inside each order (one row per purchased item). Perfect for inventory checking and packing.
   * **Columns:** `Date`, `Order ID`, `Item Name`, `Quantity`, `Unit Price`, `Item Total`

3. **`Customers` Table (Customer CRM):**
   * Storing customer lists with order histories automatically matched by phone number. Perfect for customer tracking, loyalty programs, and address histories.
   * **Columns:** `Customer ID`, `Customer Name`, `Phone`, `Address`, `Last Order Date`, `Total Orders`, `Total Spent`

---

## 🛠️ Google Apps Script Code

```javascript
// Rithvik Foods Order Processing Backend
// Auto-initializes sheets and columns if they do not exist.

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.tryLock(10000);

  try {
    var doc = SpreadsheetApp.getActiveSpreadsheet();
    
    // Parse the incoming order data
    var data = JSON.parse(e.postData.contents);
    var action = data.action; // 'create' or 'cancel'

    if (action === 'cancel') {
      return handleCancellation(doc, data);
    } else {
      return handleOrderCreation(doc, data);
    }

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ 'result': 'error', 'error': err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}

// Function to initialize sheet with headers if it does not exist
function getOrCreateSheet(doc, sheetName, headers) {
  var sheet = doc.getSheetByName(sheetName);
  if (!sheet) {
    sheet = doc.insertSheet(sheetName);
    sheet.appendRow(headers);
    
    // Style headers
    var headerRange = sheet.getRange(1, 1, 1, headers.length);
    headerRange.setFontWeight("bold");
    headerRange.setBackground("#E8F5E9"); // Very light mint green
    headerRange.setHorizontalAlignment("center");
    headerRange.setBorder(true, true, true, true, true, true);
    sheet.setFrozenRows(1);
  }
  return sheet;
}

function handleOrderCreation(doc, data) {
  var dateStr = data.date || new Date().toLocaleString();
  var orderId = data.orderId || '';
  var custId = data.customerId || 'GUEST';
  var name = data.name || '';
  var phone = data.phone || '';
  var address = data.address || '';
  var deliveryDate = data.deliveryDate || '';
  var subtotal = parseFloat(data.subtotal) || 0;
  var shipping = parseFloat(data.shipping) || 0;
  var total = parseFloat(data.total) || 0;
  var itemCount = parseInt(data.itemCount) || 0;
  var paymentMode = data.paymentMode || '';
  var orderStatus = data.orderStatus || 'Placed';
  var cartItems = data.cartItems || [];

  // 1. Save to "Orders" Sheet
  var ordersHeaders = ['Date', 'Order ID', 'Customer ID', 'Customer Name', 'Phone', 'Address', 'Delivery Date', 'Subtotal', 'Shipping', 'Total', 'Item Count', 'Payment Mode', 'Order Status', 'Cancel Token'];
  var ordersSheet = getOrCreateSheet(doc, 'Orders', ordersHeaders);
  
  var ordersRow = [
    dateStr,
    orderId,
    custId,
    name,
    "'" + phone, // Force text format to prevent stripping leading zeroes or formatting as scientific notation
    address,
    deliveryDate,
    subtotal,
    shipping,
    total,
    itemCount,
    paymentMode,
    orderStatus,
    data.cancelToken || ''
  ];
  ordersSheet.appendRow(ordersRow);

  // 2. Save to "OrderItems" Sheet
  var itemsHeaders = ['Date', 'Order ID', 'Item Name', 'Quantity', 'Unit Price', 'Item Total'];
  var itemsSheet = getOrCreateSheet(doc, 'OrderItems', itemsHeaders);
  
  if (cartItems && cartItems.length > 0) {
    for (var i = 0; i < cartItems.length; i++) {
      var item = cartItems[i];
      var itemRow = [
        dateStr,
        orderId,
        item.name || '',
        parseInt(item.qty) || 0,
        parseFloat(item.price) || 0,
        parseFloat(item.total) || 0
      ];
      itemsSheet.appendRow(itemRow);
    }
  } else if (data.items) {
    // Fallback if structured cartItems is not passed
    itemsSheet.appendRow([
      dateStr,
      orderId,
      data.items.trim(),
      itemCount,
      total - shipping,
      total - shipping
    ]);
  }

  // 3. Save / Update "Customers" Sheet
  var customersHeaders = ['Customer ID', 'Customer Name', 'Phone', 'Address', 'Last Order Date', 'Total Orders', 'Total Spent'];
  var customersSheet = getOrCreateSheet(doc, 'Customers', customersHeaders);
  
  var customersData = customersSheet.getDataRange().getValues();
  var customerRowIndex = -1;
  
  // Find customer by phone match (strip non-digits for comparison)
  var targetPhone = phone.toString().replace(/\D/g, '');
  if (targetPhone !== '') {
    for (var i = 1; i < customersData.length; i++) {
      var storedPhone = customersData[i][2].toString().replace(/\D/g, '');
      if (storedPhone === targetPhone) {
        customerRowIndex = i + 1; // Row numbers are 1-based, array indices are 0-based
        break;
      }
    }
  }

  if (customerRowIndex !== -1) {
    // Update existing customer stats
    var currentOrders = parseInt(customersData[customerRowIndex - 1][5]) || 0;
    var currentSpent = parseFloat(customersData[customerRowIndex - 1][6]) || 0;
    
    customersSheet.getRange(customerRowIndex, 2).setValue(name); // Refresh name
    customersSheet.getRange(customerRowIndex, 4).setValue(address); // Refresh address
    customersSheet.getRange(customerRowIndex, 5).setValue(dateStr); // Update last active date
    customersSheet.getRange(customerRowIndex, 6).setValue(currentOrders + 1); // Increment count
    customersSheet.getRange(customerRowIndex, 7).setValue(currentSpent + total); // Accumulate spending
  } else {
    // Add new customer entry
    var newCustomerRow = [
      custId,
      name,
      "'" + phone,
      address,
      dateStr,
      1,
      total
    ];
    customersSheet.appendRow(newCustomerRow);
  }

  return ContentService
    .createTextOutput(JSON.stringify({ 'result': 'success', 'orderId': orderId }))
    .setMimeType(ContentService.MimeType.JSON);
}

function handleCancellation(doc, data) {
  var orderId = data.orderId;
  var cancelToken = data.cancelToken;
  if (!orderId || !cancelToken) {
    return ContentService
      .createTextOutput(JSON.stringify({ 'result': 'error', 'error': 'Order ID or Cancel Token missing' }))
      .setMimeType(ContentService.MimeType.JSON);
  }

  var ordersSheet = doc.getSheetByName('Orders');
  if (!ordersSheet) {
    return ContentService
      .createTextOutput(JSON.stringify({ 'result': 'error', 'error': 'Orders sheet not found' }))
      .setMimeType(ContentService.MimeType.JSON);
  }

  var values = ordersSheet.getDataRange().getValues();
  var headers = values[0];
  
  var orderIdColIndex = -1;
  var statusColIndex = -1;
  var cancelTokenColIndex = -1;

  for (var i = 0; i < headers.length; i++) {
    var h = headers[i].toString().toLowerCase();
    if (h === 'order id') orderIdColIndex = i;
    if (h === 'order status') statusColIndex = i;
    if (h === 'cancel token') cancelTokenColIndex = i;
  }

  if (orderIdColIndex === -1 || statusColIndex === -1 || cancelTokenColIndex === -1) {
     return ContentService
      .createTextOutput(JSON.stringify({ 'result': 'error', 'error': 'Required columns not found' }))
      .setMimeType(ContentService.MimeType.JSON);
  }

  for (var i = 1; i < values.length; i++) {
    if (values[i][orderIdColIndex].toString() === orderId.toString()) {
      // Verify cancel token matches
      if (values[i][cancelTokenColIndex].toString() !== cancelToken.toString()) {
        return ContentService
          .createTextOutput(JSON.stringify({ 'result': 'error', 'error': 'Unauthorized: Cancel Token mismatch' }))
          .setMimeType(ContentService.MimeType.JSON);
      }

      var rowIndex = i + 1;
      ordersSheet.getRange(rowIndex, statusColIndex + 1).setValue('Cancelled');

      return ContentService
        .createTextOutput(JSON.stringify({ 'result': 'success', 'message': 'Order cancelled' }))
        .setMimeType(ContentService.MimeType.JSON);
    }
  }

  return ContentService
    .createTextOutput(JSON.stringify({ 'result': 'error', 'error': 'Order ID not found' }))
    .setMimeType(ContentService.MimeType.JSON);
}
```
