# Python 四日實作課程 — Level 3 進階版

> 適合已熟悉基礎語法，準備加強演算法、資料建模、模組化與獨立解題的學習者。
> 本級別保留必要摘要，把時間集中在設計、測試與比較不同解法。

## 課程安排

| 日期 | 上午 | 下午 |
|---|---|---|
| 7/6 | Unit 1 型態、I/O 與資料驗證 | Unit 2 條件建模 |
| 7/7 | Unit 3 迴圈與演算法模式 | Unit 4 演算法題庫 |
| 7/8 | Unit 5 List／String 進階 | Unit 6 資料處理實戰 |
| 7/9 | Unit 7 函式與模組化 | Unit 8 遞迴與 Dictionary |

---

## Unit 1｜環境、變數、資料型態與 I/O

### 概念摘要

- Python 是動態型態語言，名稱指向物件。
- `int`、`float`、`bool`、`str` 的轉換可能失敗，輸入需驗證。
- 優先使用 f-string；格式規格可控制寬度、對齊與精度。

```python
def read_positive_float(prompt):
    while True:
        try:
            value = float(input(prompt))
            if value > 0:
                return value
        except ValueError:
            pass
        print("請輸入正數")


radius = read_positive_float("半徑：")
area = 3.14159 * radius ** 2
print(f"{area=:.2f}")
```

### 挑戰任務

1. 設計可處理錯誤輸入的匯率換算器。
2. 不使用 `eval()`，解析 `數字 運算子 數字` 並完成四則運算。
3. 比較 `/`、`//`、`%` 在負數上的結果。

---

## Unit 2｜條件判斷 If／Elif／Else

### 設計重點

- 將條件視為集合，確認是否重疊或遺漏。
- 善用 chained comparison：`0 <= score <= 100`。
- 先處理 guard clause，可降低巢狀層級。

```python
def shipping_fee(amount, is_member, region):
    if amount < 0:
        raise ValueError("amount 不可為負數")
    if region not in {"north", "central", "south"}:
        raise ValueError("未知地區")
    if amount >= 1000 or (is_member and amount >= 500):
        return 0
    return 80 if region == "north" else 120
```

### 挑戰任務

- 將複雜票價規則整理成決策表，再實作程式。
- 使用邊界值測試成績分級與 BMI 分級。
- 比較巢狀 `if` 與 guard clause 的可讀性。

---

## Unit 3｜For／While 與基礎演算法

### 演算法模式

- reduce：累加、連乘。
- filter：篩選符合條件的元素。
- search：找到後立即 `break`。
- sentinel loop：讀到特殊值才停止。
- two-level iteration：處理表格或組合。

```python
def min_max(numbers):
    if not numbers:
        raise ValueError("numbers 不可為空")

    minimum = maximum = numbers[0]
    for number in numbers[1:]:
        if number < minimum:
            minimum = number
        elif number > maximum:
            maximum = number
    return minimum, maximum
```

### 挑戰任務

1. 實作質數篩選並分析迴圈次數。
2. 找出數列的第二大相異值，只走訪一次。
3. 將 `while` 寫法改成 `for`，比較適用情境。

---

## Unit 4｜迴圈實作與基礎題庫

### 題庫 A：數值演算法

- 最大公因數與最小公倍數。
- 完全數、質數與因數分解。
- 十進位轉二進位，不使用 `bin()`。

### 題庫 B：巢狀迴圈

- 質數表與九九乘法表。
- 菱形、空心矩形圖案。
- 二維資料的列總和與欄總和。

### 題庫 C：狀態追蹤

```python
def first_longest_run(values):
    """回傳第一段最長連續相同值及長度。"""
    best_value = current_value = values[0]
    best_length = current_length = 1

    for value in values[1:]:
        if value == current_value:
            current_length += 1
        else:
            current_value = value
            current_length = 1
        if current_length > best_length:
            best_value = current_value
            best_length = current_length
    return best_value, best_length
```

### 挑戰任務

- 1A2B 猜數字核心。
- 不使用排序函式找中位數。
- 實作氣泡排序並統計比較與交換次數。

---

## Unit 5｜List 與 String 進階操作

### 核心議題

