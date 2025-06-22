# Hệ Thống Tổng Hợp Tin Tức AI Thông Minh

Hệ thống thông minh thu thập, phân tích và tổng hợp tin tức AI từ nhiều nguồn khác nhau bao gồm GitHub, arXiv, Facebook và X (Twitter).

## 🌟 Tính Năng Chính

- **Thu Thập Dữ Liệu Đa Nguồn**
  - Kho lưu trữ AI trending trên GitHub
  - Bài báo nghiên cứu AI mới nhất từ arXiv
  - Bài đăng liên quan đến AI trên Facebook
  - Nội dung AI từ X (Twitter)
  - Phát hiện và lọc trùng lặp thông minh

- **Xử Lý Nội Dung Thông Minh**
  - Gắn thẻ và phân loại nội dung tự động
  - Tóm tắt văn bản nâng cao
  - Tạo tiêu đề thông minh
  - Kiểm tra và xác thực chất lượng

- **Tổng Hợp Nội Dung**
  - Nhóm nội dung liên quan bằng phân tích ngữ nghĩa
  - Tổng hợp nghiên cứu tự động
  - Phân tích mối quan hệ đa nguồn
  - Tạo báo cáo "Hot Topics" từ nhiều nguồn

- **Giao Diện Web**
  - Dashboard sạch sẽ, responsive với tên "My Trender"
  - Lọc nội dung theo ngày
  - Lọc nội dung theo nguồn (GitHub, arXiv, Hot Topics)
  - Cập nhật nội dung thời gian thực

- **Giám Sát & Phân Tích**
  - Tích hợp metrics Prometheus
  - Dashboard Grafana
  - Giám sát hiệu suất
  - Kiểm tra sức khỏe hệ thống

## 🚀 Hướng Dẫn Cài Đặt Nhanh

### Yêu Cầu Hệ Thống

- Docker và Docker Compose
- PostgreSQL 13+
- Python 3.11+
- API keys cho:
  - Azure OpenAI
  - Voyage AI
  - Google Search API (tùy chọn)

### Bước 1: Tải Dự Án

```bash
git clone <repository-url>
cd netmind-stalk
```

### Bước 2: Thiết Lập Biến Môi Trường

Tạo file `.env` với nội dung sau:

```bash
# Cài đặt Azure OpenAI
AZURE_OPENAI_ENDPOINT=<endpoint-của-bạn>
AZURE_OPENAI_API_KEY=<key-của-bạn>
AZURE_OPENAI_API_VERSION=2024-08-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=<tên-deployment-của-bạn>

# Cài đặt Voyage AI
VOYAGE_API_KEY=<key-của-bạn>
VOYAGE_MODEL=voyage-large-2

# Cài đặt Cơ sở dữ liệu
DB_USER=<tên-người-dùng>
DB_PASSWORD=<mật-khẩu>
DB_HOST=db
DB_PORT=5432
DB_NAME=netmind_stalk

# Tùy chọn: Cài đặt Google Search
GOOGLE_SEARCH_API_KEY=<key-của-bạn>
GOOGLE_SEARCH_ENGINE_ID=<engine-id-của-bạn>

# Tùy chọn: Cài đặt Facebook
FACEBOOK_EMAIL=<email-của-bạn>
FACEBOOK_PASSWORD=<mật-khẩu-của-bạn>

# Tùy chọn: Cài đặt X (Twitter)
# X_PAGES được cấu hình sẵn trong config.py
```

### Bước 3: Khởi Chạy Hệ Thống

```bash
docker-compose up -d
```

Hệ thống sẽ tự động:
- Tạo cơ sở dữ liệu PostgreSQL
- Khởi chạy ứng dụng web
- Thiết lập Prometheus và Grafana
- Chạy migration để tạo bảng

## 📖 Hướng Dẫn Sử Dụng Chi Tiết

### 1. Truy Cập Giao Diện Web

Sau khi khởi chạy thành công, truy cập:
- **Dashboard chính (My Trender)**: http://localhost:5000
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000

### 2. Sử Dụng Dashboard "My Trender"

