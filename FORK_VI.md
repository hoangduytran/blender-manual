**Language / Ngôn ngữ:** [English](FORK.md) · Tiếng Việt

# Sổ Tay Blender — Bản Fork Dựng Đa Ngôn Ngữ

Kho mã này là một **bản fork phái sinh (downstream fork)** của
[Sổ tay Blender](https://projects.blender.org/blender/blender-manual) chính
thức. Nó bám theo nội dung của Blender một cách trung thực, nhưng bổ sung một bộ
công cụ về dựng tài liệu, dịch thuật, tìm kiếm và giao diện nhằm **dựng và đọc
sổ tay ở nhiều ngôn ngữ cùng một lúc** (tiếng Anh cộng với bất kỳ ngôn ngữ nào
có catalô PO, ví dụ tiếng Việt).

Không có thay đổi nào ở đây động đến *nội dung* của sổ tay. Tất cả chỉ là công cụ
dựng, các phần mở rộng (extension) cho Sphinx, và JavaScript giao diện được đắp
thêm lên trên bản gốc. Nhánh `main` được giữ làm một bản sao sạch của Blender;
toàn bộ tính năng của fork nằm trên `feature/new_make_for_foreign_languages`.

- **Nguồn gốc (Blender):** https://projects.blender.org/blender/blender-manual
- **Bản fork này:** https://github.com/hoangduytran/blender-manual

> **Vì sao lại fork?** Những thay đổi này được phát triển với sự hỗ trợ của AI và
> không được hợp nhất (merge) vào dự án gốc. Đăng tại đây giúp giữ chúng sẵn có
> cho bất kỳ ai muốn dựng đa ngôn ngữ tại máy mình, đồng thời vẫn cho phép bạn
> (và người dùng) kéo về những cập nhật sổ tay liên tục của Blender — xem
> [Đồng bộ với Blender](#đồng-bộ-với-blender).

---

## Mục lục

- [Tổng quan tính năng](#tổng-quan-tính-năng)
  - [1. Dựng và phục vụ đa ngôn ngữ](#1-dựng-và-phục-vụ-đa-ngôn-ngữ)
  - [2. Dựng bản dịch tăng dần nhanh (smart MO shards)](#2-dựng-bản-dịch-tăng-dần-nhanh-smart-mo-shards)
  - [3. Tìm kiếm đa ngôn ngữ dựa trên PO](#3-tìm-kiếm-đa-ngôn-ngữ-dựa-trên-po)
  - [4. Thẻ gợi ý khi đọc (repeatable-record)](#4-thẻ-gợi-ý-khi-đọc-repeatable-record)
  - [5. Tài nguyên tĩnh và ảnh dùng chung](#5-tài-nguyên-tĩnh-và-ảnh-dùng-chung)
  - [6. Giao diện và trải nghiệm đọc](#6-giao-diện-và-trải-nghiệm-đọc)
  - [7. Sửa lỗi phím tắt (:kbd:)](#7-sửa-lỗi-phím-tắt-kbd)
  - [8. Công cụ và hạ tầng](#8-công-cụ-và-hạ-tầng)
- [Tham chiếu các mục tiêu make](#tham-chiếu-các-mục-tiêu-make)
- [Biến môi trường](#biến-môi-trường)
- [Chọn ngôn ngữ của bạn](#chọn-ngôn-ngữ-của-bạn)
- [Bắt đầu nhanh](#bắt-đầu-nhanh)
- [Quy trình biên soạn và dịch thuật hằng ngày](#quy-trình-biên-soạn-và-dịch-thuật-hằng-ngày)
- [Tùy biến ảnh và kiểu dáng](#tùy-biến-ảnh-và-kiểu-dáng)
- [Đồng bộ với Blender](#đồng-bộ-với-blender)
- [Cấu trúc kho mã](#cấu-trúc-kho-mã)

---

## Tổng quan tính năng

### 1. Dựng và phục vụ đa ngôn ngữ

Dựng **mọi** ngôn ngữ đã cấu hình vào cây kết xuất riêng của nó, rồi phục vụ tất
cả từ một trang web cục bộ duy nhất kèm bộ chuyển đổi ngôn ngữ hoạt động được.

- `make build` dựng từng mã trong `BF_LANGS` vào `build/<lang>/`. Tiếng Anh luôn
  được dựng đầu tiên với vai trò ngôn ngữ "hạt giống" cho tài nguyên dùng chung.
- `make serve` khởi động một máy chủ hợp nhất tại <http://localhost:8000>, định
  tuyến `/<lang>/…` tới bản dựng tương ứng và chèn vào thanh bên một bộ chuyển
  ngôn ngữ liệt kê đúng các ngôn ngữ hiện có tại máy.
- `make liveall` làm cả hai việc trong một lệnh: các bộ dựng-lại trực tiếp (live)
  cho từng ngôn ngữ (tự nạp lại trong trình duyệt) **cùng với** máy chủ hợp nhất.
  Sửa một tệp `.rst` hoặc một catalô PO thì trang bị ảnh hưởng sẽ tự dựng lại và
  làm mới.
- `make stop` dừng gọn gàng `liveall`/`serve` — máy chủ hợp nhất, mọi bộ dựng-lại
  của từng ngôn ngữ, và các tiến trình Sphinx con bị bỏ rơi.

Cài đặt: [tools/serve_docs.py](tools/serve_docs.py), cùng các mục tiêu `liveall`
/ `build` / `serve` / `stop` trong [Makefile](Makefile).

### 2. Dựng bản dịch tăng dần nhanh (smart MO shards)

Người dịch của Blender duy trì **một** tệp `blender_manual.po` lớn cho mỗi ngôn
ngữ. Biên dịch lại và kết xuất lại toàn bộ catalô sau mỗi lần sửa thì rất chậm.
Bản fork này biên dịch tệp PO khổng lồ thành **một tệp `.mo` cho mỗi tài liệu**
và chỉ dựng lại những tài liệu có bản dịch thực sự thay đổi.

- [tools/translations/smart_mo_compile.py](tools/translations/smart_mo_compile.py) —
  biên dịch `locale/<lang>/LC_MESSAGES/blender_manual.po` thành các mảnh (shard)
  theo từng tài liệu dưới `build/.i18n_shards/locale/<lang>/LC_MESSAGES/`, kèm
  một bộ nhớ đệm bản dịch để bỏ qua các tài liệu không đổi.
- [build_files/extensions/i18n_shards.py](build_files/extensions/i18n_shards.py) —
  một extension Sphinx đánh dấu một tài liệu là *cũ* (outdated) khi mảnh sinh ra
  của nó mới hơn lần cuối Sphinx đọc tài liệu đó, nhờ vậy bản dựng tăng dần nhận
  ra các sửa đổi bản dịch một cách đáng tin cậy qua các phiên bản Sphinx.

Tệp PO vẫn là nguồn sự thật duy nhất do con người chỉnh sửa; các mảnh chỉ là sản
phẩm phụ của quá trình dựng.

### 3. Tìm kiếm đa ngôn ngữ dựa trên PO

Một lớp phủ tìm kiếm hoạt động **theo từng ngôn ngữ**, lấy dữ liệu trực tiếp từ
các catalô PO thay vì chỉ mục mặc định chỉ-tiếng-Anh của Sphinx.

- Nhấn <kbd>/</kbd> trên bất kỳ trang nào để mở lớp phủ. Kết quả truyền về theo
  luồng qua Server-Sent Events và liên kết sâu (deep-link) tới đúng **mỏ neo của
  mục (section anchor)**, chứ không chỉ tới trang.
- Mỗi ngôn ngữ được dịch sẽ có `build/<lang>/searchindex.pkl.gz`, dựng bởi
  [tools/search/index_builder.py](tools/search/index_builder.py) từ tệp PO của nó
  (`make search-index`, cũng tự chạy bởi `make build` / `make liveall`).
- Tiếng Anh không có tệp PO, nên
  [build_files/extensions/search_index_builder.py](build_files/extensions/search_index_builder.py)
  dựng chỉ mục tiếng Anh thẳng từ cây tài liệu (doctree) — tương đương với
  `blender_manual.pot` ở ngôn ngữ nguồn.
- Phần bên trong của tìm kiếm: [tools/search/](tools/search/) (`index_builder.py`,
  `index_loader.py`, `index_searcher.py`, `po_parser.py`, `po_watcher.py`,
  `section_map.py`, `searchable_record.py`).

### 4. Thẻ gợi ý khi đọc (repeatable-record)

Dành cho người học ngôn ngữ khi đọc sổ tay đã dịch, tính năng này thêm những
**thẻ gợi ý (hint pill)** nhỏ nằm trong dòng, hiển thị thuật ngữ tiếng Anh gốc
bên cạnh bản dịch (cùng thông tin thuật ngữ/trùng-gần-đúng), được kết xuất phía
máy chủ.

- [build_files/extensions/repeatable_record.py](build_files/extensions/repeatable_record.py)
  cùng các extension `repeatable_*` đi kèm thu thập các nút có thể dịch nằm trong
  danh sách cho phép (tiêu đề, thuật ngữ, tham chiếu, nhấn mạnh) vào một kho nhỏ
  có thể pickle.
- Nhận diện thuật ngữ tự điển (`.i18n-vi-hint`), gợi ý đặt trong ngoặc đơn (ví dụ
  tiếng Nga `Аддоны (add-ons)`), và báo cáo các trường hợp trùng-gần-đúng, với
  việc so khớp tiếng Anh không phân biệt hoa thường.
- Các extension: [build_files/extensions/](build_files/extensions/)
  (`repeatable_record.py`, `repeatable_extract.py`, `repeatable_html.py`,
  `repeatable_builder.py`).

### 5. Tài nguyên tĩnh và ảnh dùng chung

Nếu không tối ưu, mỗi bản dựng ngôn ngữ sẽ sao chép `_static` (~10 MB) và
`_images` (~250 MB) vào `build/<lang>/`. Vì các ảnh chụp màn hình giống hệt nhau
giữa các ngôn ngữ, điều đó lãng phí cả dung lượng đĩa lẫn thời gian dựng.

- [build_files/extensions/shared_assets.py](build_files/extensions/shared_assets.py)
  gom các tài nguyên dùng chung về dưới `build/shared/` và cho mỗi ngôn ngữ tham
  chiếu tới đó, đồng thời vẫn cho phép **ghi đè theo từng ngôn ngữ** (một ảnh đã
  bản địa hóa trong `locale/<lang>/…` sẽ thắng ảnh tiếng Anh dùng chung).
- `liveall` theo dõi các thư mục ghi đè theo từng ngôn ngữ nên khi thay vào một
  tài nguyên đã bản địa hóa sẽ kích hoạt dựng lại.

### 6. Giao diện và trải nghiệm đọc

Các cải tiến phía trình duyệt được chèn vào mọi trang:

- **Trình xem ảnh phóng to được** —
  [build_files/theme/js/image_viewer.js](build_files/theme/js/image_viewer.js):
  bấm vào một hình trong sổ tay để mở trình xem phóng to được; hiển thị đường dẫn
  độ phân giải nguồn.
- **Thanh chia thanh bên kéo được** —
  [build_files/theme/js/sidebar_splitter.js](build_files/theme/js/sidebar_splitter.js):
  đổi kích thước các thanh bên kiểu 3D bằng cách kéo.

### 7. Sửa lỗi phím tắt (`:kbd:`)

Sphinx tách văn bản `:kbd:` tại dấu cách, `-`, `+`, `^`, làm hỏng các tên phím đã
dịch như tiếng Việt `Dấu Cộng (+) Bàn Số (NumpadPlus)` thành mỗi từ một khối
`<kbd>`. [build_files/extensions/kbd_fix.py](build_files/extensions/kbd_fix.py)
nối lại các chuỗi này và chỉ tách tại các dấu phân cách *ở cấp ngoài cùng* (không
bao giờ bên trong ngoặc đơn, không bao giờ tại dấu cách).

### 8. Công cụ và hạ tầng

- Ghi nhật ký nhẹ nhàng thay cho hạ tầng `application.log` có giới hạn cũ.
- Các hàm trợ giúp dùng chung trong [tools/common/](tools/common/)
  (`constants.py`, `utils.py`).
- Cải tiến công cụ dịch thuật: `po_shortcuts.py`, `update_po.py`,
  `file_translation_progress.py`, `rst_find_reference.py`.
- Một bộ kiểm thử chấp nhận đa nền tảng dưới [tests/](tests/) (tìm kiếm,
  repeatable-record, tài nguyên dùng chung, PO shortcuts, ghi nhật ký đa tiến
  trình) cùng các tài liệu thiết kế/kế hoạch.

---

## Tham chiếu các mục tiêu make

Chạy `make help` để có danh sách đầy đủ chính thức. Những điểm nổi bật được thêm
hoặc thay đổi bởi bản fork này:

| Mục tiêu | Tác dụng |
| --- | --- |
| `make build` | Dựng mọi ngôn ngữ trong `BF_LANGS` vào `build/<lang>/`, rồi dựng chỉ mục tìm kiếm. |
| `make remake` | `make clean` + `make build`. |
| `make liveall` | Dựng lại trực tiếp toàn bộ `BF_LANGS` **và** phục vụ tại <http://localhost:8000> (một lệnh). |
| `make serve` | Phục vụ thư mục `build/` hiện có kèm chuyển đổi ngôn ngữ. |
| `make stop` | Dừng `liveall`/`serve` đang chạy (máy chủ + các bộ dựng-lại + tiến trình Sphinx). |
| `make search-index` | Dựng (lại) `build/<lang>/searchindex.pkl.gz` cho mỗi ngôn ngữ có tệp PO. |
| `make livehtml-direct` | Tự dựng một ngôn ngữ vào `build/<lang>/` (dùng kèm `make serve`). |
| `make html` | Bản dựng HTML một-ngôn-ngữ tiêu chuẩn (hành vi gốc). |
| `make checkout_locale <mã>` | Lấy catalô bản dịch (ví dụ `make checkout_locale vi fr`) từ kho dịch thuật của Blender về `locale/`. |
| `make update_po` | Cập nhật catalô thông điệp PO. |
| `make report_po_progress` | Báo cáo tiến độ dịch / các chuỗi fuzzy. |
| `make local` | Bổ trợ: tắt intersphinx cho lần gọi này (ví dụ `make remake local`). |

## Biến môi trường

| Biến | Ý nghĩa |
| --- | --- |
| `BF_LANG` | Mã ngôn ngữ cho bản dựng hiện tại (mặc định `en`). Truyền cho Sphinx dưới dạng `-D language=<mã>`. |
| `BF_LANGS` | Danh sách ngôn ngữ cách nhau bằng dấu cách do `make build` dựng (mặc định: tự nhận từ `locale/`). Tiếng Anh luôn được thêm vào đầu làm hạt giống tài nguyên dùng chung, nên `BF_LANGS="vi ru"` trở thành `en vi ru`. |
| `NO_INTERSPHINX` | Khi khác rỗng, các mục tiêu Sphinx bỏ qua intersphinx (không cần truy cập mạng). |

Ví dụ — dựng tiếng Anh + tiếng Việt và phục vụ trực tiếp:

```bash
make liveall BF_LANGS="en vi"
```

---

## Chọn ngôn ngữ của bạn

**Kho mã này không kèm theo dữ liệu bản dịch nào.** Thư mục `locale/` không được
đưa vào git, nên bạn tự do kéo về bất kỳ ngôn ngữ nào bạn muốn. Bản dịch đến từ
chính dự án
[blender-manual-translations](https://projects.blender.org/blender/blender-manual-translations)
của Blender, lấy về bằng:

```bash
make checkout_locale vi          # một ngôn ngữ
make checkout_locale vi fr ru    # nhiều ngôn ngữ cùng lúc
make checkout_locale             # tương tác: nhắc nhập các mã
```

Lệnh này lấy thưa (sparse-checkout) `locale/<lang>/LC_MESSAGES/blender_manual.po`
cho từng mã. Tiếng Anh không cần catalô (nó là ngôn ngữ nguồn). Sau khi lấy về
một ngôn ngữ, nó sẽ sẵn sàng cho mọi mục tiêu dựng/phục vụ; truyền các mã bạn
muốn qua `BF_LANGS` (hoặc dựa vào việc tự nhận từ `locale/`).

## Bắt đầu nhanh

```bash
# 1. Sao chép (clone) bản fork
git clone git@github.com:hoangduytran/blender-manual.git
cd blender-manual

# 2. Thiết lập môi trường một lần (tạo virtualenv cho Sphinx)
make setup

# 3. Lấy ngôn ngữ bạn muốn (bỏ qua nếu chỉ dùng tiếng Anh)
make checkout_locale vi

# 4. Dựng + phục vụ trực tiếp tiếng Anh cùng các ngôn ngữ bạn chọn
make liveall BF_LANGS="en vi"
# → mở http://localhost:8000  (nhấn '/' để tìm kiếm, bộ chuyển ngôn ngữ ở thanh bên)

# Dừng tất cả
make stop
```

Chỉ dùng tiếng Anh thì không cần bước `checkout_locale`:

```bash
make liveall                 # chỉ tiếng Anh
```

Dựng trang tĩnh mà không chạy máy chủ trực tiếp:

```bash
make checkout_locale vi
make build BF_LANGS="en vi"
make serve BF_LANGS="en vi"
```

---

## Quy trình biên soạn và dịch thuật hằng ngày

Máy chủ `liveall` là trung tâm cho cả hai công việc: nó theo dõi các tệp nguồn
`.rst` tiếng Anh **và** catalô PO của từng ngôn ngữ, chỉ dựng lại phần thay đổi,
và tự làm mới trình duyệt. Khởi động một lần rồi để nó chạy:

```bash
make liveall BF_LANGS="en vi"     # tiếng Anh + tiếng Việt, trực tiếp, tại :8000
make stop                          # khi bạn xong việc
```

Nó theo dõi gì (theo từng ngôn ngữ): `manual/**.rst`, `locale/<lang>/LC_MESSAGES`
(các tệp PO), các thư mục ghi đè theo ngôn ngữ, và `build_files/` (giao diện +
extension).

### Viết / sửa nội dung tiếng Anh (RST)

1. Khi `liveall` đang chạy, sửa bất kỳ trang nào dưới `manual/**/*.rst`.
2. Khi lưu, mọi ngôn ngữ đã dựng sẽ dựng lại; trang **tiếng Anh** làm mới ngay
   lập tức. Các ngôn ngữ đã dịch sẽ hiển thị văn bản tiếng Anh làm *dự phòng*
   cho mọi chuỗi mới hoặc đã đổi cho đến khi nó được dịch.
3. Khi bạn đã thêm hoặc đổi chuỗi tiếng Anh, hãy làm mới catalô của người dịch để
   các mã thông điệp mới đến được tay họ:

   ```bash
   make update_po
   ```

   Lệnh này cập nhật `locale/<lang>/LC_MESSAGES/blender_manual.po` cho mọi ngôn
   ngữ với các `msgid` mới/đã đổi (để trống chưa dịch hoặc đánh dấu fuzzy để
   người dịch điền). Chạy nó mỗi khi văn bản nguồn tiếng Anh thay đổi, không phải
   sau mỗi lần sửa.

### Dịch sang một ngôn ngữ nước ngoài (PO)

1. Giữ `liveall` đang chạy. Mở `locale/<lang>/LC_MESSAGES/blender_manual.po` và
   điền các mục `msgstr` (trực tiếp, hoặc dùng các trợ thủ PO của dự án trong
   [tools/translations/](tools/translations/)).
2. Khi lưu:
   - `smart_mo_compile.py` biên dịch lại **chỉ** những mảnh tài liệu có bản dịch
     thay đổi,
   - ngôn ngữ đó dựng lại và trình duyệt làm mới,
   - `MultiPOWatcher` của máy chủ dựng lại **chỉ mục tìm kiếm** của ngôn ngữ đó,
     nên tìm kiếm cũng phản ánh ngay bản dịch mới của bạn.
3. Kiểm tra mức độ bao phủ bất cứ lúc nào:

   ```bash
   make report_po_progress           # số đã dịch / fuzzy / chưa dịch
   ```

### Các lựa chọn nhẹ hơn cho một ngôn ngữ

Khi bạn chỉ quan tâm tới một ngôn ngữ, các lệnh này nhẹ hơn `liveall`:

```bash
make livehtml BF_LANG=vi            # một ngôn ngữ, trực tiếp, phục vụ tại :8000
# — hoặc, dựng vào build/<lang>/ và phục vụ riêng (hai cửa sổ terminal):
make livehtml-direct BF_LANG=vi     # terminal 1: bộ dựng-lại
make serve BF_LANGS="en vi"         # terminal 2: máy chủ hợp nhất kèm bộ chuyển
```

> Nhắc lại: `BF_LANGS` luôn dựng tiếng Anh đầu tiên (hạt giống tài nguyên dùng
> chung), nên `BF_LANGS="vi"` được hiểu là `"en vi"`.

## Tùy biến ảnh và kiểu dáng

Có ba cách khác nhau để thêm tài nguyên của riêng bạn, tùy theo bạn muốn **thay
một ảnh chụp màn hình cho một ngôn ngữ**, **đổi kiểu dáng cho cả giao diện**, hay
**thêm ảnh nội dung mới**.

### A. Ghi đè ảnh / tệp tĩnh theo từng ngôn ngữ (không sửa mã)

Nhờ extension [tài nguyên dùng chung](#5-tài-nguyên-tĩnh-và-ảnh-dùng-chung), bất
kỳ ngôn ngữ nào cũng có thể ghi đè hoặc thêm một tài nguyên bằng cách đặt một tệp
dưới `locale/<lang>/_images/` hoặc `locale/<lang>/_static/`, **giữ nguyên đường
dẫn tương đối** mà sổ tay dùng. Bản ghi đè thắng bản tiếng Anh dùng chung; mọi
thứ khác vẫn liên kết tới cây dùng chung.

```text
# Thay một ảnh chụp tiếng Anh bằng ảnh tiếng Việt:
locale/vi/_images/render/cycles/gpu_rendering.png   # cùng đường dẫn với ảnh EN

# Thêm một tệp tĩnh chỉ-cho-tiếng-Việt (ví dụ chỉnh CSS hoặc phông bản địa hóa):
locale/vi/_static/css/vi_overrides.css
```

- Tiếng Anh cũng có thể ghi đè tài nguyên dùng chung của chính nó theo cách đó,
  qua `locale/en/_images/…` và `locale/en/_static/…`.
- `make liveall` theo dõi các thư mục ghi đè này (`OVERRIDE_SUBDIRS = _images
  _static`), nên thả vào hoặc thay một tệp sẽ tự kích hoạt dựng lại và làm mới.
- Không cần sửa `conf.py` hay Makefile — các bản ghi đè được phân giải theo đường
  dẫn lúc dựng.

### B. CSS / JavaScript cho cả giao diện (mọi ngôn ngữ)

Các tài nguyên tĩnh của giao diện nằm trong **`build_files/theme/`** (đăng ký làm
`html_static_path` của Sphinx). Để thêm một biểu kiểu (stylesheet) hay script
toàn trang:

1. Thả tệp vào cây giao diện, ví dụ `build_files/theme/css/my_overrides.css` hoặc
   `build_files/theme/js/my_widget.js`.
2. Đăng ký nó trong [manual/conf.py](manual/conf.py) ở khối `furo`:

   ```python
   html_css_files = [
       "css/theme_overrides.css",
       "css/version_switch.css",
       "fonts/bl-icons.css",
       "css/my_overrides.css",   # ← biểu kiểu của bạn
   ]
   html_js_files = [
       "js/version_switch.js",
       "js/sidebar_splitter.js",
       "js/image_viewer.js",
       "js/my_widget.js",        # ← script của bạn
   ]
   ```

Đây đúng là cách mà chính [image_viewer.js](build_files/theme/js/image_viewer.js)
và [sidebar_splitter.js](build_files/theme/js/sidebar_splitter.js) của fork được
gắn vào, hãy noi theo chúng làm ví dụ chạy được. Đổi kiểu dáng các phần tử có sẵn
thì tốt nhất làm trong `css/theme_overrides.css` (được nạp sau mặc định của Furo,
nên quy tắc của bạn thắng).

### C. Ảnh nội dung mới (được tham chiếu từ `.rst`)

Với ảnh xuất hiện *trong văn bản sổ tay* (hình, ảnh chụp bạn thêm vào một trang),
hãy theo quy ước gốc của Blender: đặt tệp dưới `manual/images/` và tham chiếu từ
`.rst` bằng chỉ thị `figure`/`image` thông thường. Những ảnh này tự động dùng
chung cho mọi ngôn ngữ; chỉ bản địa hóa khi cần qua cách **A** ở trên.

> Mẹo: giữ tài nguyên giao diện riêng của fork trong `build_files/theme/` và ảnh
> nội dung trong `manual/images/`. Việc tách biệt đó giúp các lần đồng bộ nội
> dung từ gốc (vốn động đến `manual/`) hiếm khi đụng độ với tùy biến giao diện
> của bạn.

## Đồng bộ với Blender

Toàn bộ ý nghĩa của mô hình fork: **giữ nội dung Blender luôn mới nhất trong khi
vẫn giữ các thay đổi công cụ này.** `main` là bản sao sạch của Blender; phần việc
của fork nằm trên `feature/new_make_for_foreign_languages`, và bạn đưa các thay
đổi từ gốc *vào* nhánh đó bằng cách **hợp nhất (merge)** (không bao giờ rebase —
hợp nhất nghĩa là người đã sao chép nhánh có thể `git pull` an toàn, không
force-push).

### Thiết lập remote một lần

Đã được cấu hình sẵn trong bản làm việc của người duy trì. Nếu bạn vừa clone mới:

```bash
git remote add upstream https://projects.blender.org/blender/blender-manual.git
git remote set-url --push upstream DISABLE   # an toàn: không bao giờ đẩy lên Blender
```

### Cập nhật định kỳ (chạy mỗi khi sổ tay Blender thay đổi)

```bash
git fetch upstream

# Giữ main là bản sao y hệt của Blender
git checkout main
git merge --ff-only upstream/main
git push origin main

# Đưa cập nhật của Blender vào fork, vẫn giữ công cụ của ta
git checkout feature/new_make_for_foreign_languages
git merge upstream/main          # giải quyết xung đột nếu có, rồi:
git push origin feature/new_make_for_foreign_languages
```

Xung đột, nếu có, gần như luôn nằm ở các tệp **nội dung** `.rst` (lấy bản của
gốc) chứ không phải ở phần `tools/`, `build_files/`, hay `Makefile` mà fork thêm
vào, vì gốc không bao giờ động đến chúng.

### Đồng bộ tự động hằng tuần

[.github/workflows/sync-upstream.yml](.github/workflows/sync-upstream.yml) chạy
mỗi thứ Hai (và theo yêu cầu qua tab Actions). Nó fast-forward `main`, thử hợp
nhất `upstream/main` vào nhánh fork, rồi hoặc là:

- **mở một pull request** với các cập nhật đã hợp nhất (hợp nhất sạch), hoặc
- **mở một issue** liệt kê các tệp xung đột (cần giải quyết thủ công).

Không có gì bị force-push và nhánh fork không bao giờ bị bot sửa trực tiếp — bạn
xem lại và hợp nhất PR.

> ℹ️ **Lưu ý:** GitHub chỉ chạy Action theo lịch từ **nhánh mặc định**. Nếu bạn
> giữ `main` làm nhánh mặc định (và là bản sao sạch), việc đồng bộ tự động này sẽ
> không tự chạy — hãy dùng các lệnh thủ công ở trên.

---

## Cấu trúc kho mã

```
build_files/extensions/   Các extension Sphinx do fork thêm
  i18n_shards.py            phát hiện cũ cho mảnh MO theo từng tài liệu
  kbd_fix.py                tách lại :kbd: cho tên phím đã dịch
  search_index_builder.py   chỉ mục tìm kiếm ngôn ngữ nguồn (tiếng Anh)
  shared_assets.py          dùng chung _static/_images giữa các ngôn ngữ
  repeatable_*.py           thu thập/kết xuất thẻ gợi ý khi đọc
build_files/theme/js/      JavaScript giao diện (image_viewer, sidebar_splitter)
tools/serve_docs.py        máy chủ phát triển đa ngôn ngữ hợp nhất
tools/translations/        smart_mo_compile.py + công cụ PO
tools/search/              chỉ mục tìm kiếm dựa trên PO + bộ tìm
tools/common/              hằng số/tiện ích dùng chung
tests/                     kiểm thử chấp nhận + tài liệu thiết kế/kế hoạch
Makefile                   các mục tiêu dựng/phục vụ/dừng đa ngôn ngữ
```

Về hướng dẫn đóng góp cho gốc, hướng dẫn văn phong, và dự án dịch thuật, xem
[README_VI.md](README_VI.md).
