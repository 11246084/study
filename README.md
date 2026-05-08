# 程式設計適性學習輔助系統 (AdaptLearn)

一套以形成性評量為核心的 Python 程式設計適性學習平台。學生完成單元測驗後，系統會依答題表現自動分派至三種難度等級之一，提供個人化的學習路徑。

## 功能特色

- **三級難度自動分流**：依測驗成績動態調整下一單元的難度（Level 1 / 2 / 3）
- **雙軌學習路徑**：
  - 垂直路徑：依成績升降級進入下一單元
  - 水平路徑：同單元提供「挑戰進階」或「補救複習」推薦
- **單元解鎖機制**：完成前一單元測驗後解鎖下一單元
- **三種題型支援**：選擇題、簡答題、程式撰寫題
- **弱點補強**：完成全部 8 單元後，自動針對成績最低的 3 個單元提供複習建議
- **角色管理**：學生 / 教師 / 管理員三種角色

## 技術架構

### 後端
- Django 5.2 + Django REST Framework 3.15.2
- JWT 認證（djangorestframework-simplejwt）
- MySQL 8.0
- python-decouple（環境變數管理）

### 前端
- 原生 HTML / CSS / JavaScript（無框架、無建置工具）
- 由 Django 直接提供靜態檔案服務

## 專案結構

```
study/
├── backend/
│   ├── apps/
│   │   ├── users/           # 自訂 User 模型（含 role 欄位）
│   │   ├── courses/         # Course、Lesson、Enrollment
│   │   ├── assessments/     # Quiz、Question、Choice、QuizAttempt、Answer
│   │   └── learning/        # AdaptiveLearningPath、Recommendation、Progress
│   ├── config/              # Django 設定
│   └── manage.py
└── frontend/
    ├── js/
    │   ├── api.js           # API 呼叫與 JWT 處理
    │   └── main.js          # 共用 navbar 初始化
    ├── index.html           # 學生主頁（8 個單元卡）
    ├── lesson.html          # 課程內容頁
    ├── quiz.html            # 測驗作答頁
    └── quiz-result.html     # 測驗結果頁
```

## 環境設定

### 1. 資料庫

啟動 MySQL（Windows）：
```bash
"/c/Program Files/MySQL/MySQL Server 8.0/bin/mysqld" --console
```

建立資料庫：
```sql
CREATE DATABASE study_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 環境變數

於 `backend/` 建立 `.env`：
```
DB_NAME=study_db
DB_USER=root
DB_PASSWORD=your_password
SECRET_KEY=your_secret_key
```

### 3. 啟動後端

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data        # 載入課程與題目資料
python manage.py createsuperuser  # 建立管理員帳號
python manage.py runserver
```

伺服器啟動後，開啟瀏覽器至 `http://127.0.0.1:8000/` 即可使用（前端由 Django 一併提供服務）。

## API 路由

所有 API 皆掛載於 `/api/`：

| 前綴 | 用途 |
|------|------|
| `/api/auth/` | 註冊、登入、個人資料 |
| `/api/courses/` | 課程列表、課程詳情、選課、我的課程、單元詳情 |
| `/api/assessments/` | 測驗詳情、提交答案、我的作答、作答詳情 |
| `/api/learning/` | 學習進度、推薦、表現紀錄、`adaptive-path/` |

## 適性化邏輯

### 升降級規則（下一單元難度）

| 分數 | 結果 |
|------|------|
| ≥ 90 | 升一級（最高 Level 3） |
| 80–89 | 維持原級 |
| < 80 | 降一級（最低 Level 1） |

### 推薦卡片規則

| 分數 | 當前等級 | 推薦 |
|------|----------|------|
| ≥ 90 | < 3 | 同單元，等級 +1（挑戰進階） |
| ≥ 90 | = 3 | 下一單元 |
| 80–89 | 任意 | 下一單元，同等級 |
| < 80 | > 1 | 同單元，等級 −1（補救複習） |
| < 80 | = 1 | 下一單元，Level 1 |

## 系統限制

- 平台固定為 **8 單元 × 3 等級**
- `Lesson.order`（1–8）即代表單元編號
- `Course.difficulty`（`beginner` / `intermediate` / `advanced`）對應等級 1 / 2 / 3
- 前後端共用 port 8000，開發環境啟用 `CORS_ALLOW_ALL_ORIGINS`

## 題型與評分

| 題型 | 評分方式 |
|------|----------|
| `multiple_choice`（初級） | 比對 `choice.id` |
| `short_answer`（中級） | 去空白、轉小寫後完全比對 |
| `coding`（高級） | 非空作答即給滿分（教師人工複審） |
