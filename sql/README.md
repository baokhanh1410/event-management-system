# Thư mục SQL - Cấu trúc Database và Dữ liệu Mẫu

Thư mục này chứa các tệp SQL được sử dụng để định nghĩa cấu trúc cơ sở dữ liệu và điền dữ liệu mẫu ban đầu cho Hệ thống Quản lý Sự kiện.

## Các tệp và Chức năng

### `schema.sql`
Tệp này chứa toàn bộ định nghĩa của cấu trúc cơ sở dữ liệu (schema), bao gồm các bảng, mối quan hệ, chỉ mục (indexes), stored procedures và views.
*   **Bảng (Tables):** Định nghĩa các bảng cho `events`, `categories`, `event_categories`, `guests`, `organizers`, `registrations`, `venues`, `event_finance`, `roles`, `permissions`, `role_permissions`, và `users`.
*   **Chỉ mục & Khóa ngoại (Indexes & Foreign Keys):** Thiết lập các chỉ mục cần thiết để tối ưu hóa truy vấn và các ràng buộc khóa ngoại để duy trì tính toàn vẹn của dữ liệu.
*   **Stored Procedures:**
    *   `sp_check_in_guest`: Chứa logic để đánh dấu khách là "Đã check-in" một cách an toàn, đồng thời ngăn chặn việc check-in trùng lặp hoặc check-in cho những đăng ký không tồn tại.
*   **Views:**
    *   `vw_event_attendance_summary`: Tổng hợp dữ liệu đăng ký và điểm danh để cung cấp bản tóm tắt về tổng số lượt đăng ký và tỉ lệ tham dự cho mỗi sự kiện.
    *   `vw_finance_summary`: Tổng hợp dữ liệu tài chính, tính toán chi phí và doanh thu thực tế dựa trên số lượt check-in và đăng ký, sau đó tính toán lợi nhuận và mức chênh lệch cho mỗi sự kiện.
