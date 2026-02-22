"""
Image Optimization Module
Handles image compression, format conversion, and responsive image generation
"""

import os
from pathlib import Path
from PIL import Image
import io
from werkzeug.utils import secure_filename

# Image settings
MAX_IMAGE_WIDTH = 1200
MAX_IMAGE_HEIGHT = 800
THUMBNAIL_WIDTH = 400
THUMBNAIL_HEIGHT = 300
WEBP_QUALITY = 85
JPEG_QUALITY = 85
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_image_file(filename):
    """Check if file is an allowed image type"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def optimize_image(image_path, max_width=MAX_IMAGE_WIDTH, max_height=MAX_IMAGE_HEIGHT):
    """
    Optimize an image by compressing and resizing
    Returns the optimized image path
    """
    try:
        if not os.path.exists(image_path):
            return None

        # Open image
        img = Image.open(image_path)

        # Convert RGBA to RGB if necessary (for JPEG compatibility)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        # Resize if too large
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

        # Save optimized version (overwrite original)
        img.save(image_path, 'JPEG', quality=JPEG_QUALITY, optimize=True)

        return image_path

    except Exception as e:
        print(f"Error optimizing image {image_path}: {str(e)}")
        return None


def create_thumbnail(image_path, thumbnail_dir=None):
    """
    Create a thumbnail version of the image
    Returns the thumbnail path
    """
    try:
        if not os.path.exists(image_path):
            return None

        img = Image.open(image_path)

        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        # Create thumbnail
        img.thumbnail((THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT), Image.Resampling.LANCZOS)

        # Determine thumbnail path
        if thumbnail_dir is None:
            base_path = Path(image_path)
            thumbnail_path = base_path.parent / f"{base_path.stem}_thumb.jpg"
        else:
            filename = Path(image_path).name
            thumbnail_path = os.path.join(thumbnail_dir, f"thumb_{filename}")

        # Save thumbnail
        img.save(thumbnail_path, 'JPEG', quality=JPEG_QUALITY, optimize=True)

        return thumbnail_path

    except Exception as e:
        print(f"Error creating thumbnail for {image_path}: {str(e)}")
        return None


def create_webp_version(image_path):
    """
    Create a WebP version of the image for better compression
    Returns the WebP path
    """
    try:
        if not os.path.exists(image_path):
            return None

        img = Image.open(image_path)

        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        # Create WebP path
        base_path = Path(image_path)
        webp_path = base_path.with_suffix('.webp')

        # Save as WebP
        img.save(webp_path, 'WEBP', quality=WEBP_QUALITY)

        return webp_path

    except Exception as e:
        print(f"Error creating WebP version for {image_path}: {str(e)}")
        return None


def get_image_dimensions(image_path):
    """Get the dimensions of an image"""
    try:
        if not os.path.exists(image_path):
            return None

        img = Image.open(image_path)
        return {
            'width': img.width,
            'height': img.height,
            'aspect_ratio': round(img.width / img.height, 2) if img.height > 0 else 0
        }

    except Exception as e:
        print(f"Error getting image dimensions for {image_path}: {str(e)}")
        return None


def generate_srcset_data(image_filename, static_dir='static/uploads'):
    """
    Generate srcset data for responsive images
    Returns a dictionary with different image sizes
    """
    image_path = os.path.join(static_dir, image_filename)

    if not os.path.exists(image_path):
        return None

    srcset_data = {
        'original': f"/static/uploads/{image_filename}",
        'sizes': ""
    }

    try:
        # Get original dimensions
        dims = get_image_dimensions(image_path)
        if dims:
            srcset_data['original'] = f"/static/uploads/{image_filename} {dims['width']}w"

        # Create multiple sizes for responsive images
        sizes = [400, 600, 900, 1200]
        srcset_list = []

        for size in sizes:
            srcset_list.append(f"/static/uploads/{image_filename} {size}w")

        srcset_data['srcset'] = ", ".join(srcset_list)
        srcset_data['sizes'] = "(max-width: 576px) 100vw, (max-width: 768px) 90vw, (max-width: 1024px) 80vw, 1000px"

    except Exception as e:
        print(f"Error generating srcset data: {str(e)}")

    return srcset_data


class ImageProcessor:
    """Class for batch image processing"""

    def __init__(self, upload_dir='static/uploads'):
        self.upload_dir = upload_dir
        self.processed_files = []
        self.errors = []

    def process_upload(self, file, filename):
        """
        Process an uploaded image file
        Returns a dict with file information and paths
        """
        try:
            # Secure the filename
            filename = secure_filename(filename)

            # Check extension
            if not allowed_image_file(filename):
                self.errors.append(f"File type not allowed: {filename}")
                return None

            # Save original
            filepath = os.path.join(self.upload_dir, filename)
            os.makedirs(self.upload_dir, exist_ok=True)
            file.save(filepath)

            # Optimize
            optimized_path = optimize_image(filepath)

            # Create thumbnail
            thumbnail_path = create_thumbnail(filepath)

            # Create WebP version
            webp_path = create_webp_version(filepath)

            result = {
                'filename': filename,
                'original_path': filepath,
                'thumbnail_path': thumbnail_path,
                'webp_path': webp_path,
                'dimensions': get_image_dimensions(filepath),
                'srcset': generate_srcset_data(filename)
            }

            self.processed_files.append(result)
            return result

        except Exception as e:
            error_msg = f"Error processing image {filename}: {str(e)}"
            self.errors.append(error_msg)
            return None

    def cleanup(self):
        """Remove processed files and reset"""
        self.processed_files = []
        self.errors = []

    def get_summary(self):
        """Get processing summary"""
        return {
            'processed_count': len(self.processed_files),
            'error_count': len(self.errors),
            'files': self.processed_files,
            'errors': self.errors
        }
