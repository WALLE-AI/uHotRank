"""Test export utility functions."""

import json
import csv
from io import StringIO
from backend.utils.export import (
    export_to_json,
    export_to_csv,
    export_to_excel,
    select_fields,
    flatten_article
)


def test_select_fields():
    """Test field selection functionality."""
    articles = [
        {'id': '1', 'title': 'Test 1', 'content': 'Content 1', 'category': 'tech'},
        {'id': '2', 'title': 'Test 2', 'content': 'Content 2', 'category': 'news'}
    ]
    
    # Select specific fields
    selected = select_fields(articles, ['id', 'title'])
    assert len(selected) == 2
    assert 'id' in selected[0]
    assert 'title' in selected[0]
    assert 'content' not in selected[0]
    print("✓ Field selection works")


def test_flatten_article():
    """Test article flattening functionality."""
    article = {
        'id': '1',
        'title': 'Test Article',
        'content': 'Test content',
        'category': 'tech',
        'published_time': '2024-01-01',
        'created_at': '2024-01-01T00:00:00',
        'tech_detection': {
            'is_tech_related': True,
            'categories': ['AI', 'ML'],
            'confidence': 0.95,
            'matched_keywords': ['python', 'machine learning']
        },
        'content_analysis': {
            'keywords': ['AI', 'technology'],
            'topics': ['artificial intelligence'],
            'summary': 'A test summary',
            'sentiment': 'positive',
            'category': 'Technology',
            'entities': [
                {'name': 'Python', 'type': 'technology'},
                {'name': 'Google', 'type': 'organization'}
            ]
        }
    }
    
    flattened = flatten_article(article)
    assert flattened['id'] == '1'
    assert flattened['is_tech_related'] == True
    assert flattened['tech_categories'] == 'AI, ML'
    assert flattened['sentiment'] == 'positive'
    assert 'Python' in flattened['entities']
    print("✓ Article flattening works")


def test_export_to_json():
    """Test JSON export functionality."""
    articles = [
        {'id': '1', 'title': 'Test 1', 'content': 'Content 1'},
        {'id': '2', 'title': 'Test 2', 'content': 'Content 2'}
    ]
    
    # Export all fields
    json_bytes = export_to_json(articles)
    json_data = json.loads(json_bytes.decode('utf-8'))
    assert len(json_data) == 2
    assert json_data[0]['id'] == '1'
    print("✓ JSON export works")
    
    # Export selected fields
    json_bytes = export_to_json(articles, fields=['id', 'title'])
    json_data = json.loads(json_bytes.decode('utf-8'))
    assert 'id' in json_data[0]
    assert 'title' in json_data[0]
    assert 'content' not in json_data[0]
    print("✓ JSON export with field selection works")


def test_export_to_csv():
    """Test CSV export functionality."""
    articles = [
        {
            'id': '1',
            'title': 'Test 1',
            'content': 'Content 1',
            'category': 'tech',
            'published_time': '2024-01-01',
            'created_at': '2024-01-01T00:00:00'
        },
        {
            'id': '2',
            'title': 'Test 2',
            'content': 'Content 2',
            'category': 'news',
            'published_time': '2024-01-02',
            'created_at': '2024-01-02T00:00:00'
        }
    ]
    
    # Export to CSV
    csv_bytes = export_to_csv(articles)
    csv_str = csv_bytes.decode('utf-8')
    
    # Parse CSV
    reader = csv.DictReader(StringIO(csv_str))
    rows = list(reader)
    assert len(rows) == 2
    assert rows[0]['id'] == '1'
    assert rows[0]['title'] == 'Test 1'
    print("✓ CSV export works")


def test_export_to_excel():
    """Test Excel export functionality."""
    articles = [
        {
            'id': '1',
            'title': 'Test 1',
            'content': 'Content 1',
            'category': 'tech',
            'published_time': '2024-01-01',
            'created_at': '2024-01-01T00:00:00'
        }
    ]
    
    # Export to Excel
    excel_bytes = export_to_excel(articles)
    assert len(excel_bytes) > 0
    assert excel_bytes[:2] == b'PK'  # Excel files start with PK (ZIP format)
    print("✓ Excel export works")
    
    # Test empty export
    empty_bytes = export_to_excel([])
    assert len(empty_bytes) > 0
    print("✓ Empty Excel export works")


def test_nested_field_selection():
    """Test nested field selection with dot notation."""
    articles = [
        {
            'id': '1',
            'title': 'Test',
            'content_analysis': {
                'summary': 'Test summary',
                'sentiment': 'positive'
            }
        }
    ]
    
    selected = select_fields(articles, ['id', 'content_analysis.summary'])
    assert 'id' in selected[0]
    assert 'content_analysis.summary' in selected[0]
    assert selected[0]['content_analysis.summary'] == 'Test summary'
    print("✓ Nested field selection works")


if __name__ == '__main__':
    print("Testing export utilities...")
    print()
    
    test_select_fields()
    test_flatten_article()
    test_export_to_json()
    test_export_to_csv()
    test_export_to_excel()
    test_nested_field_selection()
    
    print()
    print("All tests passed! ✓")
