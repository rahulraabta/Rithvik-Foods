# Google Apps Script Code

Please copy the following code into your Google Apps Script project (Extensions > Apps Script in your Google Sheet).

**IMPORTANT:**
1.  After pasting, Save the project.
2.  Click **Deploy** > **New deployment**.
3.  Select type: **Web app**.
4.  Execute as: **Me**.
5.  Who has access: **Anyone** (this is critical for the website to send data).
6.  Click **Deploy** and copy the **Web App URL**.
7.  **Ensure your Google Sheet HEADER ROW (Row 1) has these exact columns:**
    `Date`, `Order ID`, `Customer ID`, `Name`, `Phone`, `Address`, `City`, `State`, `Zip`, `Delivery Date`, `Items`, `Total`, `Item Count`, `Payment Mode`, `Order Status`

```javascript
// SHEET CONFIGURATION
var SHEET_NAME = "Sheet1"; // Change if your sheet name is different

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.tryLock(10000);

  try {
    var doc = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = doc.getSheetByName(SHEET_NAME);

    // Parse the incoming data
    var data = JSON.parse(e.postData.contents);
    var action = data.action; // 'create' or 'cancel'

    if (action === 'cancel') {
      return handleCancellation(sheet, data);
    } else {
      return handleOrderCreation(sheet, data);
    }

  } catch (e) {
    return ContentService
      .createTextOutput(JSON.stringify({ 'result': 'error', 'error': e }))
      .setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}

function handleOrderCreation(sheet, data) {
  var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  var nextRow = sheet.getLastRow() + 1;
  var newRow = [];

  // Map data to headers
  // We look for specific header names and map the data accordingly
  for (var i = 0; i < headers.length; i++) {
    var header = headers[i].toString().toLowerCase(); // Normalize header name

    switch (header) {
      case 'date':
        newRow.push(data.date || new Date());
        break;
      case 'order id':
        newRow.push(data.orderId || '');
        break;
      case 'customer id':
        newRow.push(data.customerId || '');
        break;
      case 'name':
        newRow.push(data.name || '');
        break;
      case 'phone':
        newRow.push("'" + data.phone || ''); // Force string for phone
        break;
      case 'address':
        newRow.push(data.address || '');
        break;
      case 'delivery date':
        newRow.push(data.deliveryDate || '');
        break;
      case 'items':
        newRow.push(data.items || '');
        break;
      case 'total':
        newRow.push(data.total || 0);
        break;
      case 'item count':
        newRow.push(data.itemCount || 0);
        break;
      case 'payment mode':
        newRow.push(data.paymentMode || '');
        break;
      case 'order status':
        newRow.push('Placed'); // Default status
        break;
      default:
        newRow.push(''); // Empty string for unknown columns
    }
  }

  sheet.appendRow(newRow);

  return ContentService
    .createTextOutput(JSON.stringify({ 'result': 'success', 'row': nextRow }))
    .setMimeType(ContentService.MimeType.JSON);
}

function handleCancellation(sheet, data) {
  var orderId = data.orderId;
  
  if (!orderId) {
    return ContentService
      .createTextOutput(JSON.stringify({ 'result': 'error', 'error': 'No Order ID provided' }))
      .setMimeType(ContentService.MimeType.JSON);
  }

  var dataRange = sheet.getDataRange();
  var values = dataRange.getValues();
  var headers = values[0];
  
  // Find "Order ID" column index
  var orderIdColIndex = -1;
  var statusColIndex = -1;

  for (var i = 0; i < headers.length; i++) {
    var h = headers[i].toString().toLowerCase();
    if (h === 'order id') orderIdColIndex = i;
    if (h === 'order status') statusColIndex = i;
  }

  if (orderIdColIndex === -1 || statusColIndex === -1) {
     return ContentService
      .createTextOutput(JSON.stringify({ 'result': 'error', 'error': 'Columns not found' }))
      .setMimeType(ContentService.MimeType.JSON);
  }

  // Find the row with the matching Order ID
  // Start from row 1 (excluding header row 0)
  for (var i = 1; i < values.length; i++) {
    if (values[i][orderIdColIndex].toString() === orderId.toString()) {
      // Row found (i + 1 because sheets are 1-indexed)
      var rowIndex = i + 1;
      
      // Update status
      sheet.getRange(rowIndex, statusColIndex + 1).setValue('Cancelled');

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
