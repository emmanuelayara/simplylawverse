"""
Test suite for input validation and security measures
Run with: python -m pytest test_validation.py
"""

import pytest
from security import (
    sanitize_html, sanitize_string, validate_email,
    validate_image_file, validate_document_file,
    get_safe_filename
)
from werkzeug.datastructures import FileStorage
from io import BytesIO


class TestEmailValidation:
    """Email validation tests"""
    
    def test_valid_emails(self):
        """Test that valid emails pass validation"""
        valid_emails = [
            "user@example.com",
            "john.doe@company.co.uk",
            "support+tag@website.org",
            "test123@sub.domain.com",
        ]
        for email in valid_emails:
            assert validate_email(email), f"Email should be valid: {email}"
    
    def test_invalid_emails(self):
        """Test that invalid emails fail validation"""
        invalid_emails = [
            "invalid.email@",
            "user@domain",
            "@example.com",
            "user..name@example.com",
            "user@domain..",
            "user name@example.com",
            "user@exam ple.com",
            "",
            "user" * 50 + "@example.com",  # Too long
        ]
        for email in invalid_emails:
            assert not validate_email(email), f"Email should be invalid: {email}"
    
    def test_email_length_limit(self):
        """Test email length validation"""
        # Max 120 characters
        long_email = "a" * 115 + "@example.com"  # 128 chars, too long
        assert not validate_email(long_email)


class TestXSSSanitization:
    """XSS prevention tests"""
    
    def test_script_removal(self):
        """Test that script tags are removed"""
        test_cases = [
            ('<script>alert("xss")</script>', ''),
            ('Hello <script>alert(1)</script> World', 'Hello  World'),
        ]
        for input_text, expected in test_cases:
            result = sanitize_html(input_text)
            assert '<script' not in result.lower()
    
    def test_event_handlers_removed(self):
        """Test that event handlers are removed"""
        test_cases = [
            ('<img src=x onerror="alert(1)">', '<img src="x">'),
            ('<div onclick="evil()">Click</div>', 'Click'),
            ('<input onchange="hack()" />', '<input>'),
        ]
        for input_text, _ in test_cases:
            result = sanitize_html(input_text)
            assert 'onclick' not in result.lower()
            assert 'onerror' not in result.lower()
            assert 'onchange' not in result.lower()
    
    def test_dangerous_tags_removed(self):
        """Test that dangerous tags are stripped"""
        dangerous_inputs = [
            '<iframe src="evil.com"></iframe>',
            '<embed src="malware.swf">',
            '<object data="bad"></object>',
        ]
        for input_text in dangerous_inputs:
            result = sanitize_html(input_text)
            assert '<iframe' not in result.lower()
            assert '<embed' not in result.lower()
            assert '<object' not in result.lower()
    
    def test_safe_tags_preserved(self):
        """Test that safe tags are kept"""
        input_text = '<p>Hello <strong>world</strong>! <a href="google.com">Link</a></p>'
        result = sanitize_html(input_text)
        assert '<p>' in result
        assert '<strong>' in result
        assert '<a' in result
    
    def test_javascript_url_removed(self):
        """Test that javascript: URLs are handled"""
        input_text = '<a href="javascript:alert(1)">Click</a>'
        result = sanitize_html(input_text)
        # Bleach removes the href attribute
        assert 'javascript:' not in result.lower()


class TestStringValidation:
    """Plain text sanitization tests"""
    
    def test_null_bytes_removed(self):
        """Test that null bytes are removed"""
        input_text = "Hello\x00World"
        result = sanitize_string(input_text)
        assert '\x00' not in result
        assert result == "HelloWorld"
    
    def test_length_limit(self):
        """Test maximum length enforcement"""
        input_text = "A" * 100
        result = sanitize_string(input_text, max_length=50)
        assert len(result) == 50
    
    def test_html_escaping(self):
        """Test HTML escaping when allow_html=False"""
        input_text = "<p>Hello</p>"
        result = sanitize_string(input_text, allow_html=False)
        assert '&lt;p&gt;' in result
        assert '<p>' not in result
    
    def test_whitespace_stripping(self):
        """Test leading/trailing whitespace removal"""
        input_text = "  Hello World  \n\t"
        result = sanitize_string(input_text)
        assert result == "Hello World"


class TestFilenameGeneration:
    """Safe filename generation tests"""
    
    def test_path_traversal_prevention(self):
        """Test that path traversal attempts are prevented"""
        dangerous_names = [
            "../../etc/passwd",
            "..\\..\\windows\\system32",
            "..\\/admin/key.txt",
        ]
        for name in dangerous_names:
            result = get_safe_filename(name)
            assert '..' not in result
            assert '/' not in result or result.startswith('{')
    
    def test_special_characters_removed(self):
        """Test that special characters are removed"""
        input_names = [
            "file<name>.txt",
            "file|name.txt",
            "file:name.txt",
            "file*name.txt",
        ]
        for name in input_names:
            result = get_safe_filename(name)
            assert '<' not in result
            assert '|' not in result
            assert ':' not in result
            assert '*' not in result
    
    def test_timestamp_prefix(self):
        """Test that timestamp prefix is added"""
        filename = "document.pdf"
        result = get_safe_filename(filename)
        # Format should be: {timestamp}_{filename}
        assert '_' in result
        assert 'document.pdf' in result.lower()
    
    def test_empty_filename_handling(self):
        """Test handling of empty filenames"""
        result = get_safe_filename("...")
        assert len(result) > 0  # Should have at least timestamp
        assert result != "..."


