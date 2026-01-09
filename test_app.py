import unittest
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, colors


class ColorPollTestCase(unittest.TestCase):
    """Unit tests for the Color Poll Flask application"""
    
    def setUp(self):
        """Set up test client and context"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests"""
        self.app_context.pop()
    
    # ==================== Route Tests ====================
    
    def test_index_page_loads(self):
        """Test that index page loads successfully"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Select Your Favorite Color', response.data)
    
    def test_index_contains_color_options(self):
        """Test that index page contains all color options"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Red', response.data)
        self.assertIn(b'Green', response.data)
        self.assertIn(b'Yellow', response.data)
        self.assertIn(b'Blue', response.data)
    
    def test_color_detail_page_red(self):
        """Test color detail page for Red"""
        response = self.client.get('/color/R')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Red', response.data)
        self.assertIn(b'Real-World Importance', response.data)
    
    def test_color_detail_page_green(self):
        """Test color detail page for Green"""
        response = self.client.get('/color/G')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Green', response.data)
    
    def test_color_detail_page_yellow(self):
        """Test color detail page for Yellow"""
        response = self.client.get('/color/Y')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Yellow', response.data)
    
    def test_color_detail_page_blue(self):
        """Test color detail page for Blue"""
        response = self.client.get('/color/B')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Blue', response.data)
    
    def test_invalid_color_redirects(self):
        """Test that invalid color code redirects to index"""
        response = self.client.get('/color/Z', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
    
    # ==================== API Tests ====================
    
    def test_api_get_colors(self):
        """Test /api/colors endpoint returns all colors"""
        response = self.client.get('/api/colors')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('R', data)
        self.assertIn('G', data)
        self.assertIn('Y', data)
        self.assertIn('B', data)
    
    def test_api_colors_has_required_fields(self):
        """Test that API returns colors with required fields"""
        response = self.client.get('/api/colors')
        data = json.loads(response.data)
        
        for color_code in ['R', 'G', 'Y', 'B']:
            self.assertIn('name', data[color_code])
            self.assertIn('code', data[color_code])
            self.assertIn('description', data[color_code])
            self.assertIn('importance', data[color_code])
    
    def test_api_select_color_valid(self):
        """Test /api/select-color with valid color"""
        response = self.client.post(
            '/api/select-color',
            data=json.dumps({'color': 'R'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['color'], 'R')
        self.assertEqual(data['name'], 'Red')
        self.assertIn('#FF0000', data['code'])
    
    def test_api_select_color_all_valid(self):
        """Test /api/select-color with all valid colors"""
        for color in ['R', 'G', 'Y', 'B']:
            response = self.client.post(
                '/api/select-color',
                data=json.dumps({'color': color}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['color'], color)
    
    def test_api_select_color_invalid(self):
        """Test /api/select-color with invalid color"""
        response = self.client.post(
            '/api/select-color',
            data=json.dumps({'color': 'Z'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('Invalid color', data['error'])
    
    def test_api_select_color_missing_color(self):
        """Test /api/select-color without color parameter"""
        response = self.client.post(
            '/api/select-color',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    # ==================== Data Validation Tests ====================
    
    def test_color_data_structure(self):
        """Test that color data has correct structure"""
        for color_code, color_data in colors.items():
            self.assertIn('name', color_data)
            self.assertIn('code', color_data)
            self.assertIn('description', color_data)
            self.assertIn('importance', color_data)
            
            self.assertIsInstance(color_data['name'], str)
            self.assertIsInstance(color_data['code'], str)
            self.assertIsInstance(color_data['description'], str)
            self.assertIsInstance(color_data['importance'], list)
            self.assertGreater(len(color_data['importance']), 0)
    
    def test_color_codes_are_valid(self):
        """Test that color codes match expected values"""
        expected_codes = {'R', 'G', 'Y', 'B'}
        actual_codes = set(colors.keys())
        self.assertEqual(expected_codes, actual_codes)
    
    def test_color_hex_codes_valid_format(self):
        """Test that color hex codes are in valid format"""
        import re
        hex_pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')
        
        for color_code, color_data in colors.items():
            self.assertTrue(
                hex_pattern.match(color_data['code']),
                f"Invalid hex code for {color_code}: {color_data['code']}"
            )


class ColorPollIntegrationTests(unittest.TestCase):
    """Integration tests for complete workflows"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_complete_color_selection_workflow(self):
        """Test complete workflow: visit poll -> select color -> view details"""
        # 1. Load poll page
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # 2. Fetch color data via API
        response = self.client.get('/api/colors')
        self.assertEqual(response.status_code, 200)
        colors_data = json.loads(response.data)
        self.assertGreater(len(colors_data), 0)
        
        # 3. Select a color
        response = self.client.post(
            '/api/select-color',
            data=json.dumps({'color': 'G'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # 4. Visit detail page
        response = self.client.get('/color/G')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Green', response.data)


if __name__ == '__main__':
    unittest.main()
