# Simply Law - UI Components Quick Reference

## 🎯 Common Component Patterns

### Buttons

**Primary Button** (Main Actions)
```html
<button class="btn btn-primary">
    <i class="fas fa-check"></i>
    Confirm Action
</button>
```
CSS: Blue gradient, white text, shadow, lift on hover

**Success Button** (Positive Actions)
```html
<button class="btn btn-success">
    <i class="fas fa-plus"></i>
    Create New
</button>
```
CSS: Green gradient, white text, shadow

**Danger Button** (Destructive Actions)
```html
<button class="btn btn-danger">
    <i class="fas fa-trash"></i>
    Delete Item
</button>
```
CSS: Red gradient, white text, shadow

**Outline Button** (Secondary Actions)
```html
<button class="btn btn-outline">
    <i class="fas fa-times"></i>
    Cancel
</button>
```
CSS: Transparent background, blue border, fills on hover

---

### Form Elements

**Text Input**
```html
<div class="form-group">
    <label class="form-label">Full Name</label>
    <input type="text" class="form-control" placeholder="John Doe">
</div>
```
CSS: Gray border, light background, blue focus state

**Select Dropdown**
```html
<div class="form-group">
    <label class="form-label">Category</label>
    <select class="form-select">
        <option>Select a category</option>
        <option>Legal News</option>
        <option>Case Law</option>
    </select>
</div>
```

**Textarea**
```html
<div class="form-group">
    <label class="form-label">Message</label>
    <textarea class="form-control" rows="5" placeholder="Your message..."></textarea>
</div>
```
CSS: Min-height 150px, vertical resize

**File Upload** (Modern Style)
```html
<div class="file-upload-wrapper">
    <label class="file-upload-label" for="fileInput">
        <div class="file-upload-content">
            <div class="file-upload-icon">
                <i class="fas fa-cloud-upload-alt"></i>
            </div>
            <div class="file-upload-text">Click to upload</div>
            <p class="file-upload-hint">PNG, JPG up to 5MB</p>
        </div>
    </label>
    <input type="file" id="fileInput" class="form-control" style="display: none;">
</div>
```
CSS: Dashed blue border, light blue background, hover effect

---

### Cards

**Standard Card**
```html
<div class="card">
    <div class="card-header">
        <h3>Card Title</h3>
    </div>
    <div class="card-body">
        <p>Card content goes here...</p>
    </div>
</div>
```
CSS: White background, subtle shadow, hover lift

**Info Card** (With Icon)
```html
<div class="card">
    <div style="text-align: center; padding: 2rem;">
        <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; margin: 0 auto 1rem; font-size: 1.75rem;">
            <i class="fas fa-envelope"></i>
        </div>
        <h4>Email</h4>
        <p style="color: #6b7280;">support@simplylaw.com</p>
    </div>
</div>
```

---

### Alerts

**Success Alert**
```html
<div class="alert alert-success">
    <i class="fas fa-check-circle"></i>
    Your action was successful!
</div>
```
CSS: Light green background, green border, green text

**Danger Alert**
```html
<div class="alert alert-danger">
    <i class="fas fa-exclamation-circle"></i>
    An error occurred. Please try again.
</div>
```
CSS: Light red background, red border, red text

**Info Alert**
```html
<div class="alert alert-info">
    <i class="fas fa-info-circle"></i>
    Please fill out all required fields.
</div>
```
CSS: Light blue background, blue border, blue text

---

### Navigation

**Navbar Link** (Active/Hover)
```html
<nav class="navbar">
    <a class="navbar-brand" href="/">
        <img src="logo.png" alt="Logo">
        <span>Simply Law</span>
    </a>
    <ul class="navbar-nav">
        <li class="nav-item">
            <a class="nav-link" href="/about">
                <i class="fas fa-info-circle"></i>
                <span>About</span>
            </a>
        </li>
    </ul>
</nav>
```
CSS: Blue gradient background, white text, rounded hover state

---

### Content Sections

**Section with Title**
```html
<section class="section">
    <div class="container">
        <div class="section-header">
            <h2 class="section-title">Latest Articles</h2>
            <p class="section-subtitle">Explore our collection of legal insights</p>
        </div>
        <!-- Content here -->
    </div>
</section>
```

**Article Card** (Grid Item)
```html
<div class="article-card">
    <div class="article-header">
        <h5 class="article-title">Article Title Here</h5>
        <small class="article-author">by John Doe</small>
    </div>
    <div class="article-body">
        <img src="cover.jpg" class="cover-image" alt="Cover">
        <p class="article-text">Preview text...</p>
        <a href="#" class="read-more-btn">
            Read More <i class="fas fa-arrow-right"></i>
        </a>
    </div>
</div>
```

---

## 📱 Responsive Classes

### Grid System
```html
<!-- 3 columns on desktop, 2 on mobile -->
<div class="articles-grid">
    <div class="article-card">...</div>
    <div class="article-card">...</div>
    <div class="article-card">...</div>
</div>
```