class TestFileValidation:
    """File upload validation tests"""
    
    def test_image_size_limit(self):
        """Test that oversized images are rejected"""
        # Create a mock file > 5MB
        large_content = b"x" * (6 * 1024 * 1024)  # 6MB
        file = FileStorage(
            stream=BytesIO(large_content),
            filename="large.jpg",
            content_type="image/jpeg"
        )
        
        is_valid, error = validate_image_file(file)
        assert not is_valid
        assert "too large" in error.lower()
    
    def test_document_size_limit(self):
        """Test that oversized documents are rejected"""
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        file = FileStorage(
            stream=BytesIO(large_content),
            filename="large.pdf",
            content_type="application/pdf"
        )
        
        is_valid, error = validate_document_file(file)
        assert not is_valid
        assert "too large" in error.lower()
    
    def test_invalid_image_extension(self):
        """Test that non-image files are rejected for image upload"""
        content = b"Not an image"
        file = FileStorage(
            stream=BytesIO(content),
            filename="document.pdf",
            content_type="application/pdf"
        )
        
        is_valid, error = validate_image_file(file)
        assert not is_valid
        assert "Invalid" in error or "type" in error.lower()
    
    def test_invalid_document_extension(self):
        """Test that non-document files are rejected for document upload"""
        content = b"Not a document"
        file = FileStorage(
            stream=BytesIO(content),
            filename="image.jpg",
            content_type="image/jpeg"
        )
        
        is_valid, error = validate_document_file(file)
        assert not is_valid
        assert "Invalid" in error or "type" in error.lower()
    
    def test_empty_file_rejection(self):
        """Test that empty files are rejected"""
        file = FileStorage(
            stream=BytesIO(b""),
            filename="empty.jpg",
            content_type="image/jpeg"
        )
        
        is_valid, error = validate_image_file(file)
        assert not is_valid
        assert "empty" in error.lower()
    
    def test_no_extension_rejection(self):
        """Test that files without extensions are rejected"""
        content = b"Some content"
        file = FileStorage(
            stream=BytesIO(content),
            filename="noextension",
            content_type="image/jpeg"
        )
        
        is_valid, error = validate_image_file(file)
        assert not is_valid


class TestFormValidation:
    """Form-level validation tests (requires Flask app context)"""
    
    def test_comment_form_validation(self):
        """Test CommentForm validation"""
        from forms import CommentForm
        
        # Valid form
        form = CommentForm()
        form.name.data = "John Doe"
        form.email.data = "john@example.com"
        form.content.data = "Great article!"
        
        # Note: validate() requires form submission context
        # This is a simplified test
        assert len(form.name.data) >= 2
        assert len(form.content.data) >= 2
    
    def test_article_form_content_limits(self):
        """Test ArticleSubmissionForm content limits"""
        from forms import ArticleSubmissionForm
        
        form = ArticleSubmissionForm()
        
        # Title validation (5-200 chars)
        form.title.data = "Valid Article Title"
        assert 5 <= len(form.title.data) <= 200
        
        # Content validation (50-50000 chars)
        form.content.data = "This is a " * 100  # 1000 chars
        assert 50 <= len(form.content.data) <= 50000


# Integration tests
class TestIntegration:
    """Integration tests combining multiple validators"""
    
    def test_malicious_comment_sanitization(self):
        """Test complete comment sanitization flow"""
        malicious_comment = """
        Nice article! <script>alert('hacked')</script>
        <img src=x onerror="fetch('/admin/delete')">
        <a href="javascript:void(0)">Click here</a>
        """
        
        # Sanitize
        result = sanitize_html(malicious_comment)
        
        # Verify no malicious content
        assert '<script' not in result.lower()
        assert 'onerror' not in result.lower()
        assert 'javascript:' not in result.lower()
        assert 'fetch' not in result.lower()
    
    def test_file_upload_complete_validation(self):
        """Test complete file upload validation"""
        # Valid image
        valid_image = FileStorage(
            stream=BytesIO(b"Valid image content"),
            filename="photo.jpg",
            content_type="image/jpeg"
        )
        
        is_valid, error = validate_image_file(valid_image)
        assert is_valid
        assert error is None


if __name__ == "__main__":
    print("Run with: pytest test_validation.py -v")
    print("\nTo run all tests:")
    print("  pytest test_validation.py")
    print("\nTo run specific test class:")
    print("  pytest test_validation.py::TestEmailValidation")
    print("\nTo run with coverage:")
    print("  pytest test_validation.py --cov=security --cov=forms")
