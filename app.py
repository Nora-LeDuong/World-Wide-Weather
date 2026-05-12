from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from config import Config
from models import db, SearchHistory, Favorite
from utils import get_weather_data, VIETNAMESE_CITIES
from datetime import datetime
import re
from translations import translations

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()

def detect_language(text):
    if not text:
        return 'en'
    # Check if city is in Vietnamese cities list
    if text.lower().strip() in VIETNAMESE_CITIES:
        return 'vi'
    # Detect Vietnamese characters
    if re.search(r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', text.lower()):
        return 'vi'
    return 'en'

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    favorites = Favorite.query.all()
    history = SearchHistory.query.order_by(SearchHistory.searched_at.desc()).limit(5).all()
    lang = 'en' # Default language

    if request.method == 'POST':
        city = request.form.get('city')
        if city:
            lang = detect_language(city)
            weather_data = get_weather_data(city, lang)
            if not weather_data.get('error'):
                # Save to history
                new_search = SearchHistory(city_name=weather_data['current']['city'])
                db.session.add(new_search)
                db.session.commit()
    
    # Check for query param
    city_param = request.args.get('city')
    if city_param and not weather_data:
         lang = detect_language(city_param)
         weather_data = get_weather_data(city_param, lang)

    current_translations = translations[lang]

    return render_template('index.html', weather=weather_data, favorites=favorites, history=history, t=current_translations, lang=lang)

@app.route('/add_favorite', methods=['POST'])
def add_favorite():
    city = request.form.get('city')
    if city:
        # Check if already exists
        existing = Favorite.query.filter_by(city_name=city).first()
        if not existing:
            new_fav = Favorite(city_name=city)
            db.session.add(new_fav)
            db.session.commit()
            flash(f'Added {city} to favorites!' if detect_language(city) == 'en' else f'Đã thêm {city} vào danh sách yêu thích!', 'success')
        else:
            flash(f'{city} is already in favorites.' if detect_language(city) == 'en' else f'{city} đã có trong danh sách yêu thích.', 'info')
    return redirect(url_for('index', city=city))

@app.route('/remove_favorite/<int:fav_id>')
def remove_favorite(fav_id):
    fav = Favorite.query.get_or_404(fav_id)
    city_name = fav.city_name  # Save before deleting
    db.session.delete(fav)
    db.session.commit()
    is_vi = re.search(r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', city_name.lower())
    msg = f'Đã xóa {city_name} khỏi danh sách yêu thích.' if is_vi else f'Removed {city_name} from favorites.'
    flash(msg, 'success') 
    return redirect(url_for('index'))

@app.route('/clear_history')
def clear_history():
    SearchHistory.query.delete()
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
