# 🔐 Getting Google OAuth Credentials

Complete step-by-step guide to download Google Photos and Drive credentials.

## ✅ Prerequisites

- Google account with Photos and Drive access
- Admin access to Google Cloud Console
- 10 minutes

## Step 1: Go to Google Cloud Console

Open: https://console.cloud.google.com/

Sign in with your Google account (losiconosdelabachata@gmail.com or similar)

## Step 2: Create a New Project

1. Click the **Project dropdown** (top left, near Google Cloud logo)
2. Click **NEW PROJECT**
3. Enter name: `Los Iconos Blog`
4. Click **CREATE**
5. Wait for project to be created (~2 mins)

## Step 3: Enable Google Photos Library API

1. In your new project, search for: `Photos Library API`
2. Click on **Google Photos Library API**
3. Click **ENABLE**
4. Wait for it to enable

## Step 4: Enable Google Drive API

1. Search for: `Google Drive API`
2. Click on **Google Drive API**
3. Click **ENABLE**
4. Wait for it to enable

## Step 5: Create OAuth 2.0 Credentials

1. Go to: **APIs & Services** → **Credentials** (left sidebar)
2. Click **+ CREATE CREDENTIALS**
3. Choose: **OAuth 2.0 Client ID**
4. You'll get a warning "To create an OAuth client ID, you must first set a user consent screen"
5. Click **CONFIGURE CONSENT SCREEN**

### Configure Consent Screen

1. Choose **External** (not Internal)
2. Click **CREATE**
3. Fill in the form:
   - **App name**: `Los Iconos Blog`
   - **User support email**: `losiconosdelabachata@gmail.com`
   - **Developer contact**: `losiconosdelabachata@gmail.com`
4. Click **SAVE AND CONTINUE**
5. Click **ADD OR REMOVE SCOPES**
6. Search and add these scopes:
   - `https://www.googleapis.com/auth/photoslibrary.readonly`
   - `https://www.googleapis.com/auth/drive.readonly`
7. Click **UPDATE**
8. Click **SAVE AND CONTINUE**
9. Click **SAVE AND CONTINUE** again
10. Review and click **BACK TO DASHBOARD**

## Step 6: Create OAuth Client ID

Back to **APIs & Services** → **Credentials**

1. Click **+ CREATE CREDENTIALS** again
2. Choose **OAuth 2.0 Client ID**
3. Choose **Desktop application**
4. Name: `Los Iconos Blog`
5. Click **CREATE**
6. A dialog will appear with your credentials
7. Click **DOWNLOAD JSON** (button on the right)

## Step 7: Save Both Credential Files

The downloaded file will be named something like: `client_secret_XXXXXXX.json`

**Important:** Rename it to **`google_photos_credentials.json`** and place in your project folder:

```
C:\Users\Fellito Rodriguez\Projects\google_photos_credentials.json
```

### For Google Drive (Option A: Use Same Credentials)

If using the same OAuth credential for both Photos and Drive:

1. Rename/copy the same JSON file again to:
   ```
   C:\Users\Fellito Rodriguez\Projects\google_drive_credentials.json
   ```

### For Google Drive (Option B: Create Separate Credentials)

If you want separate credentials for Drive (not necessary, but more organized):

1. Repeat Step 6 to create another OAuth Client ID
2. Download the JSON
3. Rename to `google_drive_credentials.json`
4. Place in your project folder

## Step 8: Verify Files

Check that you have these two files in your project directory:

```
C:\Users\Fellito Rodriguez\Projects\
  ├── google_photos_credentials.json
  └── google_drive_credentials.json
```

If using same file for both, both paths can point to the same file.

## Step 9: Run Setup Script

```bash
cd C:\Users\Fellito Rodriguez\Projects\
python setup_google_credentials.py
```

This will:
1. Prompt you to authenticate with Google Photos
2. Prompt you to authenticate with Google Drive
3. Save authentication tokens automatically
4. Verify everything is working

## Step 10: Authenticate in Browser

When prompted by the setup script:

1. A browser will open asking for permission
2. Click **Allow** to grant access
3. You'll see "The authentication flow has completed"
4. Return to terminal/console

Do this twice (once for Photos, once for Drive).

## ✅ Done!

After authentication, you'll see:
```
✅ Google Photos authentication successful!
✅ Google Drive authentication successful!
✅ All credentials configured!
```

## Troubleshooting

### "credentials.json not found"
- Make sure you downloaded the JSON file from Google Cloud Console
- Check that files are named correctly (google_photos_credentials.json)
- Verify they're in the correct directory (C:\Users\Fellito Rodriguez\Projects\)

### "Invalid client" error
- Check that the JSON file contents are valid
- Re-download from Google Cloud Console if needed
- Make sure you haven't edited the JSON file

### "Access Denied" in browser
- Make sure you're signed into the correct Google account
- Grant all permissions when prompted
- Try again if you see "This app hasn't been verified by Google"

### "The authentication flow has completed" but script doesn't continue
- Check browser for any additional prompts
- Close the browser window that opened
- Check terminal/console for error messages

## Verification

To verify credentials are working, run:

```bash
python -c "from google_photos_api import GooglePhotosClient; client = GooglePhotosClient(); print('✅ Connected!')"
```

Should output: `✅ Connected!`

## What Gets Saved

After authentication, these files are created:
- `token.pickle` - OAuth tokens (git-ignored, keep secure)
- `.env` - Configuration (already set up)

These tokens allow the bot to access your Photos and Drive without you needing to login each time.

## Security Notes

- Keep `token.pickle` and JSON credential files private
- Add to `.gitignore` if using version control
- Credentials are read-only (photos and docs only, can't delete or modify)
- Tokens expire and refresh automatically

## Next Steps

After authentication:

1. ✅ Google credentials configured
2. Create `customer_emails.txt` with your customer email list
3. Set up Gmail app password in `.env` (see BLOG_SETUP_GUIDE.md)
4. Run: `python blog_scheduler.py`

Happy blogging! 🎵

---

**Los Iconos de la Bachata**  
*Timeless Music, Timeless Stories*
