# How to View the UI Prototypes

## Quick Access URLs

I've set up HTTP servers to serve the HTML prototypes. You can view them at:

### 1. **UX Prototypes Server** (Port 8080)
   - **Document Upload**: http://localhost:8080/document-upload.html
   - **Extraction Review**: http://localhost:8080/extraction-review.html

### 2. **Root HTML Files Server** (Port 8081)
   - **Manual Entry Form**: http://localhost:8081/dream-ui-minimal.html

### 3. **React App** (Port 5173)
   - **Main Application**: http://localhost:5173
   - Views:
     - http://localhost:5173/#dashboard
     - http://localhost:5173/#analysis
     - http://localhost:5173/#pipeline
     - http://localhost:5173/#intake

## Alternative: Open Files Directly

You can also open the HTML files directly in your browser:

1. **Windows File Explorer**: Navigate to the file and double-click it
2. **Browser**: File → Open → Select the HTML file
3. **Drag & Drop**: Drag the HTML file into your browser window

**File Locations:**
- `ux-prototypes/document-upload.html`
- `ux-prototypes/extraction-review.html`
- `dream-ui-minimal.html` (in root directory)

## Troubleshooting

If you see a blank page:
1. **Check the browser console** (F12) for errors
2. **Make sure the servers are running**:
   - Port 8080: UX Prototypes
   - Port 8081: Root HTML files
   - Port 5173: React App (Vite)
3. **Try a different browser** (Chrome, Firefox, Edge)

## Server Status

To check if servers are running:
```powershell
Get-NetTCPConnection -LocalPort 8080,8081,5173 -ErrorAction SilentlyContinue
```

## Stop Servers

To stop the servers, press `Ctrl+C` in the terminal where they're running, or close the terminal window.