#### Xem Tin Tức Theo Ngày
1. Mở dashboard tại http://localhost:5000
2. Chọn ngày từ bộ lọc ngày ở đầu trang
3. Xem danh sách tin tức và báo cáo tổng hợp

#### Lọc Theo Nguồn
Dashboard cung cấp 4 bộ lọc chính:
- **All Sources**: Hiển thị tất cả nguồn
- **GitHub**: Kho lưu trữ AI trending (viền đen)
- **arXiv**: Bài báo nghiên cứu (viền đỏ)
- **Hot topic**: Báo cáo tổng hợp từ nhiều nguồn (viền cam)

#### Xem Báo Cáo Tổng Hợp
- Phần "Hot Topics" hiển thị các báo cáo được AI tổng hợp
- Mỗi báo cáo kết hợp thông tin từ nhiều nguồn liên quan
- Được đánh dấu bằng viền cam và tag "Hot topic"

### 3. Thu Thập Dữ Liệu Thủ Công

Để chạy quy trình thu thập dữ liệu thủ công:

```bash
# Chạy toàn bộ quy trình
python main.py

# Hoặc chạy từng bước riêng biệt
python -c "from agents.research import crawl_data; crawl_data()"
```

### 4. Quản Lý Cơ Sở Dữ Liệu

```bash
# Xem tóm tắt chi tiết cơ sở dữ liệu
python scripts/db_summary.py

# Xóa toàn bộ dữ liệu
python scripts/clear_database.py

# Sao lưu cơ sở dữ liệu
docker exec -it netmind-stalk-db-1 pg_dump -U <DB_USER> <DB_NAME> > backup.sql
```

### 5. Giám Sát Hệ Thống

#### Prometheus Metrics
- Truy cập http://localhost:9090
- Xem các metrics:
  - Số lượng request HTTP
  - Thời gian phản hồi
  - Lỗi hệ thống
  - Hiệu suất cơ sở dữ liệu

#### Grafana Dashboard
- Truy cập http://localhost:3000
- Đăng nhập với:
  - Username: `admin`
  - Password: `your_grafana_password`
- Xem dashboard về hiệu suất hệ thống

### 6. API Endpoints

Hệ thống cung cấp các API sau:

```bash
# Lấy tin tức theo ngày
GET http://localhost:5000/api/news/2024-01-15

# Kiểm tra sức khỏe hệ thống
GET http://localhost:5000/health

# Metrics Prometheus
GET http://localhost:5000/metrics
```

## 🔧 Cấu Hình Nâng Cao

### Tùy Chỉnh Quy Trình Thu Thập

Chỉnh sửa file `config.py` để thay đổi:

#### Cấu Hình ArXiv
```python
ARXIV_SUBJECT = ["cs.AI", "cs.IR", "cs.LG", "cs.MA", "cs.CV", "cs.CL"]
ARXIV_MAX_RESULTS = 1  # Số lượng bài báo thu thập
```

#### Cấu Hình GitHub
```python
GITHUB_MAX_REPOS = 1  # Số lượng repository thu thập
```

#### Cấu Hình Facebook
```python
FACEBOOK_PAGES = [
    "https://www.facebook.com/cung.AI.VN",
    "https://www.facebook.com/groups/DeepLearnng",
    "https://www.facebook.com/groups/artificialintelligenceforbusines"
]
MAX_FACEBOOK_POSTS = 5
```

#### Cấu Hình X (Twitter)
```python
X_PAGES = ["https://x.com/HyperspaceAI"]
MAX_X_POSTS = 5
```

### Thêm Nguồn Dữ Liệu Mới

1. Tạo crawler mới trong thư mục `crawlers/`
2. Thêm logic xử lý trong `agents/`
3. Cập nhật cấu hình trong `config.py`
4. Thêm model tương ứng trong `models/models.py`

### Tùy Chỉnh Giao Diện

Chỉnh sửa templates trong thư mục `templates/`:
- `index.html`: Trang chính "My Trender"
- CSS và JavaScript tùy chỉnh

## 🛠️ Phát Triển

