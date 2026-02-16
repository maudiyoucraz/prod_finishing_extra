from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
import uuid
import os
import re

app = Flask(__name__)

# Configure PostgreSQL connection
postgres_conn = os.environ.get('POSTGRES_CONN', '')
if postgres_conn and postgres_conn.startswith('postgres://'):
    postgres_conn = postgres_conn.replace('postgres://', 'postgresql://', 1)

if not postgres_conn:
    # Build from individual components if POSTGRES_CONN not available
    username = os.environ.get('POSTGRES_USERNAME', 'postgres')
    password = os.environ.get('POSTGRES_PASSWORD', 'postgres')
    host = os.environ.get('POSTGRES_HOST', 'localhost')
    port = os.environ.get('POSTGRES_PORT', '5432')
    database = os.environ.get('POSTGRES_DATABASE', 'postgres')
    postgres_conn = f'postgresql://{username}:{password}@{host}:{port}/{database}'

app.config['SQLALCHEMY_DATABASE_URI'] = postgres_conn
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('RANDOM_SECRET', 'dev-secret-key-change-in-production')

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# ============================================
# MODELS
# ============================================

class Country(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    alpha2 = db.Column(db.String(2))
    alpha3 = db.Column(db.String(3))
    region = db.Column(db.String(50))

# Create tables if needed
with app.app_context():
    db.create_all()

# ============================================
# ENDPOINTS
# ============================================

@app.route('/api/ping', methods=['GET'])
def ping():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200

@app.route('/api/countries', methods=['GET'])
def get_countries():
    """Get list of countries with optional region filtering"""
    try:
        # Get region filter from query params (can be multiple)
        regions = request.args.getlist('region')
        
        # Validate regions if provided
        valid_regions = ['Europe', 'Africa', 'Americas', 'Oceania', 'Asia']
        if regions:
            for region in regions:
                if region and region not in valid_regions:
                    return jsonify({"reason": "Invalid region specified"}), 400
        
        # Query database
        if regions:
            countries = Country.query.filter(Country.region.in_(regions)).order_by(Country.alpha2).all()
        else:
            countries = Country.query.order_by(Country.alpha2).all()
        
        # Format response
        result = []
        for country in countries:
            country_data = {
                "name": country.name,
                "alpha2": country.alpha2,
                "alpha3": country.alpha3
            }
            # Only include region if it exists
            if country.region:
                country_data["region"] = country.region
            result.append(country_data)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({"reason": f"Error retrieving countries: {str(e)}"}), 500

@app.route('/api/countries/<string:alpha2>', methods=['GET'])
def get_country(alpha2):
    """Get a single country by alpha2 code"""
    try:
        country = Country.query.filter_by(alpha2=alpha2).first()
        
        if not country:
            return jsonify({"reason": "Country not found"}), 404
        
        country_data = {
            "name": country.name,
            "alpha2": country.alpha2,
            "alpha3": country.alpha3
        }
        # Only include region if it exists
        if country.region:
            country_data["region"] = country.region
        
        return jsonify(country_data), 200
    
    except Exception as e:
        return jsonify({"reason": f"Error retrieving country: {str(e)}"}), 500

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    # Parse SERVER_ADDRESS or use SERVER_PORT
    server_address = os.environ.get('SERVER_ADDRESS', '0.0.0.0:8080')
    server_port = os.environ.get('SERVER_PORT', '8080')
    
    # Try to parse host:port from SERVER_ADDRESS
    if ':' in server_address:
        host, port = server_address.rsplit(':', 1)
        port = int(port)
    else:
        host = '0.0.0.0'
        port = int(server_port)
    
    app.run(host=host, port=port)
