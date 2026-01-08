from flask import Flask, render_template, jsonify, request, redirect, url_for

app = Flask(__name__)

# Color configuration with descriptions
colors = {
    'R': {
        'name': 'Red',
        'code': '#FF0000',
        'description': 'Red is a powerful color that represents energy, passion, and urgency.',
        'importance': [
            'Stop signals & traffic lights - alerts people to danger',
            'Emergency services - ambulances, fire trucks symbolize urgency',
            'Marketing & branding - creates excitement and grabs attention',
            'Medical field - represents vitality and life force',
            'Sports & competition - evokes passion and intensity'
        ]
    },
    'G': {
        'name': 'Green',
        'code': '#00AA00',
        'description': 'Green symbolizes growth, nature, harmony, and renewal.',
        'importance': [
            'Go signals & traffic lights - permits action and movement',
            'Environmental movement - represents sustainability and eco-friendly practices',
            'Healthcare - symbolizes healing and wellness',
            'Finance - represents money and economic growth',
            'Agriculture & nature - connection to plants and natural resources'
        ]
    },
    'Y': {
        'name': 'Yellow',
        'code': '#FFFF00',
        'description': 'Yellow radiates optimism, happiness, and positive energy.',
        'importance': [
            'Warning signs - caution in construction and hazardous areas',
            'Education & positivity - encourages learning and creativity',
            'Solar energy - represents renewable and clean power',
            'Safety equipment - visibility in visibility vests and helmets',
            'Happiness & psychology - boosts mood and mental well-being'
        ]
    },
    'B': {
        'name': 'Blue',
        'code': '#0000FF',
        'description': 'Blue conveys trust, stability, calm, and professionalism.',
        'importance': [
            'Corporate branding - most trusted color for businesses',
            'Technology industry - represents innovation and reliability',
            'Medical & healthcare - associated with cleanliness and trust',
            'Ocean & water conservation - environmental awareness',
            'Mental health - calming effect that reduces stress and anxiety'
        ]
    }
}

@app.route('/')
def index():
    return render_template('index.html', colors=colors)

@app.route('/color/<color_code>')
def color_detail(color_code):
    if color_code not in colors:
        return redirect(url_for('index'))
    
    color = colors[color_code]
    return render_template('color_detail.html', 
                         color_code=color_code, 
                         color=color)

@app.route('/api/colors')
def get_colors():
    return jsonify(colors)

@app.route('/api/select-color', methods=['POST'])
def select_color():
    data = request.get_json()
    color_code = data.get('color')
    
    if color_code in colors:
        return jsonify({
            'success': True,
            'color': color_code,
            'name': colors[color_code]['name'],
            'code': colors[color_code]['code'],
            'redirect_url': url_for('color_detail', color_code=color_code)
        })
    
    return jsonify({'success': False, 'error': 'Invalid color'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
