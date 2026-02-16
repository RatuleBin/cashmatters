# Cash Matters - Wagtail Dashboard

A Wagtail CMS dashboard with custom login page and blog functionality.

## Features

- ✅ Custom branded login page with gradient background
- ✅ Blog/Vlog functionality with rich text editor
- ✅ Wagtail admin dashboard for content management
- ✅ Responsive design
- ✅ SQLite database (easy to upgrade to PostgreSQL)

## Project Structure

```
cashmatters/
├── blog/                       # Blog app for vlog/blog posts
│   ├── models.py              # BlogIndexPage and BlogPage models
│   └── templates/
│       └── blog/
│           ├── blog_index_page.html
│           └── blog_page.html
├── cashmatters/               # Main project settings
│   ├── settings/
│   ├── static/
│   │   └── css/
│   │       └── blog.css       # Blog styling
│   └── templates/
│       └── wagtailadmin/
│           └── login.html     # Custom login page
├── home/                      # Default home page app
└── manage.py
```

## Setup Instructions

### 1. Create a Superuser (Admin Account)

Run the following command to create an admin account:

```bash
python manage.py createsuperuser
```

You'll be prompted to enter:
- Username
- Email address
- Password

### 2. Run the Development Server

```bash
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`

### 3. Access the Dashboard

1. **Admin Dashboard**: Navigate to `http://127.0.0.1:8000/admin/`
2. **Login**: Use the superuser credentials you created
3. **Custom Login Page**: You'll see the custom "Cash Matters" branded login page

### 4. Create Blog Pages

1. Log into the admin dashboard
2. Go to "Pages" in the left sidebar
3. Click on "Home" and then "+ Add child page"
4. Select "Blog Index Page" as the page type
5. Give it a title like "Blog" or "Vlog"
6. Add an intro text (optional)
7. Click "Publish"

8. To add blog posts:
   - Click on your Blog Index Page
   - Click "+ Add child page"
   - Select "Blog Page"
   - Fill in the date, title, intro, and body content
   - Click "Publish"

### 5. View Your Blog

Visit `http://127.0.0.1:8000/` and navigate to your blog page to see your posts.

## Key Features Explained

### Custom Login Page

The login page (`cashmatters/templates/wagtailadmin/login.html`) features:
- Custom "Cash Matters" branding
- Gradient purple background
- Styled form inputs
- Responsive design

### Blog Models

**BlogIndexPage**: 
- Main blog listing page
- Shows all published blog posts
- Displays posts in reverse chronological order

**BlogPage**: 
- Individual blog post
- Fields: date, intro, body (rich text)
- Searchable content

## Customization

### Change Login Page Colors

Edit `cashmatters/templates/wagtailadmin/login.html` and modify the CSS:

```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);  /* Background gradient */
background: #43b1b0;  /* Button color */
```

### Add More Fields to Blog Posts

Edit `blog/models.py` and add fields to the `BlogPage` model:

```python
featured_image = models.ForeignKey(
    'wagtailimages.Image',
    null=True,
    blank=True,
    on_delete=models.SET_NULL,
    related_name='+'
)
```

Don't forget to run migrations after making changes:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Next Steps

- Add image uploads to blog posts
- Create more page types
- Customize the admin dashboard colors
- Add user authentication for the frontend
- Deploy to production (Heroku, DigitalOcean, etc.)

## Useful Commands

```bash
# Create new app
python manage.py startapp appname

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files (for production)
python manage.py collectstatic

# Create superuser
python manage.py createsuperuser
```

## Resources

- [Wagtail Documentation](https://docs.wagtail.org/)
- [Django Documentation](https://docs.djangoproject.com/)
- [Wagtail Tutorial](https://docs.wagtail.org/en/stable/getting_started/tutorial.html)

## License

This project is open source and available under the MIT License.
