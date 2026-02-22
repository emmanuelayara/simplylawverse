# Template Integration Quick Reference

## Components Overview

| Component | File | Purpose |
|-----------|------|---------|
| Upload Feedback | `upload_feedback.html` | Toast notifications + file validation |
| Advanced Search | `advanced_search.html` | Enhanced search UI with filters |
| Trending Articles | `trending_articles.html` | Display trending/most viewed articles |
| Lazy Loading | `lazy_loading.html` | Image optimization + lazy loading |

## home.html - Integration Example

```html
{% extends 'layout.html' %}

{% block content %}
<div class="container mt-5">
    <!-- Search Section -->
    {% include 'components/advanced_search.html' %}
    
    <!-- Trending Articles Section -->
    {% include 'components/trending_articles.html' %}
    
    <!-- Main Articles Section -->
    <section class="articles-section">
        <h2 class="mb-4">{{ 'Search Results' if search_query else 'Latest Articles' }}</h2>
        
        <div class="row">
            {% for article in articles.items %}
                <div class="col-md-6 mb-4">
                    <div class="card article-card">
                        {% if article.image_filename %}
                            <img src="{{ url_for('static', filename='uploads/' + article.image_filename) }}"
                                 data-src="{{ url_for('static', filename='uploads/' + article.image_filename) }}"
                                 loading="lazy"
                                 class="card-img-top"
                                 alt="{{ article.title }}">
                        {% else %}
                            <img src="{{ url_for('static', filename='images/placeholder-article.png') }}"
                                 loading="lazy"
                                 class="card-img-top"
                                 alt="No image">
                        {% endif %}
                        
                        <div class="card-body">
                            <h5 class="card-title">{{ article.title }}</h5>
                            <p class="card-text text-muted">{{ article.category }}</p>
                            <p class="card-text">{{ article.content[:200] | striptags }}...</p>
                            
                            <div class="d-flex justify-content-between align-items-center">
                                <small class="text-muted">
                                    <i class="fas fa-eye"></i> {{ article.views or 0 }} views
                                </small>
                                <a href="{{ url_for('articles.view_article', article_id=article.id) }}"
                                   class="btn btn-sm btn-primary">Read More</a>
                            </div>
                        </div>
                    </div>
                </div>
            {% endfor %}
        </div>
        
        <!-- Pagination -->
        {% if articles.pages > 1 %}
            <nav class="mt-4">
                <ul class="pagination justify-content-center">
                    {% if articles.has_prev %}
                        <li class="page-item">
                            <a class="page-link" href="{{ url_for('public.home', page=articles.prev_num, search=search_query, category=selected_category, sort_by=sort_by) }}">
                                Previous
                            </a>
                        </li>
                    {% endif %}
                    
                    {% for page_num in articles.iter_pages() %}
                        {% if page_num %}
                            {% if page_num == articles.page %}
                                <li class="page-item active">
                                    <span class="page-link">{{ page_num }}</span>
                                </li>
                            {% else %}
                                <li class="page-item">
                                    <a class="page-link" href="{{ url_for('public.home', page=page_num, search=search_query, category=selected_category, sort_by=sort_by) }}">
                                        {{ page_num }}
                                    </a>
                                </li>
                            {% endif %}
                        {% endif %}
                    {% endfor %}
                    
                    {% if articles.has_next %}
                        <li class="page-item">
                            <a class="page-link" href="{{ url_for('public.home', page=articles.next_num, search=search_query, category=selected_category, sort_by=sort_by) }}">
                                Next
                            </a>
                        </li>
                    {% endif %}
                </ul>
            </nav>
        {% endif %}
    </section>
</div>

<!-- Include Lazy Loading Script -->
{% include 'components/lazy_loading.html' %}
{% endblock %}
```

## submit_article.html - Integration Example

