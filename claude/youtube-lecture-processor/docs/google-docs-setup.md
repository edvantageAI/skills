# Google Docs API Setup Guide

This reference explains how to set up Google Docs API authentication for creating documents directly via the API.

## Prerequisites

Install required Python packages:

```bash
sudo pip3 install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Authentication Methods

### Method 1: Service Account (Recommended for Automation)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Enable Google Docs API and Google Drive API
4. Create service account credentials:
   - Navigate to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Download JSON key file
5. Save the JSON file securely (e.g., `~/google-credentials.json`)

**Note**: Documents created by service accounts are owned by the service account. To access them:
- Share the document with your Google account email
- Or use the Drive API to transfer ownership

### Method 2: OAuth 2.0 (For User-Owned Documents)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create OAuth 2.0 credentials
3. Download client secrets JSON
4. Use OAuth flow to obtain user credentials

This method creates documents owned by the authenticated user.

## Using Credentials

Pass the credentials file path when creating Google Docs:

```bash
python create_document.py aligned.json output.json --format gdoc --credentials ~/google-credentials.json
```

## Troubleshooting

**Error: "Credentials file not found"**
- Ensure the path to credentials JSON is correct
- Check file permissions

**Error: "API not enabled"**
- Enable Google Docs API and Google Drive API in Cloud Console

**Cannot access created document**
- For service accounts: manually share the document URL with your email
- Or switch to OAuth 2.0 method for user-owned documents
