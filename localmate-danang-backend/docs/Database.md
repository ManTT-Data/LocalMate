### **1\. Overview**

**Chính:**

* `users` – thông tin tài khoản & profile cơ bản.

* `driver_profiles` – thông tin bổ sung cho tài xế (map 1–1 với `users` role driver).

* `itineraries` – itinerary tổng quát (trip của user).

* `itinerary_stops` – từng điểm dừng trong itinerary (trỏ sang Neo4j `place_id`).

* `bookings` – booking thực hiện qua MCP (Grab, hotel, ticket…).

* `affiliate_programs` – thông tin venues/đối tác có hoa hồng (cũng trỏ sang `place_id`).

**Quan hệ (logical ER):**

* `users` 1–N `itineraries`

* `itineraries` 1–N `itinerary_stops`

* `users` 1–N `bookings`

* `itineraries` 1–N `bookings` (optional FK)

* `users` 1–1 `driver_profiles`

* `affiliate_programs` N–1 `place_id` (Neo4j)

---

### **2\. Tables Detail**

#### **2.1. `users`**

Thông tin tài khoản chung cho cả tourist và driver.

| Column | Type | Constraints | Description |
| ----- | ----- | ----- | ----- |
| user\_id | UUID | PK, default `gen_random_uuid()` | User ID |
| user\_email | TEXT | UNIQUE, NOT NULL | Email đăng nhập |
| user\_password\_hash | TEXT | NOT NULL | Mật khẩu đã hash (hoặc null nếu social login) |
| user\_full\_name | TEXT | NOT NULL | Tên hiển thị |
| user\_phone | TEXT | NULL | Số điện thoại  |
| user\_role | TEXT | NOT NULL, CHECK in ('tourist','driver','admin') | Phân quyền |
| user\_locale | TEXT | NOT NULL, default `'vi_VN'` | Ngôn ngữ ưu tiên |
| timezone | TEXT | NOT NULL, default `'Asia/Ho_Chi_Minh'` | Timezone user |
| created\_at | TIMESTAMPTZ | NOT NULL, default `now()` | Thời gian tạo |
| updated\_at | TIMESTAMPTZ | NOT NULL, default `now()` | Lần cập nhật gần nhất |

**Indexes:**

* `idx_users_email` UNIQUE(email)

* `idx_users_role` (role)

---

#### **2.2. `driver_profiles`**

Thông tin chi tiết cho driver, map 1–1 với `users.id`.

| Column | Type | Constraints | Description |
| ----- | ----- | ----- | ----- |
| driver\_id | UUID | PK, default `gen_random_uuid()` | Driver profile ID |
| driver\_user\_id | UUID | UNIQUE, NOT NULL, FK → users(id) | Liên kết tới `users` |
| grab\_driver\_id | TEXT | NULL | ID của tài xế bên Grab (nếu có) |
| driver\_languages | TEXT\[\] | NOT NULL, default `ARRAY['vi']` | Các ngôn ngữ driver có thể nói |
| driver\_rating | NUMERIC(2,1) | NULL | Rating trung bình (nếu sync được) |
| driver\_bio | TEXT | NULL | Mô tả ngắn |
| created\_at | TIMESTAMPTZ | NOT NULL, default `now()` |  |
| updated\_at | TIMESTAMPTZ | NOT NULL, default `now()` |  |

**Indexes:**

* `idx_driver_profiles_user_id` UNIQUE(user\_id)

* `idx_driver_profiles_grab_driver_id` (grab\_driver\_id)

---

#### **2.3. `itineraries`**

Một itinerary ứng với một chuyến đi / plan của user.

| Column | Type | Constraints | Description |
| ----- | ----- | ----- | ----- |
| itinerary\_id | UUID | PK, default `gen_random_uuid()` | Itinerary ID |
| itinerary\_user\_id | UUID | NOT NULL, FK → users(id) | Chủ sở hữu itinerary |
| itinerary\_title | TEXT | NOT NULL | Tên itinerary (e.g., "Da Nang 3 days trip") |
| start\_date | DATE | NULL | Ngày bắt đầu (optional nếu open) |
| end\_date | DATE | NULL | Ngày kết thúc |
| itinerary\_total\_days | INT | NOT NULL, CHECK (total\_days \>= 1\) | Số ngày được planner tính toán |
| itinerary\_total\_budget | NUMERIC(12,2) | NULL | Tổng budget dự kiến |
| itinerary\_currency | TEXT | NOT NULL, default `'VND'` | Loại tiền tệ |
| itinerary\_meta | JSONB | NULL | Extra info (family size, interests, etc.) |
| created\_at | TIMESTAMPTZ | NOT NULL, default `now()` |  |
| updated\_at | TIMESTAMPTZ | NOT NULL, default `now()` |  |

**Indexes:**

* `idx_itineraries_user_id` (user\_id)

* `idx_itineraries_created_at` (created\_at)

---

#### **2.4. `itinerary_stops`**

