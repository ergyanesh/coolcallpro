/**
 * Cool Call Pro — /contact form receiver.
 *
 * Appends every contact-form submission to the Google Sheet this script is
 * bound to. Deploy from a PERSONAL Google account (not the coolcallpro.com
 * Workspace, which is being cancelled).
 *
 * SETUP (one time, ~3 minutes)
 * ---------------------------------------------------------------------------
 * 1. Personal Google account → sheets.new → name it "Cool Call Pro — Contact
 *    Form". Leave it empty; the header row is written automatically.
 * 2. In that Sheet: Extensions → Apps Script. Delete the placeholder code,
 *    paste this whole file, Save.
 * 3. Deploy → New deployment → type "Web app":
 *       Description:  Contact form receiver
 *       Execute as:   Me (your personal account)
 *       Who has access: Anyone            <-- REQUIRED. "Anyone with Google
 *                                             account" will silently reject
 *                                             anonymous visitors.
 * 4. Authorize when prompted (it will warn the app is unverified — it's your
 *    own script; continue).
 * 5. Copy the Web app URL. It ends in /exec.
 * 6. Paste it into CONTACT_FORM_ENDPOINT at the top of js/main.js, then
 *    re-minify:  npx --yes terser js/main.js -o js/main.min.js --compress --mangle
 * 7. Commit + push. Live in ~60s.
 *
 * To get an email ping per submission: in the Sheet, Tools → Notification
 * rules → "Notify me when any changes are made" → immediately. Cheaper than
 * putting MailApp.sendEmail in here (no extra quota, no extra auth scope).
 *
 * Re-deploying after an edit: Deploy → Manage deployments → pencil icon →
 * Version: "New version" → Deploy. The /exec URL stays the same. Creating a
 * *new* deployment instead mints a new URL and you'd have to update main.js.
 */

var HEADERS = ['Timestamp', 'First Name', 'Last Name', 'Email', 'ZIP', 'Inquiry Type', 'Message'];

function doPost(e) {
  try {
    // main.js posts JSON as text/plain, which keeps the request "simple" so
    // the browser never fires a CORS preflight Apps Script can't answer.
    var d = JSON.parse(e.postData.contents);
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];

    if (sheet.getLastRow() === 0) {
      sheet.appendRow(HEADERS);
      sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
      sheet.setFrozenRows(1);
    }

    sheet.appendRow([
      new Date(),
      d.firstName || '',
      d.lastName || '',
      d.email || '',
      d.zip || '',
      d.subject || '',
      d.message || ''
    ]);

    return ContentService.createTextOutput('ok');
  } catch (err) {
    // Log and still 200 — the browser can't read the body under no-cors
    // anyway, and a thrown error here shows up as a red "Executions" entry
    // in the Apps Script dashboard, which is where you'd look.
    console.error(err);
    return ContentService.createTextOutput('error');
  }
}

function doGet() {
  // Visiting the /exec URL in a browser lands here. Handy smoke test that the
  // deployment is live and set to "Anyone".
  return ContentService.createTextOutput('Cool Call Pro contact endpoint is live.');
}
