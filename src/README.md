# Thư mục Src - Logic Backend & Tiện ích

Thư mục này chứa các module backend Python cốt lõi xử lý các kết nối cơ sở dữ liệu, thao tác dữ liệu (CRUD), xác thực, học máy (machine learning) và tạo dữ liệu.

## Các tệp và Chức năng

### `auth.py`
Xử lý toàn bộ các tính năng liên quan đến xác thực, phân quyền và bảo mật người dùng.
*   `hash_password()` & `verify_password()`: Các hàm tiện ích sử dụng `bcrypt` để băm (hash) và xác minh mật khẩu một cách an toàn.
*   `authenticate_user()`: Xác thực thông tin đăng nhập của người dùng so với cơ sở dữ liệu và lấy ra thông tin chi tiết, vai trò cùng danh sách các quyền hạn được cấp.
*   `register_new_guest_user()`: Xử lý luồng đăng ký cho người dùng "Khách" mới, chèn các bản ghi vào cả hai bảng `guests` và `users` một cách an toàn.
*   `has_permission()`: Kiểm tra xem người dùng hiện đang đăng nhập có sở hữu quyền hạn cụ thể bắt buộc để thực hiện một hành động hoặc xem một trang hay không.

### `connection.py`
Quản lý kết nối SQLAlchemy tới cơ sở dữ liệu MySQL.
*   `get_db_engine()`: Đọc thông tin đăng nhập cơ sở dữ liệu từ các biến môi trường (tệp `.env`) và tạo một đối tượng SQLAlchemy engine ở dạng singleton.
*   `get_session()`: Cung cấp một đối tượng phiên làm việc (session object) của SQLAlchemy (`Session()`) được sử dụng bởi các module khác để thực thi các câu truy vấn và giao dịch SQL.

### `crud.py`
Chứa tất cả các thao tác Create (Tạo), Read (Đọc), Update (Cập nhật), và Delete (Xóa). Tệp này tương tác trực tiếp với cơ sở dữ liệu bằng cách sử dụng các truy vấn SQL thô thông qua SQLAlchemy và Pandas.
*   **Quản lý Sự kiện:** Các hàm như `get_all_events()`, `create_event()`, `get_event_by_id()`, và `update_event()` để quản lý vòng đời của các sự kiện.
*   **Điểm danh & Đăng ký:** Các hàm như `get_available_events_for_guest()`, `get_registrations_by_event()`, `create_registration()`, và `check_in_guest()` (hàm gọi stored procedure) để xử lý việc tham gia của khách.
*   **Quản lý Tài chính:** Các hàm như `get_finance_summary()`, `get_finance_by_event()`, và `update_finance()` để theo dõi ngân sách và chi phí.
*   **Chuẩn bị Dữ liệu:** `get_data_for_recommendation()` thu thập dữ liệu đăng ký và điểm danh trong quá khứ được sử dụng để huấn luyện mô hình machine learning.

### `ml_models.py`
Chứa logic của hệ thống gợi ý bằng Machine Learning.
*   `preprocess_features()`: Chuẩn bị tập dữ liệu bằng cách áp dụng phương pháp One-Hot Encoding cho các thể loại sự kiện.
*   `train_xgboost_recommender()`: Huấn luyện một mô hình `XGBClassifier` (XGBoost) sử dụng dữ liệu lịch sử để dự đoán khả năng một khách hàng sẽ tham dự một sự kiện.
*   `get_recommended_events()`: Sử dụng mô hình đã được huấn luyện để dự đoán xác suất tham dự cho các sự kiện sắp tới mà khách chưa đăng ký, trả về top N các gợi ý.

### `sample_data.py`
Một script tiện ích được sử dụng để tạo dữ liệu giả cho ứng dụng bằng thư viện `Faker`.
*   `generate_seed_data()`: Tự động tạo các dữ liệu mẫu thực tế (địa điểm, ban tổ chức, sự kiện, khách, v.v.) và ghi các câu lệnh `INSERT` SQL tương ứng vào tệp `sql/seed.sql`. Nó cũng xử lý các logic để làm cho giá cả, ngân sách và tỉ lệ tham dự trở nên thực tế một cách tương đối.
*   `insert_seed_data()`: Đọc tệp `sql/seed.sql` và thực thi các câu lệnh theo từng lô (batch) để điền dữ liệu trực tiếp vào cơ sở dữ liệu.