### Container
```html
<div class="container">
    <!-- Max-width 1200px, centered -->
</div>
```

### Responsive Text
```html
<!-- Hide on mobile, show on desktop -->
<span class="d-none d-md-inline">Desktop only text</span>

<!-- Show on mobile, hide on desktop -->
<span class="d-md-none">Mobile only text</span>
```

---

## 🎨 Color Usage Guide

### Primary Actions
Use `#1e3a8a` (deep blue) or `#3b82f6` (bright blue)
- Main buttons
- Links
- Form focus states
- Primary elements

### Secondary Actions
Use `#6b7280` (medium gray) or `#9ca3af` (light gray)
- Less important buttons
- Secondary text
- Disabled states

### Success States
Use `#10b981` (green)
- Confirmation buttons
- Success messages
- Valid form inputs
- Checkmarks

### Danger/Error States
Use `#ef4444` (red)
- Delete buttons
- Error messages
- Invalid inputs
- Warnings

### Backgrounds
- White `#ffffff` - Cards, content areas
- Light Gray `#f8fafc` - Page background
- Lighter Gray `#f1f5f9` - Sections

### Text
- Dark Gray `#1f2937` - Headings, primary text
- Medium Gray `#6b7280` - Body text
- Light Gray `#9ca3af` - Hints, disabled

---

## 🎬 Animation Patterns

### Fade In
```css
animation: fadeIn 0.6s ease-out;

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
```

### Slide Down
```css
animation: slideDown 0.6s ease-out;

@keyframes slideDown {
    from {
        opacity: 0;
        transform: translateY(-30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
```

### Lift on Hover
```css
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

&:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}
```

### Smooth Color Change
```css
transition: all 0.3s ease;

&:hover {
    color: #3b82f6;
    background: #f0f9ff;
}
```

---

## 📏 Spacing Examples

```html
<!-- Margin around element -->
<div style="margin: 2rem;">Content</div>

<!-- Padding inside element -->
<div style="padding: 1.5rem;">Content</div>

<!-- Margin bottom (common) -->
<div style="margin-bottom: 1rem;">Content</div>

<!-- Gap between flex items -->
<div style="display: flex; gap: 1rem;">
    <div>Item 1</div>
    <div>Item 2</div>
</div>
```

**Spacing Scale**:
- xs: 0.25rem (4px)
- sm: 0.5rem (8px)
- md: 1rem (16px)
- lg: 1.5rem (24px)
- xl: 2rem (32px)
- 2xl: 3rem (48px)

---

## 🔤 Typography Examples

```html
<!-- Heading 1 -->
<h1 class="section-title">Page Title</h1>

<!-- Heading 2 -->
<h2>Section Heading</h2>

<!-- Heading 3 -->
<h3>Subsection</h3>

<!-- Body Text -->
<p>Regular paragraph text with line-height 1.6...</p>

<!-- Secondary Text -->
<p style="color: #6b7280;">Secondary text in gray</p>

<!-- Small Text -->
<small style="color: #9ca3af;">Small hint text</small>
```

**Font Sizes**:
- H1: 2.5rem (40px)
- H2: 2rem (32px)
- H3: 1.75rem (28px)
- Body: 1rem (16px)
- Small: 0.875rem (14px)

---

## 💡 Best Practices

### ✅ DO
- Use consistent spacing from the scale
- Apply hover effects to interactive elements
- Use icons with text on buttons
- Test on mobile devices
- Use semantic HTML
- Keep animations under 400ms
- Maintain color contrast
- Group related form fields

### ❌ DON'T
- Mix multiple button styles in same action group
- Use flash red for non-critical messages
- Create text smaller than 14px
- Forget padding on mobile
- Animate on every interaction
- Use too many different colors
- Nest cards more than 2 levels
- Forget focus states

---

## 🔗 Common Component Combinations

### Form Section
```html
<div class="submit-card">
    <div class="submit-card-header">
        <h2 class="card-header-title">Form Title</h2>
    </div>
    <div class="form-body">
        <div class="form-group">
            <label class="form-label">Field Label</label>
            <input type="text" class="form-control">
        </div>
        <button class="btn-submit">Submit</button>
    </div>
</div>
```

### Info Grid
```html
<div class="contact-grid">
    <div class="contact-form-card">
        <!-- Form here -->
    </div>
    <div class="contact-info-container">
        <div class="info-card">
            <!-- Info here -->
        </div>
    </div>
</div>
```

### Article Grid
```html
<div class="articles-grid">
    <div class="article-card">
        <div class="article-header">
            <h5 class="article-title">Title</h5>
        </div>
        <div class="article-body">
            <!-- Content -->
        </div>
    </div>
</div>
```

---

**Last Updated**: January 4, 2026
**Quick Reference Version**: 1.0
