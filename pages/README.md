# Thư mục Pages - Giao diện người dùng (Streamlit)

Thư mục này chứa các trang giao diện người dùng cho Hệ thống Quản lý Sự kiện, được xây dựng bằng [Streamlit](https://streamlit.io/). Mỗi tệp đại diện cho một trang/tab khác nhau trong ứng dụng.

## Các tệp và Chức năng

### `0_Login.py`
Đây là điểm khởi đầu của ứng dụng, xử lý việc xác thực và đăng ký người dùng.
*   **Tab Đăng nhập:** Cho phép người dùng hiện tại (Admin, Staff, hoặc Guest) xác thực an toàn. Sử dụng hàm `authenticate_user()` từ `src.auth`.
*   **Tab Đăng ký Guest:** Cho phép người dùng mới tạo tài khoản "Khách" (Guest). Sử dụng hàm `register_new_guest_user()` từ `src.auth`.
*   **Trạng thái Phiên (Session State):** Quản lý trạng thái đăng nhập của người dùng và hiển thị thông tin chi tiết (User ID, Role, Guest ID) sau khi đăng nhập thành công.

### `1_Events.py`
Trang này dành riêng cho việc lập lịch và quản lý Sự kiện. Các tính năng sẽ thay đổi tùy thuộc vào vai trò của người dùng đã đăng nhập.
*   **Chế độ xem Công khai:** Hiển thị tất cả các sự kiện hiện có trong một bảng (ID, Tên, Thể loại, Ngày, Địa điểm, Ban tổ chức, Trạng thái, Giá).
*   **Tính năng cho Khách (Guest):** 
    *   **Sự kiện của tôi:** Hiển thị các sự kiện mà khách đã đăng ký thành công.
    *   **Gợi ý:** Sử dụng mô hình Machine Learning XGBoost (`get_recommended_events` từ `src.ml_models`) để đề xuất các sự kiện sắp tới dựa trên hồ sơ của khách.
    *   **Form Đăng ký:** Cho phép khách đăng ký tham gia các sự kiện.
*   **Tính năng cho Admin/Staff (Tạo mới):** Form để tạo một sự kiện mới (Tên, Ngày, Thể loại, Địa điểm, Ban tổ chức, Thời gian, Giá). Sử dụng hàm `create_event()` từ `src.crud`.
*   **Tính năng cho Admin/Staff (Chỉnh sửa):** Form để cập nhật thông tin của một sự kiện đã có dựa trên ID Sự kiện.

### `2_Attendence.py`
Trang này xử lý việc đăng ký của khách và điểm danh.
*   **Tab 1 - Danh sách Đăng ký:** Hiển thị danh sách khách đã đăng ký cho một sự kiện được chọn. Khách chỉ có thể xem danh sách đăng ký của chính mình.
*   **Tab 2 - Check-in:** Cho phép nhân viên có thẩm quyền (với quyền `attendance_checkin`) đánh dấu khách là "Đã check-in" khi họ đến.
*   **Tab 3 - Đăng ký Mới:** Cho phép nhân viên có thẩm quyền đăng ký thủ công cho một khách vào một sự kiện.
*   **Tab 4 - Thống kê:** Hiển thị các chỉ số và tỉ lệ tham dự ở các sự kiện khác nhau (Chỉ dành cho Admin/Staff).

### `3_Finance.py`
Trang này xử lý các khía cạnh tài chính của sự kiện. Quyền truy cập bị giới hạn ở những người dùng có quyền `manage_finance` hoặc `view_analytics`.
*   **Tab 1 - Tổng quan:** Hiển thị các thẻ KPI (Tổng Ngân sách, Chi phí, Doanh thu, Lợi nhuận Ròng) và biểu đồ cột so sánh ngân sách dự kiến với chi phí thực tế và doanh thu với chi phí.
*   **Tab 2 - Chi tiết:** Hiển thị bảng dữ liệu toàn diện với các chỉ số tài chính cho từng sự kiện. Sử dụng định dạng có điều kiện để làm nổi bật lợi nhuận (màu xanh) và thua lỗ (màu đỏ).
*   **Tab 3 - Chỉnh sửa:** Cho phép người dùng có quyền `manage_finance` cập nhật "Ngân sách Dự kiến" và "Chi phí Thực tế" cho từng sự kiện. (Doanh thu được tính tự động dựa trên số lượng check-in).
