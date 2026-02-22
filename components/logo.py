"""
Logo component for Simply Lawverse
Renders SVG logos for headers, documents, and branding
"""

def render_logo(size='64', variant='full', color='black'):
    """
    Render SVG logo for Simply Lawverse
    
    Args:
        size: Logo size in pixels (default 64)
        variant: 'full' (with text), 'mark' (symbol only), 'monochrome'
        color: Color scheme - 'black', 'white', 'gold'
    
    Returns:
        SVG string
    """
    
    if variant == 'mark':
        return render_mark_logo(size, color)
    elif variant == 'monochrome':
        return render_monochrome_logo(size)
    else:
        return render_full_logo(size, color)


def render_mark_logo(size='64', color='black'):
    """
    Render the logo mark only (geometric symbol)
    Minimal, geometric design representing law and professionalism
    """
    color_map = {
        'black': '#000000',
        'white': '#FFFFFF',
        'gold': '#B8860B'
    }
    
    stroke_color = color_map.get(color, '#000000')
    
    svg = f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <!-- Outer circle frame -->
  <circle cx="32" cy="32" r="30" fill="none" stroke="{stroke_color}" stroke-width="1.5" opacity="0.8"/>
  
  <!-- Vertical element - represents balance and order -->
  <line x1="32" y1="12" x2="32" y2="52" stroke="{stroke_color}" stroke-width="2" stroke-linecap="round"/>
  
  <!-- Left diagonal accent -->
  <line x1="20" y1="20" x2="32" y2="44" stroke="{stroke_color}" stroke-width="1.5" stroke-linecap="round" opacity="0.9"/>
  
  <!-- Right diagonal accent -->
  <line x1="44" y1="20" x2="32" y2="44" stroke="{stroke_color}" stroke-width="1.5" stroke-linecap="round" opacity="0.9"/>
  
  <!-- Small accent marks at top -->
  <circle cx="20" cy="16" r="1.5" fill="{stroke_color}" opacity="0.7"/>
  <circle cx="44" cy="16" r="1.5" fill="{stroke_color}" opacity="0.7"/>
  
  <!-- Bottom accent - foundation element -->
  <line x1="18" y1="52" x2="46" y2="52" stroke="{stroke_color}" stroke-width="1.5" stroke-linecap="round"/>
</svg>'''
    
    return svg


def render_monochrome_logo(size='64'):
    """
    Render monochrome version (black only)
    For professional documents and printing
    """
    svg = f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <circle cx="32" cy="32" r="30" fill="none" stroke="#000000" stroke-width="1.5" opacity="0.8"/>
  <line x1="32" y1="12" x2="32" y2="52" stroke="#000000" stroke-width="2" stroke-linecap="round"/>
  <line x1="20" y1="20" x2="32" y2="44" stroke="#000000" stroke-width="1.5" stroke-linecap="round" opacity="0.9"/>
  <line x1="44" y1="20" x2="32" y2="44" stroke="#000000" stroke-width="1.5" stroke-linecap="round" opacity="0.9"/>
  <circle cx="20" cy="16" r="1.5" fill="#000000" opacity="0.7"/>
  <circle cx="44" cy="16" r="1.5" fill="#000000" opacity="0.7"/>
  <line x1="18" y1="52" x2="46" y2="52" stroke="#000000" stroke-width="1.5" stroke-linecap="round"/>
</svg>'''
    
    return svg


def render_full_logo(size='64', color='black'):
    """
    Render full logo with mark and firm name
    For main branding
    """
    color_map = {
        'black': '#000000',
        'white': '#FFFFFF',
        'gold': '#B8860B'
    }
    
    stroke_color = color_map.get(color, '#000000')
    
    svg = f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <!-- Logo mark -->
  <circle cx="32" cy="32" r="30" fill="none" stroke="{stroke_color}" stroke-width="1.5" opacity="0.8"/>
  <line x1="32" y1="12" x2="32" y2="52" stroke="{stroke_color}" stroke-width="2" stroke-linecap="round"/>
  <line x1="20" y1="20" x2="32" y2="44" stroke="{stroke_color}" stroke-width="1.5" stroke-linecap="round" opacity="0.9"/>
  <line x1="44" y1="20" x2="32" y2="44" stroke="{stroke_color}" stroke-width="1.5" stroke-linecap="round" opacity="0.9"/>
  <circle cx="20" cy="16" r="1.5" fill="{stroke_color}" opacity="0.7"/>
  <circle cx="44" cy="16" r="1.5" fill="{stroke_color}" opacity="0.7"/>
  <line x1="18" y1="52" x2="46" y2="52" stroke="{stroke_color}" stroke-width="1.5" stroke-linecap="round"/>
</svg>'''
    
    return svg


# Also provide standalone SVG file content for static files
LOGO_SVG = '''<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <!-- Outer circle frame -->
  <circle cx="32" cy="32" r="30" fill="none" stroke="#000000" stroke-width="1.5" opacity="0.8"/>
  
  <!-- Vertical element - represents balance and order -->
  <line x1="32" y1="12" x2="32" y2="52" stroke="#000000" stroke-width="2" stroke-linecap="round"/>
  
  <!-- Left diagonal accent -->
  <line x1="20" y1="20" x2="32" y2="44" stroke="#000000" stroke-width="1.5" stroke-linecap="round" opacity="0.9"/>
  
  <!-- Right diagonal accent -->
  <line x1="44" y1="20" x2="32" y2="44" stroke="#000000" stroke-width="1.5" stroke-linecap="round" opacity="0.9"/>
  
  <!-- Small accent marks at top -->
  <circle cx="20" cy="16" r="1.5" fill="#000000" opacity="0.7"/>
  <circle cx="44" cy="16" r="1.5" fill="#000000" opacity="0.7"/>
  
  <!-- Bottom accent - foundation element -->
  <line x1="18" y1="52" x2="46" y2="52" stroke="#000000" stroke-width="1.5" stroke-linecap="round"/>
</svg>'''

LOGO_SVG_GOLD = '''<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <circle cx="32" cy="32" r="30" fill="none" stroke="#B8860B" stroke-width="1.5" opacity="0.8"/>
  <line x1="32" y1="12" x2="32" y2="52" stroke="#B8860B" stroke-width="2" stroke-linecap="round"/>
  <line x1="20" y1="20" x2="32" y2="44" stroke="#B8860B" stroke-width="1.5" stroke-linecap="round" opacity="0.9"/>
  <line x1="44" y1="20" x2="32" y2="44" stroke="#B8860B" stroke-width="1.5" stroke-linecap="round" opacity="0.9"/>
  <circle cx="20" cy="16" r="1.5" fill="#B8860B" opacity="0.7"/>
  <circle cx="44" cy="16" r="1.5" fill="#B8860B" opacity="0.7"/>
  <line x1="18" y1="52" x2="46" y2="52" stroke="#B8860B" stroke-width="1.5" stroke-linecap="round"/>
</svg>'''

def get_logo_html(variant='mark', color='black', classes=''):
    """
    Returns HTML-safe logo markup for templates
    """
    svg_map = {
        ('mark', 'black'): render_mark_logo('64', 'black'),
        ('mark', 'gold'): render_mark_logo('64', 'gold'),
        ('mark', 'white'): render_mark_logo('64', 'white'),
    }
    
    svg = svg_map.get((variant, color), render_mark_logo('64', color))
    return f'<div class="{classes}">{svg}</div>'