- aliasing 與 shallow copy。
- 切片、unpacking 與 comprehension。
- `enumerate()`、`zip()` 與二維串列。
- 字串不可變性及常見清理流程。

```python
records = ["Amy,88", "Bob,72", "Cindy,95"]
parsed = []

for record in records:
    name, score = record.split(",")
    parsed.append((name, int(score)))

ranking = sorted(parsed, key=lambda item: item[1], reverse=True)
```

### Tuple 延伸

元組適合固定結構資料與多值回傳。可用 unpacking 提升可讀性。

```python
for rank, (name, score) in enumerate(ranking, start=1):
    print(rank, name, score)
```

### 挑戰任務

- 手動實作 `split()` 的簡化版本。
- 將二維矩陣轉置，不使用外部套件。
- 說明 `a = b`、`a = b[:]`、`a = b.copy()` 的差異。

---

## Unit 6｜串列與字串實戰題庫

### 資料處理管線

1. 驗證與清理原始輸入。
2. 解析成結構化資料。
3. 轉換、篩選、聚合。
4. 依指定格式輸出。

### 實戰一：文字分析

```python
def normalize(text):
    return "".join(char.lower() for char in text if char.isalnum())


def is_palindrome(text):
    cleaned = normalize(text)
    return cleaned == cleaned[::-1]
```

### 實戰二：簡易 CSV

讀入多行 `姓名,分數`，拒絕格式錯誤或超出 0–100 的資料，再依分數排序。

### 挑戰任務

- 凱薩密碼加密與解密。
- Run-length encoding：`AAABBCCCC` → `A3B2C4`。
- 找出兩段文字共同出現且頻率最高的詞。
- 用二維串列完成井字棋勝負判斷。

---

## Unit 7｜函式與模組化

### 設計原則

- 函式介面應清楚：參數代表輸入，`return` 代表輸出。
- 避免全域狀態與可變預設參數。
- 將純計算與 I/O 分離，讓函式容易測試。

```python
def summarize(numbers):
    if not numbers:
        raise ValueError("numbers 不可為空")
    return {
        "count": len(numbers),
        "total": sum(numbers),
        "average": sum(numbers) / len(numbers),
        "minimum": min(numbers),
        "maximum": max(numbers),
    }
```

### 模組化範例

將成績系統拆成：

- `parse_scores(text)`：解析輸入。
- `validate_score(score)`：驗證範圍。
- `summarize(scores)`：計算統計。
- `format_report(result)`：產生輸出。

### 挑戰任務

- 使用 `*args` 建立可接受任意數量資料的平均函式。
- 使用 `**kwargs` 建立學生資料。
- 為函式撰寫正常、邊界與錯誤輸入測試。
- 將程式拆成兩個 `.py` 模組並使用 `import`。

---

## Unit 8｜遞迴與 Dictionary 應用

### 遞迴三要素

1. 終止條件。
2. 問題規模縮小。
3. 組合子問題結果。

```python
def binary_search(values, target, left=0, right=None):
    if right is None:
        right = len(values) - 1
    if left > right:
        return -1

    middle = (left + right) // 2
    if values[middle] == target:
        return middle
    if target < values[middle]:
        return binary_search(values, target, left, middle - 1)
    return binary_search(values, target, middle + 1, right)
```

### Dictionary 建模

```python
students = {
    "S001": {"name": "Amy", "scores": [88, 92, 85]},
    "S002": {"name": "Bob", "scores": [72, 80, 78]},
}

ranking = sorted(
    students.items(),
    key=lambda item: sum(item[1]["scores"]) / len(item[1]["scores"]),
    reverse=True,
)
```

### Set 延伸

使用交集、聯集、差集處理選課名單或資料去重。

### 挑戰任務

- 比較階乘的迴圈與遞迴版本。
- 用字典建立詞頻分析器。
- 遞迴走訪巢狀字典，輸出所有鍵值路徑。
- 完成模組化學生成績管理系統，加入查詢、排名與統計。

---

## 進階完課標準

- 能說明解法的正確性、邊界與可能失敗情況。
- 能將重複邏輯抽成可測試函式。
- 能選擇合適的資料結構，而非只讓程式「跑得動」。
- 能比較迴圈與遞迴、串列與字典等不同設計的取捨。