```html
{% extends 'layout.html' %}

{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <h2 class="mb-4">Submit an Article</h2>
            
            <!-- Include Upload Feedback Component -->
            {% include 'components/upload_feedback.html' %}
            
            <form method="POST" enctype="multipart/form-data" id="article-form">
                {{ form.hidden_tag() }}
                
                <!-- Title Field -->
                <div class="form-group mb-3">
                    {{ form.title.label }}
                    {{ form.title(class="form-control", placeholder="Enter article title...") }}
                    {% if form.title.errors %}
                        <div class="invalid-feedback d-block">
                            {{ form.title.errors[0] }}
                        </div>
                    {% endif %}
                </div>
                
                <!-- Category Field -->
                <div class="form-group mb-3">
                    {{ form.category.label }}
                    {{ form.category(class="form-control") }}
                    {% if form.category.errors %}
                        <div class="invalid-feedback d-block">
                            {{ form.category.errors[0] }}
                        </div>
                    {% endif %}
                </div>
                
                <!-- Content Field -->
                <div class="form-group mb-3">
                    {{ form.content.label }}
                    {{ form.content(class="form-control", rows="8", placeholder="Write your article content...") }}
                    {% if form.content.errors %}
                        <div class="invalid-feedback d-block">
                            {{ form.content.errors[0] }}
                        </div>
                    {% endif %}
                </div>
                
                <!-- Image Upload -->
                <div class="form-group mb-3">
                    {{ form.cover_image.label }}
                    {{ form.cover_image(class="form-control", id="cover-image-input") }}
                    {% if form.cover_image.errors %}
                        <div class="invalid-feedback d-block">
                            {{ form.cover_image.errors[0] }}
                        </div>
                    {% endif %}
                    <small class="form-text text-muted">
                        Max size: 5MB. Allowed: JPG, PNG
                    </small>
                </div>
                
                <!-- Document Upload -->
                <div class="form-group mb-3">
                    {{ form.document.label }}
                    {{ form.document(class="form-control", id="document-input") }}
                    {% if form.document.errors %}
                        <div class="invalid-feedback d-block">
                            {{ form.document.errors[0] }}
                        </div>
                    {% endif %}
                    <small class="form-text text-muted">
                        Max size: 10MB. Allowed: PDF, DOCX
                    </small>
                </div>
                
                <!-- Author Fields (if not logged in) -->
                {% if not current_user.is_authenticated %}
                    <div class="form-group mb-3">
                        {{ form.author_name.label }}
                        {{ form.author_name(class="form-control", placeholder="Your name...") }}
                        {% if form.author_name.errors %}
                            <div class="invalid-feedback d-block">
                                {{ form.author_name.errors[0] }}
                            </div>
                        {% endif %}
                    </div>
                    
                    <div class="form-group mb-3">
                        {{ form.author_email.label }}
                        {{ form.author_email(class="form-control", type="email", placeholder="your.email@example.com") }}
                        {% if form.author_email.errors %}
                            <div class="invalid-feedback d-block">
                                {{ form.author_email.errors[0] }}
                            </div>
                        {% endif %}
                    </div>
                {% endif %}
                
                <!-- Submit Button with Loading State -->
                <div class="form-group">
                    <button type="submit" class="btn btn-primary btn-lg w-100" id="submit-button">
                        <span class="submit-text">Submit Article</span>
                        <span class="submit-spinner d-none">
                            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                            Submitting...
                        </span>
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>

<script>
    // Initialize FileUploadHandler for image and document inputs
    document.addEventListener('DOMContentLoaded', function() {
        const fileHandler = new FileUploadHandler();
        
        // Setup image input
        const imageInput = document.getElementById('cover-image-input');
        if (imageInput) {
            imageInput.addEventListener('change', function(e) {
                fileHandler.handleFileSelect(e);
            });
        }
        
        // Setup document input
        const docInput = document.getElementById('document-input');
        if (docInput) {
            docInput.addEventListener('change', function(e) {
                fileHandler.handleFileSelect(e);
            });
        }
        
        // Setup form loading state
        const form = document.getElementById('article-form');
        if (form) {
            form.addEventListener('submit', function() {
                const formState = new FormLoadingState(document.getElementById('submit-button'));
                formState.handleSubmit();
            });
        }
    });
</script>

<!-- Include Lazy Loading Script -->
{% include 'components/lazy_loading.html' %}
{% endblock %}
```

## edit_article.html - Integration Example

```html
{% extends 'layout.html' %}

{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <h2 class="mb-4">Edit Article</h2>
            
            <!-- Include Upload Feedback Component -->
            {% include 'components/upload_feedback.html' %}
            
            <form method="POST" enctype="multipart/form-data" id="edit-article-form">
                {{ form.hidden_tag() }}
                
                <!-- Title -->
                <div class="form-group mb-3">
                    {{ form.title.label }}
                    {{ form.title(class="form-control") }}
                </div>
                
                <!-- Category -->
                <div class="form-group mb-3">
                    {{ form.category.label }}
                    {{ form.category(class="form-control") }}
                </div>
                
                <!-- Content -->
                <div class="form-group mb-3">
                    {{ form.content.label }}
                    {{ form.content(class="form-control", rows="10") }}
                </div>
                
                <!-- Current Image Preview -->
                {% if article.image_filename %}
                    <div class="form-group mb-3">
                        <label>Current Cover Image</label>
                        <img src="{{ url_for('static', filename='uploads/' + article.image_filename) }}"
                             loading="lazy"
                             class="img-fluid rounded"
                             style="max-height: 200px;"
                             alt="Current cover image">
                    </div>
                {% endif %}
                
                <!-- New Image Upload -->
                <div class="form-group mb-3">
                    {{ form.cover_image.label }}
                    {{ form.cover_image(class="form-control", id="cover-image-input") }}
                    <small class="form-text text-muted">
                        Leave empty to keep current image. Max: 5MB
                    </small>
                </div>
                
                <!-- Buttons -->
                <div class="form-group">
                    <button type="submit" class="btn btn-primary" id="update-button">
                        <span class="submit-text">Update Article</span>
                        <span class="submit-spinner d-none">
                            <span class="spinner-border spinner-border-sm"></span>
                            Updating...
                        </span>
                    </button>
                    <a href="{{ url_for('articles.my_articles') }}" class="btn btn-secondary">
                        Cancel
                    </a>
                </div>
            </form>
        </div>
    </div>
</div>

<script>
    document.addEventListener('DOMContentLoaded', function() {
        const fileHandler = new FileUploadHandler();
        const imageInput = document.getElementById('cover-image-input');
        
        if (imageInput) {
            imageInput.addEventListener('change', fileHandler.handleFileSelect.bind(fileHandler));
        }
        
        const form = document.getElementById('edit-article-form');
        form.addEventListener('submit', function() {
            const formState = new FormLoadingState(document.getElementById('update-button'));
            formState.handleSubmit();
        });
    });
</script>

<!-- Include Lazy Loading Script -->
{% include 'components/lazy_loading.html' %}
{% endblock %}
```

