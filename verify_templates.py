#!/usr/bin/env python
"""Verify all template integrations are correct"""

from app import create_app
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError
import os

def verify_templates():
    # Load the app
    app = create_app()
    
    # Check templates
    template_path = os.path.join(app.root_path, 'templates')
    env = Environment(loader=FileSystemLoader(template_path))
    
    templates_to_check = [
        'home.html',
        'submit_article.html',
        'edit_article.html',
        'contact.html',
        'view_article.html',
        'admin_view_article.html'
    ]
    
    print("✅ Checking all templates for syntax errors...\n")
    
    all_valid = True
    for template_name in templates_to_check:
        try:
            template = env.get_template(template_name)
            print(f"✅ {template_name}: Valid syntax")
        except TemplateSyntaxError as e:
            print(f"❌ {template_name}: Syntax error at line {e.lineno}")
            print(f"   Error: {e.message}")
            all_valid = False
    
    print("\n" + "="*50)
    
    # Check for component includes
    components_to_find = {
        'home.html': [
            'components/advanced_search.html',
            'components/trending_articles.html',
            'components/lazy_loading.html'
        ],
        'submit_article.html': ['components/upload_feedback.html'],
        'edit_article.html': ['components/upload_feedback.html'],
        'contact.html': ['components/upload_feedback.html'],
        'view_article.html': ['components/lazy_loading.html'],
        'admin_view_article.html': ['components/lazy_loading.html'],
    }
    
    print("\n✅ Checking for component integrations...\n")
    
    for template_file, components in components_to_find.items():
        with open(os.path.join(template_path, template_file), 'r') as f:
            content = f.read()
            for component in components:
                if component in content:
                    print(f"✅ {template_file} includes {component}")
                else:
                    print(f"❌ {template_file} MISSING {component}")
                    all_valid = False
    
    print("\n" + "="*50)
    
    if all_valid:
        print("\n✅ ALL VERIFICATIONS PASSED!")
        print("\nTemplate Integration Status: COMPLETE ✅")
        return 0
    else:
        print("\n❌ SOME VERIFICATIONS FAILED")
        return 1

if __name__ == '__main__':
    exit(verify_templates())
