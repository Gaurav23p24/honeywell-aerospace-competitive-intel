"""
Honeywell Aerospace Competitive Analysis - Web Application
Phase 5: Modern Web UI with Flask
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from datetime import datetime
import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'honeywell-aerospace-analysis-2025'

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Run competitive analysis"""
    try:
        data = request.get_json()
        honeywell_product = data.get('honeywell_product', '')
        competitor_query = data.get('competitor_query', '')
        
        if not honeywell_product or not competitor_query:
            return jsonify({'error': 'Both product and competitor query are required'}), 400
        
        logger.info(f"Starting analysis: {honeywell_product} vs {competitor_query}")
        
        # Import and run the analysis workflow
        from workflow import run_analysis_workflow
        result = run_analysis_workflow(honeywell_product, competitor_query)
        
        # Return the result
        return jsonify({
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/reports')
def reports():
    """List available reports"""
    try:
        reports_dir = 'reports'
        if not os.path.exists(reports_dir):
            return jsonify({'reports': []})
        
        reports = []
        for filename in os.listdir(reports_dir):
            if filename.endswith('.pdf'):
                filepath = os.path.join(reports_dir, filename)
                stat = os.stat(filepath)
                reports.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # Sort by creation time (newest first)
        reports.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({'reports': reports})
        
    except Exception as e:
        logger.error(f"Failed to list reports: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_report(filename):
    """Download a specific report"""
    try:
        filepath = os.path.join('reports', filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'Report not found'}), 404
        
        return send_file(filepath, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Failed to download report: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status')
def status():
    """API status check"""
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('reports', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    print("Starting Honeywell Aerospace Competitive Analysis Web App")
    print("Phase 5: Modern Web UI")
    print("Access at: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