### Thiết Lập Môi Trường Phát Triển

```bash
# Tạo môi trường ảo
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt

# Cài đặt Playwright browsers
playwright install chromium
playwright install-deps
```

### Chạy Ứng Dụng Locally

```bash
# Khởi chạy cơ sở dữ liệu
docker-compose up db -d

# Chạy ứng dụng
python run_local.py
```

### Kiểm Tra Logs

```bash
# Xem logs của tất cả services
docker-compose logs -f

# Xem logs của service cụ thể
docker-compose logs -f web
docker-compose logs -f db
```

## 🚨 Xử Lý Sự Cố

### Lỗi Thường Gặp

1. **Lỗi kết nối cơ sở dữ liệu**
   ```bash
   # Kiểm tra trạng thái database
   docker-compose ps
   # Restart database
   docker-compose restart db
   ```

2. **Lỗi API keys**
   - Kiểm tra file `.env` có đúng format
   - Xác nhận API keys còn hiệu lực

3. **Lỗi memory/disk space**
   ```bash
   # Dọn dẹp Docker
   docker system prune -a
   # Xóa volumes không sử dụng
   docker volume prune
   ```

4. **Lỗi Playwright (cho X crawler)**
   ```bash
   # Cài đặt lại Playwright
   playwright install chromium
   playwright install-deps
   ```

### Kiểm Tra Sức Khỏe Hệ Thống

```bash
# Kiểm tra tất cả services
curl http://localhost:5000/health

# Kiểm tra database
docker exec -it netmind-stalk-db-1 pg_isready -U <DB_USER>
```

## 📊 Cấu Trúc Dự Án

```
netmind-stalk/
├── agents/          # AI agents cho các tác vụ khác nhau
│   ├── research.py      # Thu thập dữ liệu
│   ├── process.py       # Xử lý và gắn thẻ
│   ├── summarize.py     # Tóm tắt nội dung
│   ├── inspector.py     # Kiểm tra chất lượng
│   ├── filter.py        # Lọc nội dung
│   └── social.py        # Phân tích xu hướng xã hội
├── crawlers/        # Bộ thu thập dữ liệu theo nguồn
│   ├── github_crawler.py    # Thu thập từ GitHub
│   ├── arxiv_crawler.py     # Thu thập từ arXiv
│   ├── facebook_crawler.py  # Thu thập từ Facebook
│   └── X_crawler.py         # Thu thập từ X (Twitter)
├── models/          # Models và schemas cơ sở dữ liệu
│   ├── models.py        # Pydantic và SQLAlchemy models
│   └── database.py      # Kết nối và thao tác database
├── templates/       # Templates giao diện web
│   └── index.html       # Trang chính "My Trender"
├── scripts/         # Công cụ quản lý
│   ├── db_summary.py    # Xem tóm tắt database
│   └── clear_database.py # Xóa database
├── tools/          # Công cụ tiện ích
├── utils/          # Hàm hỗ trợ
├── app.py          # Ứng dụng Flask chính
├── main.py         # Quy trình thu thập dữ liệu
├── config.py       # Cấu hình hệ thống
├── prompts.py      # Prompts cho AI
└── run_local.py    # Chạy ứng dụng locally
```

## 🔍 Các Nguồn Dữ Liệu Hiện Tại

### GitHub
- Thu thập các repository AI trending
- Số lượng: 1 repository mỗi lần chạy
- Nguồn: GitHub trending pages

### arXiv
- Thu thập bài báo nghiên cứu AI mới nhất
- Chủ đề: cs.AI, cs.IR, cs.LG, cs.MA, cs.CV, cs.CL
- Số lượng: 1 bài báo mỗi lần chạy

### Facebook
- Thu thập bài đăng từ các trang/groups AI
- Trang mặc định: cung.AI.VN, DeepLearnng, artificialintelligenceforbusines
- Số lượng: 5 bài đăng mỗi trang

### X (Twitter)
- Thu thập bài đăng từ các tài khoản AI
- Tài khoản mặc định: HyperspaceAI
- Số lượng: 5 bài đăng mỗi tài khoản
