# 🌤️ World-Wide Weather Forecast Website
## 📖 Mục đích dự án (Project Purpose)
Dự án **Weather forecast website** là một ứng dụng web trực quan giúp người dùng tra cứu thông tin thời tiết hiện tại và dự báo thời tiết cho các thành phố trên toàn thế giới. Ứng dụng cung cấp các chỉ số thời tiết chi tiết, hỗ trợ đa ngôn ngữ (Anh/Việt), và cho phép người dùng lưu lại lịch sử tìm kiếm cũng như tạo danh sách các địa điểm yêu thích để tiện theo dõi.
## 🚀 Các tính năng nổi bật (Key Features)
- **Tra cứu thời tiết thời gian thực:** Cung cấp thông tin chi tiết như Nhiệt độ, Cảm giác như, Độ ẩm, Áp suất, Tầm nhìn, Tốc độ gió, Thời gian Mặt trời mọc/lặn, Khả năng có mưa và Chỉ số Chất lượng Không khí (AQI).
- **Dự báo chi tiết:** Hiển thị dự báo thời tiết theo giờ trong ngày và dự báo tổng quan trong 5 ngày tới.
- **Tự động nhận diện ngôn ngữ (I18n):** Hỗ trợ song ngữ Tiếng Anh và Tiếng Việt. Ứng dụng có cơ chế tự động nhận diện ngôn ngữ dựa trên từ khóa tìm kiếm (ví dụ: gõ tiếng Việt có dấu hoặc tên các thành phố Việt Nam) để điều chỉnh ngôn ngữ hiển thị của toàn bộ giao diện.
- **Lịch sử tìm kiếm & Danh sách Yêu thích (Database Integration):** 
  - Lưu lại 5 địa điểm tìm kiếm gần nhất.
  - Cho phép người dùng thêm/xóa các thành phố vào danh sách Yêu thích. Dữ liệu này được lưu trữ trong cơ sở dữ liệu SQLite.
- **Giao diện động (Dynamic UI):** Hình nền của trang web sẽ tự động thay đổi dựa trên tình trạng thời tiết thực tế hiện tại (trời nắng, mưa, nhiều mây, có tuyết, có bão, v.v.).
- **Tối ưu hóa tìm kiếm địa phương:** Xử lý tốt các tên thành phố đặc thù của Việt Nam (như Sa Pa, Đà Lạt), xử lý các trường hợp nhiễu dữ liệu API và tự động chuẩn hóa chuỗi (loại bỏ dấu) để tăng độ chính xác khi gọi OpenWeatherMap API.
## 🔍 Phân tích công nghệ (Technical Analysis)
Dự án được xây dựng dựa trên sự kết hợp giữa **Python** và **Flask framework** để làm máy chủ backend xử lý logic, kết nối trực tiếp với cơ sở dữ liệu **SQLite** (thông qua ORM **Flask-SQLAlchemy**) nhằm lưu trữ lịch sử tìm kiếm và danh sách địa điểm yêu thích của người dùng. Ở phía frontend, ứng dụng sử dụng giao diện **HTML5/CSS3** kết hợp cùng hệ thống render template **Jinja2** để tạo ra các trang web động, trực quan. Trái tim của hệ thống là việc gọi dữ liệu từ **OpenWeatherMap API**, cho phép ứng dụng truy xuất theo thời gian thực các số liệu thời tiết chi tiết, kết hợp cùng thư viện `python-dotenv` để bảo mật thông tin biến môi trường.
## ⚙️ Hướng dẫn cài đặt (Installation)
1. **Clone repository:**
   ```bash
   git clone <repository-url>
   cd Weather_forecast_website
   ```
2. **Tạo môi trường ảo và cài đặt thư viện:**
   ```bash
   python -m venv venv
   
   # Kích hoạt venv trên Windows:
   venv\Scripts\activate
   # Kích hoạt venv trên Mac/Linux:
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```
3. **Cấu hình API Key:**
   - Tạo file `.env` ở thư mục gốc của dự án.
   - Thêm các biến môi trường sau vào file `.env` (thay thế bằng API Key OpenWeatherMap của bạn):
     ```env
     OPENWEATHER_API_KEY=your_openweather_api_key_here
     SECRET_KEY=your_flask_secret_key_here
     ```
4. **Khởi chạy ứng dụng:**
   ```bash
   python app.py
   ```
   - Mở trình duyệt và truy cập địa chỉ: `http://127.0.0.1:5000`
## 📁 Cấu trúc dự án chính (Main Structure)
- `app.py`: File entry-point, khởi tạo ứng dụng Flask và định nghĩa các route (URL) chính.
- `models.py`: Định nghĩa các cấu trúc bảng trong cơ sở dữ liệu (`SearchHistory`, `Favorite`).
- `utils.py`: Chứa các hàm tiện ích cốt lõi, logic gọi API thời tiết, làm sạch dữ liệu, chuẩn hóa tên thành phố.
- `translations.py`: Chứa từ điển các từ vựng hỗ trợ cho hệ thống đa ngôn ngữ (Anh/Việt).
- `config.py`: File thiết lập cấu hình ứng dụng.
- `templates/`: Thư mục chứa các giao diện HTML.
- `static/`: Thư mục chứa CSS và các assets tĩnh.
