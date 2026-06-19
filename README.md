# ToyCity — Website Bán Hàng (Django)

ToyCity là một dự án website bán hàng (cửa hàng đồ chơi) được xây dựng trên nền tảng **Django**, hỗ trợ quản lý danh mục, sản phẩm, giỏ hàng, tài khoản người dùng và tích hợp nhiều công cụ quản lý dữ liệu CSV tiện ích cho Quản trị viên (Admin).

---

## 🚀 Các Tính Năng Chính

### Giao Diện Khách Hàng (User)
- **Xem & Tìm kiếm sản phẩm**: Lọc sản phẩm theo danh mục và sắp xếp theo giá cả.
- **Phân trang (Pagination)**: Tự động phân trang hiển thị tối đa **8 sản phẩm/trang** để tối ưu hóa tốc độ tải và trải nghiệm người dùng.
- **Quản lý giỏ hàng**: Thêm/cập nhật số lượng sản phẩm trong giỏ hàng.
- **Đăng ký / Đăng nhập / Xác thực Email**: Hệ thống đăng ký tài khoản và gửi link xác thực email tự động kích hoạt tài khoản.
- **Hồ sơ cá nhân**: Đổi thông tin cá nhân, mật khẩu và cập nhật ảnh đại diện (avatar) ngay lập tức.

### Giao Diện Quản Trị (Admin)
- **Quản lý Danh mục & Sản phẩm**: Thêm, sửa, xóa các danh mục và sản phẩm.
- **Quản lý Tài khoản**: Quản lý thông tin tài khoản người dùng, phân quyền (ADMIN/USER), kích hoạt hoặc khóa tài khoản.
- **Nút dropdown "Dữ liệu" tích hợp**:
  - **Xuất dữ liệu (Export CSV)**: Tải xuống file CSV thông tin Danh mục, Sản phẩm hoặc Tài khoản (tự động đính kèm UTF-8 BOM hiển thị chuẩn tiếng Việt trên Excel).
  - **Nhập dữ liệu (Import CSV)**: Tải lên file CSV để cập nhật hàng loạt dữ liệu. Tự động kiểm tra trùng lặp thông tin (nếu trùng tên/username sẽ cập nhật, chưa có sẽ tạo mới) và thông báo kết quả bằng Toast Notification trực quan.

---

## 📜 Các Kịch Bản JS & Tương Tác Giao Diện (Scripts)

Dự án tích hợp các kịch bản JavaScript để tối ưu hóa trải nghiệm người dùng (UX) và tự động hóa các thao tác:

1. **Xem trước ảnh đại diện (Avatar Preview Script)**:
   - **Tệp tin**: [profile.html](file:///d:/WORKSPACE/Python/websitebanhang/templates/auth/profile.html)
   - **Cách thức hoạt động**: Khi người dùng nhấn nút chọn file ảnh mới, hàm `previewImage(input)` sử dụng API `FileReader` để đọc tệp tin cục bộ dưới định dạng DataURL và cập nhật trực tiếp thẻ `<img>` đại diện ngay lập tức mà không cần tải lại trang.

2. **Kích hoạt tự động Nhập dữ liệu (Auto-Submit Import CSV)**:
   - **Tệp tin**: [list.html (Sản phẩm)](file:///d:/WORKSPACE/Python/websitebanhang/templates/product/list.html), [list.html (Danh mục)](file:///d:/WORKSPACE/Python/websitebanhang/templates/category/list.html), [list.html (Tài khoản)](file:///d:/WORKSPACE/Python/websitebanhang/templates/account/list.html)
   - **Cách thức hoạt động**: Để đơn giản hóa giao diện, form nhập CSV được ẩn đi. Khi Admin nhấn vào "Nhập CSV" trong dropdown, JS sẽ giả lập hành động nhấp chuột (`.click()`) vào thẻ `<input type="file">`. Ngay sau khi tệp tin `.csv` được chọn (`onchange`), lệnh JS tự động gọi `.submit()` gửi form lên máy chủ mà không cần thêm bước xác nhận thủ công.

3. **Hệ thống Toast Notification tự động kết hợp Django Messages**:
   - **Tệp tin**: [base.html](file:///d:/WORKSPACE/Python/websitebanhang/templates/base.html)
   - **Cách thức hoạt động**: Định nghĩa hàm hiển thị thông báo popup trượt `showToast(message, type)`. Ở cuối trang, mã template Django tự động lặp qua tập hợp `messages` (gửi từ server sau khi Import/Export thành công, hoặc cập nhật hồ sơ thất bại) để kết xuất thành mã JavaScript gọi hàm `showToast` tương ứng với cấp độ (`success`, `error`, `warning`).

---

## 🛠️ Công Nghệ Sử Dụng

- **Backend**: Python 3.x, Django 6.0
- **Database**: SQLite (Mặc định cho môi trường phát triển)
- **Frontend**: HTML5, Vanilla CSS (Design System tùy chỉnh phong cách Inter & Boxicons), JavaScript ES6.
- **Thư viện tích hợp**: `pillow` (xử lý hình ảnh), `csv` (xử lý tệp dữ liệu).

---

## 📦 Hướng Dẫn Cài Đặt & Chạy Dự Án

### 1. Chuẩn bị môi trường
Yêu cầu máy tính đã cài đặt sẵn **Python 3.x**.

Mở terminal tại thư mục gốc của dự án:
```bash
# Khởi tạo môi trường ảo (venv) nếu chưa có
python -m venv venv

# Kích hoạt môi trường ảo
# Trên Windows (Command Prompt):
venv\Scripts\activate.bat
# Trên Windows (PowerShell):
venv\Scripts\Activate.ps1
# Trên macOS/Linux:
source venv/bin/activate
```

### 2. Cài đặt các thư viện phụ thuộc
```bash
pip install -r requirements.txt
```

### 3. Đồng bộ Cơ sở dữ liệu (Migrations)
```bash
python manage.py migrate
```

### 4. Khởi chạy Server cục bộ
```bash
python manage.py runserver
```

Truy cập trang web tại địa chỉ: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### 5. Các Lệnh Quản Trị Hệ Thống (Custom CLI Commands)

Dự án cung cấp một bộ công cụ dòng lệnh (Django Management Commands) được thiết lập sẵn trong `app/management/commands/` phục vụ cho việc quản trị dữ liệu thông qua cửa sổ Terminal:

- **Tạo tài khoản Admin mới**:
  ```bash
  python manage.py createadmin
  ```
  *Nhập họ tên, tên đăng nhập, email từ terminal; hệ thống tự sinh mật khẩu ngẫu nhiên 8 ký tự.*

- **Hiển thị danh sách Admin**:
  ```bash
  python manage.py showadmin
  ```
  *Liệt kê danh sách tất cả các tài khoản có vai trò ADMIN hiện có trong hệ thống.*

- **Đổi mật khẩu tài khoản Admin**:
  ```bash
  python manage.py changepasswordadmin
  ```
  *Thay đổi mật khẩu thủ công cho một tài khoản Admin cụ thể.*

- **Đặt lại mật khẩu Admin**:
  ```bash
  python manage.py resetpasswordadmin
  ```
  *Reset mật khẩu của một tài khoản Admin sang mật khẩu ngẫu nhiên mới và hiển thị ra màn hình.*

- **Xóa tài khoản Admin**:
  ```bash
  python manage.py deleteadmin
  ```
  *Xóa tài khoản Admin khỏi hệ thống thông qua tên đăng nhập.*

- **Hiển thị danh sách các bảng cơ sở dữ liệu**:
  ```bash
  python manage.py showtables
  ```
  *Liệt kê tất cả các bảng dữ liệu hiện có trong ứng dụng.*

- **Xem chi tiết bản ghi của bảng**:
  ```bash
  python manage.py viewtable
  ```
  *Lựa chọn bảng để xem các dữ liệu dòng dưới định dạng cấu trúc chi tiết.*

---

## 📁 Cấu Trúc Thư Mục Dự Án

```text
websitebanhang/
├── app/                  # Logic chính của website (Models, Views, URLs, Migrations)
│   ├── views/            # Các view xử lý logic (Phân chia theo Module)
│   ├── models.py         # Cấu trúc cơ sở dữ liệu (Category, Product, Account...)
│   └── urls.py           # Định tuyến URL của website
├── config/               # Cấu hình dự án Django (settings.py, urls.py, wsgi.py)
├── media/                # Thư mục lưu trữ hình ảnh tải lên (avatars, products, categories)
├── static/               # File tĩnh (CSS, JS, Images hệ thống)
│   └── css/style.css     # Design System & CSS tùy chỉnh cho toàn hệ thống
├── templates/            # File giao diện HTML
│   ├── base.html         # Giao diện khung dùng chung (Header, Footer, Toast)
│   ├── account/          # Template quản trị tài khoản
│   ├── auth/             # Template liên quan đến đăng nhập, hồ sơ, xác thực
│   ├── category/         # Template quản lý danh mục
│   └── product/          # Template danh sách và chi tiết sản phẩm
├── manage.py             # Script quản trị dự án Django
└── requirements.txt      # Khai báo các thư viện Python phụ thuộc
```