## Template Variables Summary

### home.html Required Variables
```python
{
    'articles': Paginated articles,
    'categories': List of categories,
    'search_query': Current search term,
    'selected_category': Currently selected category,
    'sort_by': Current sort order,
    'trending_articles': Top 5 trending articles
}
```

### Form Required CSS Classes
```html
<!-- Button loading state -->
<button id="submit-button" class="btn btn-primary">
    <span class="submit-text">Submit</span>
    <span class="submit-spinner d-none">Loading...</span>
</button>

<!-- File input for handler -->
<input type="file" id="cover-image-input" class="form-control">
```

## CSS Classes Reference

### Upload Feedback
- `.toast-container`: Toast wrapper
- `.toast`: Individual toast notification
- `.toast-success`, `.toast-error`, `.toast-warning`: Toast types
- `.file-upload-progress`: Progress bar container
- `.loading-spinner`: Spinner animation

### Advanced Search
- `.advanced-search`: Main search container
- `.search-grid`: Form fields grid
- `.tag-filters`: Quick filter tags
- `.tag-filter.active`: Active filter state
- `.btn-search`, `.btn-clear`: Action buttons

### Trending Articles
- `.trending-section`: Main container
- `.trending-grid`: Article grid
- `.trending-card`: Individual article card
- `.trending-badge`: Ranking badge
- `.trending-view-count`: View count display

### Lazy Loading
- `img[loading="lazy"]`: Lazy loadable images
- `.image-loaded`: Successfully loaded image
- `.image-error`: Failed image load
- `.image-placeholder`: Loading placeholder

## JavaScript APIs Reference

### FileUploadHandler
```javascript
const handler = new FileUploadHandler();
handler.handleFileSelect(event);
handler.validateFile(file, maxSize, allowedTypes);
```

### FormLoadingState
```javascript
const state = new FormLoadingState(buttonElement);
state.handleSubmit(event);
state.setLoading(true);
state.setLoading(false);
```

### Toast
```javascript
new Toast('success', 'Title', 'Message', duration);
new Toast('error', 'Title', 'Message');
new Toast('warning', 'Title', 'Message');
```

### LazyLoadManager
```javascript
window.lazyLoadManager = new LazyLoadManager(options);
window.lazyLoadManager.loadAllImages();
```

### ImageOptimizationHelper
```javascript
ImageOptimizationHelper.supportsWebP();
ImageOptimizationHelper.generateSrcSet(url, sizes);
ImageOptimizationHelper.preloadCriticalImages(selectors);
ImageOptimizationHelper.getOptimalImageSize();
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Upload feedback not showing | Verify `upload_feedback.html` is included |
| Trending articles empty | Ensure articles have views > 0 |
| Images not lazy loading | Use `data-src` instead of `src` |
| Cache not working | Clear browser cache (Ctrl+Shift+Del) |
| Search not filtering | Verify `selected_category` variable is passed |
| Loading spinner not animating | Check CSS is included in layout.html |

## Performance Tips

1. **Load Lazy Loading Script Last**
   ```html
   <!-- At the very end of your template -->
   {% include 'components/lazy_loading.html' %}
   ```

2. **Use Cache-Busting URLs for Static Assets**
   ```html
   <link rel="stylesheet" href="{{ cache_busting_url('css/style.css') }}">
   ```

3. **Preload Critical Images**
   ```html
   <img src="..." loading="eager"> <!-- For above-the-fold images -->
   ```

4. **Optimize Image Sizes in Database**
   - Use image_optimizer.py on upload
   - Serve appropriately sized images

## Testing Checklist

- [ ] Search form appears and accepts input
- [ ] Category filter works
- [ ] Sort options change article order
- [ ] Trending articles appear at top
- [ ] Upload feedback shows on file select
- [ ] Error toast shows for oversized files
- [ ] Loading spinner appears during form submission
- [ ] Images lazy load when scrolled into view
- [ ] View count increments on article view
- [ ] All links work correctly