Từng điểm dừng trong itinerary, trỏ tới **Neo4j Place bằng `place_id`**.

| Column | Type | Constraints | Description |
| ----- | ----- | ----- | ----- |
| stop\_id | UUID | PK, default `gen_random_uuid()` | Stop ID |
| stop\_itinerary\_id | UUID | NOT NULL, FK → itineraries(id) | Itinerary chứa stop này |
| stop\_day\_index | INT | NOT NULL, ≥ 1 | Ngày thứ mấy trong trip (1 \= Day 1\) |
| stop\_order\_index | INT | NOT NULL, ≥ 1 | Thứ tự trong ngày |
| stop\_place\_id | TEXT | NOT NULL | **Neo4j `Place.id`** (string slug) |
| arrival\_time | TIMESTAMPTZ | NULL | Time dự kiến đến (optional) |
| stay\_minutes | INT | NULL | Dự kiến thời gian ở đó |
| stop\_notes | TEXT | NULL | Ghi chú riêng cho user |
| stop\_tags | TEXT\[\] | NULL | Tag: \['seafood', 'family', 'view'\] |
| stop\_snapshot | JSONB | NULL | Snapshot nhỏ từ Neo4j (name, category ...) tại thời điểm tạo, optional |
| created\_at | TIMESTAMPTZ | NOT NULL, default `now()` |  |
| updated\_at | TIMESTAMPTZ | NOT NULL, default `now()` |  |

**Note (Option A):**

* `place_id` **không FK** tới table nào trong Postgres.

* Nó là foreign key “logical” trỏ tới Neo4j `(:Place { id })`.

* `snapshot` dùng để lưu một ít info (name, rating) nhằm tránh UI bị empty nếu Neo4j unavailable.

**Indexes:**

* `idx_itinerary_stops_itinerary_id` (itinerary\_id)

* `idx_itinerary_stops_place_id` (place\_id)

* `idx_itinerary_stops_day_order` (itinerary\_id, day\_index, order\_index)

---

#### **2.5. `bookings`**

Lưu các booking thực hiện qua MCP (Grab, Agoda, Klook…).

| Column | Type | Constraints | Description |
| ----- | ----- | ----- | ----- |
| booking\_id | UUID | PK, default `gen_random_uuid()` | Internal Booking ID |
| user\_id | UUID | NOT NULL, FK → users(id) | Ai tạo booking |
| itinerary\_id | UUID | NULL, FK → itineraries(id) | Gắn với itinerary nào (nếu có) |
| stop\_id | UUID | NULL, FK → itinerary\_stops(id) | Gắn với stop nào (nếu có) |
| booking\_provider | TEXT | NOT NULL | 'grab', 'agoda', 'klook', ... |
| booking\_type | TEXT | NOT NULL | 'ride', 'hotel', 'ticket', ... |
| external\_id | TEXT | NOT NULL | ID bên provider (e.g. Grab booking id) |
| booking\_status | TEXT | NOT NULL | 'pending','confirmed','cancelled','failed', ... |
| booking\_price | NUMERIC(12,2) | NULL | Giá thực tế |
| booking\_currency | TEXT | NOT NULL, default 'VND' | Loại tiền |
| place\_id | TEXT | NULL | Neo4j Place id nếu là booking tới 1 địa điểm cụ thể |
| raw\_request | JSONB | NULL | Payload request gửi MCP (debug/audit) |
| raw\_response | JSONB | NULL | Payload response từ MCP/provider |
| created\_at | TIMESTAMPTZ | NOT NULL, default `now()` |  |
| updated\_at | TIMESTAMPTZ | NOT NULL, default `now()` |  |

**Indexes:**

* `idx_bookings_user_id` (user\_id)

* `idx_bookings_itinerary_id` (itinerary\_id)

* `idx_bookings_external` (provider, external\_id)

* `idx_bookings_place_id` (place\_id)

---

#### **2.6. `affiliate_programs`**

Lưu các chương trình hoa hồng theo `place_id` (Neo4j).

| Column | Type | Constraints | Description |
| ----- | ----- | ----- | ----- |
| affiliate\_id | UUID | PK, default `gen_random_uuid()` | Affiliate program ID |
| place\_id | TEXT | NOT NULL | Neo4j Place id |
| affiliate\_partner\_name | TEXT | NOT NULL | Tên partner (e.g., "Klook", "Local Seafood Chain") |
| affiliate\_commission\_rate | NUMERIC(5,2) | NOT NULL | % hoa hồng (e.g. 10.00) |
| affiliate\_tracking\_url | TEXT | NOT NULL | URL kèm params tracking |
| affiliate\_active | BOOLEAN | NOT NULL, default TRUE | Đang active hay không |
| created\_at | TIMESTAMPTZ | NOT NULL, default `now()` |  |
| updated\_at | TIMESTAMPTZ | NOT NULL, default `now()` |  |

**Indexes:**

* `idx_affiliate_programs_place_id` (place\_id)

* `idx_affiliate_programs_partner` (partner\_name)

