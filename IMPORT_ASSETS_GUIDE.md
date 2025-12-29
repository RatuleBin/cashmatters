# Guide: Importing Support Cash Page Assets

This guide explains how to import digital assets (Logos, Banners, Fact Cards, Post Cards, Videos) from the old CashMatters website to the new one.

---

## Overview

The old website at `cashmatters.org` uses dynamic JavaScript loading, making it difficult to scrape assets automatically. You'll need to manually download assets from the old CMS and add them to the new website.

---

## Step 1: Access the Old CMS

1. Go to: **https://cashmatters.backend-api.io/cms/login/**
2. Login with:
   - **Username:** `directorgeneral`
   - **Password:** `SYz6fZ8ndjkf3v`

---

## Step 2: Navigate to Brand Assets

Once logged in, look for:
- **Images** section (for logos, banners, fact cards, post cards)
- **Documents** section (for downloadable PDFs)
- **Media** or **Snippets** section (for video embeds)

The assets you need are:

| Category | What to Download |
|----------|------------------|
| **Logos** | CashMatters logo variations (PNG, SVG) |
| **Banners** | Promotional banner images |
| **Fact Cards** | Statistical infographic cards |
| **Post Cards** | Social media shareable images |
| **Videos** | Vimeo video IDs or embed URLs |

---

## Step 3: Download Assets

### For Images (Logos, Banners, Fact Cards, Post Cards):

1. In the CMS, go to **Images** section
2. Search for or browse to find brand assets
3. Download each image by clicking on it and saving
4. Note the original filenames

### For Videos:

1. Look for Vimeo embed codes or video URLs
2. Note down the Vimeo video IDs (e.g., `123456789` from `vimeo.com/123456789`)

---

## Step 4: Add Assets to New Website

### Image Files Location:

Save downloaded images to:
```
/Users/Apple/Desktop/projects/cashmatters/cashmatters/static/images/support/
```

Create subfolders for organization:
```
cashmatters/static/images/support/
├── logos/
│   ├── logo-dark.png
│   ├── logo-light.png
│   └── logo-icon.svg
├── banners/
│   ├── banner-1.png
│   └── banner-2.png
├── fact-cards/
│   ├── fact-card-1.png
│   └── fact-card-2.png
└── post-cards/
    ├── post-card-1.png
    └── post-card-2.png
```

---

## Step 5: Update the Support Template

Edit the file: `/Users/Apple/Desktop/projects/cashmatters/cashmatters/templates/support.html`

### For Logos (around line 145):

Replace placeholder content with:
```html
<div class="asset-card bg-white d-flex align-items-center justify-content-center p-5">
    <img src="{% static 'images/support/logos/logo-dark.png' %}" alt="CashMatters Logo Dark" class="img-fluid">
</div>
```

### For Banners (around line 175):

Replace placeholder content with:
```html
<div class="asset-card bg-white d-flex align-items-center justify-content-center p-3">
    <img src="{% static 'images/support/banners/banner-1.png' %}" alt="Banner 1" class="img-fluid">
</div>
```

### For Videos (around line 220):

Replace "Coming Soon" with Vimeo embeds:
```html
<div class="ratio ratio-16x9">
    <iframe src="https://player.vimeo.com/video/YOUR_VIDEO_ID"
            frameborder="0"
            allow="autoplay; fullscreen; picture-in-picture"
            allowfullscreen>
    </iframe>
</div>
```

---

## Step 6: Add Download Links

For downloadable assets, update the download links:

```html
<a href="{% static 'images/support/logos/logo-dark.png' %}"
   download="cashmatters-logo-dark.png"
   class="text-reset text-decoration-none hover-mint">
    <i class="bi bi-download"></i> Download
</a>
```

---

## Alternative: Use CDN Links Directly

If assets are already on the old website's CDN, you can link directly:

**CDN Base URL:** `https://d3an988loexeh7.cloudfront.net/media/`

Example found assets:
- Header: `https://d3an988loexeh7.cloudfront.net/media/original_images/assets-header.png`
- Video thumbnails: `https://d3an988loexeh7.cloudfront.net/media/images/cm-video-cash-matters-thumb.origin.2e16d0ba.fill-304x160.png`

You can use these URLs directly in the template if they remain accessible.

---

## Current Support Page Structure

The support page (`support.html`) has these tab sections ready for content:

| Tab | Lines | Current Status |
|-----|-------|----------------|
| Logos | ~145-170 | Has 4 placeholder logos |
| Banners | ~175-200 | Has 2 placeholder banners |
| Fact Cards | ~205-210 | Shows "Coming Soon" |
| Post Cards | ~215-220 | Shows "Coming Soon" |
| Videos | ~225-235 | Shows "Coming Soon" |

---

## Checklist

- [ ] Login to old CMS
- [ ] Download logo variations (at least 4)
- [ ] Download banner images (at least 2)
- [ ] Download fact card images
- [ ] Download post card images
- [ ] Get Vimeo video IDs
- [ ] Create `/cashmatters/static/images/support/` folder structure
- [ ] Save all images to appropriate folders
- [ ] Update `support.html` with correct image paths
- [ ] Add Vimeo embeds for videos
- [ ] Test all download links work
- [ ] Run `python manage.py collectstatic` for production

---

## Need Help?

If you encounter issues:
1. Check that `{% load static %}` is at the top of `support.html`
2. Verify image paths are correct
3. Run `python manage.py collectstatic --noinput` to collect static files
4. Clear browser cache and reload

---

*Last updated: December 2024*
