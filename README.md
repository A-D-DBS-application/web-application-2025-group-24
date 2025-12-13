# Flask Application Setup Guide

This repository contains a Flask web application for property listing with image upload capabilities. Follow the instructions below to set up and run the application on Windows.

## Features

- Property listing and search functionality.
- **Image upload for properties** (New!)
- User authentication for developers and property owners
- Supabase integration for data storage and file management
- Responsive web design

## Prerequisites

- Python 3.x installed on your system
- Git (for cloning the repository)
- Supabase account (for database and storage)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/ambervrschldn/group-24.git
cd group-24
```

### 2. Create Virtual Environment

Create a virtual environment to isolate project dependencies:

```powershell
py -m venv venv
```

### 3. Activate Virtual Environment

**Important**: Always activate the virtual environment before working on the project.

```powershell
.\venv\Scripts\activate.bat
```

You should see `(venv)` at the beginning of your command prompt when the virtual environment is active.

### 4. Install Dependencies

Install all required packages including image upload support:

```powershell
py -m pip install -r requirements.txt
```

Or install individually:
```powershell
py -m pip install flask supabase python-dotenv pillow
```

### 5. Configure Environment Variables

Create a `.env` file in the project root with your Supabase credentials:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SECRET_KEY=your_flask_secret_key
```

### 6. Set Up Supabase Storage

**Important**: You need to create a storage bucket for images:

1. Go to your Supabase dashboard
2. Navigate to Storage
3. Create a new bucket called `property-images`
4. Set the bucket to public (for image access)

## Running the Application

### 1. Ensure Virtual Environment is Active

Make sure your virtual environment is activated (you should see `(venv)` in your prompt):

```powershell
.\venv\Scripts\activate.bat
```

### 2. Run the Flask Application

```powershell
py app.py
```

### 3. Access the Application

Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

## Image Upload Feature

### For Property Owners:

1. **Login** as a property owner
2. **Add New Property** with the form
3. **Upload Multiple Images**:
   - Click "Choose Files" in the Property Images section
   - Select multiple images (JPG, PNG, GIF supported)
   - Images are automatically previewed
   - Maximum 5MB per image
   - You can remove images before submitting

### Image Display:

- **Property List**: Shows first image as a thumbnail
- **Property Details**: Full image gallery with:
  - Large main image
  - Thumbnail navigation
  - Click thumbnails to change main image
  - Responsive design

### Technical Details:

- Images stored in **Supabase Storage**
- Automatic filename generation with timestamp
- Image URLs stored in database
- Supports multiple image formats
- File size validation
- Error handling for upload failures

## Development Workflow

### Daily Development Steps:

1. **Activate virtual environment**:
   ```powershell
   .\venv\Scripts\activate.bat
   ```

2. **Make your code changes** in `app.py` or other files

3. **Run the application**:
   ```powershell
   py app.py
   ```

4. **Test your changes** at http://127.0.0.1:5000

5. **Deactivate virtual environment** when done:
   ```powershell
   deactivate
   ```

## Troubleshooting

### Image Upload Issues

**Storage bucket not found**:
- Ensure you created the `property-images` bucket in Supabase Storage
- Check bucket permissions (should be public for image access)

**Upload fails**:
- Check image file size (max 5MB)
- Verify Supabase credentials in `.env`
- Check console for JavaScript errors

**Images not displaying**:
- Verify bucket is set to public
- Check image URLs in the database
- Ensure proper CORS settings in Supabase

### General Issues

**Virtual Environment Issues**:
- Use the batch file instead: `.\venv\Scripts\activate.bat`
- Or temporarily change execution policy: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**Python Not Found**:
- Use `py` instead of `python`
- Install Python from https://python.org or Microsoft Store
- Ensure Python is added to your system PATH

**Database Connection**:
- Check your `.env` file has correct Supabase credentials
- Verify Supabase project is active
- Check network connection

## Project Structure

```
group-24/
├── .git/                 # Git repository files
├── .gitattributes        # Git attributes configuration
├── .gitignore            # Git ignore file (excludes venv/ and other files)
├── .env                  # Environment variables (not tracked in Git)
├── venv/                 # Virtual environment (created after setup, not tracked in Git)
├── app.py                # Main Flask application with image upload
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## API Endpoints

### Property Management:
- `GET /` - Homepage with search functionality
- `GET /property/<id>` - Property details page with image gallery
- `POST /api/submit-property` - Submit property with image uploads
- `GET /api/properties` - Get properties with search filters

### User Management:
- `POST /api/login` - User login
- `POST /api/register-developer` - Register developer account
- `POST /api/register-property-owner` - Register property owner account

## Database Schema

### Property Table:
- `property_id` - Unique identifier
- `property_name` - Name/title of the property
- `size` - Area in square meters
- `description` - Property description
- `state` - Location/province
- `propertyOwner_id` - Owner's user ID
- `image_urls` - Array of image URLs from Supabase Storage
- `created_at` - Creation timestamp

## Notes

- The application runs in debug mode, which means:
  - Automatic reloading when code changes
  - Detailed error messages
  - **Do not use in production**

- The virtual environment folder (`venv/`) is automatically excluded by `.gitignore`
- **Image storage requires Supabase Storage configuration**
- Always work within the activated virtual environment
- The Flask development server is only for development purposes

## Getting Help

If you encounter any issues:

1. Ensure Python is properly installed: `py --version`
2. Check if pip is available: `py -m pip --version`
3. Verify virtual environment is activated (look for `(venv)` in prompt)
4. Check if all packages are installed: `py -m pip list`
5. Verify `.env` file contains correct Supabase credentials
6. Check Supabase Storage bucket exists and is public

---

**Happy coding with image uploads!** 🚀📸
