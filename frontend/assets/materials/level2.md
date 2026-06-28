# Python 四日實作課程 — Level 2 標準版

> 適合已具備基本電腦操作能力，透過「觀念 → 示範 → 實作 → 檢核」完成四天密集課程的學習者。
> 課程依 7/6–7/9 上午與下午時段規劃，共 8 個單元。

## 課程地圖

| 日期 | 上午 09:00–12:00 | 下午 13:30–16:30 |
|---|---|---|
| 7/6 | Unit 1 環境、變數、資料型態與 I/O | Unit 2 條件判斷 |
| 7/7 | Unit 3 For／While 與基礎演算法 | Unit 4 迴圈實作題庫 |
| 7/8 | Unit 5 List 與 String 進階操作 | Unit 6 串列與字串實戰題庫 |
| 7/9 | Unit 7 函式與模組化 | Unit 8 遞迴與 Dictionary 應用 |

---

## Unit 1｜環境、變數、資料型態與 I/O

### 學習目標

- 能執行第一支 Python 程式並理解錯誤訊息的位置。
- 能正確命名變數，使用算術運算子與型態轉換。
- 能使用 `input()`、`print()` 與 f-string 完成互動程式。

### 核心觀念

Python 以由上而下的順序執行。變數是「名稱指向一個值」，不需要事先宣告型態。

```python
name = "Amy"        # str
age = 15            # int
height = 162.5      # float
is_student = True   # bool

print(type(name), type(age), type(height), type(is_student))
```

常用運算子：`+ - * / // % **`。優先順序不確定時使用括號。

```python
price = int(input("單價："))
quantity = int(input("數量："))
total = price * quantity
print(f"共 {quantity} 件，總價 {total} 元")
```

### 實作任務

1. 輸入姓名、學號，輸出格式化自我介紹。
2. 輸入圓半徑，輸出面積與周長，保留兩位小數。
3. 輸入秒數，換算成「分、秒」。

### 常見錯誤

- `input()` 回傳字串，計算前要用 `int()` 或 `float()`。
- `=` 是指定，`==` 才是比較。
- 不使用 `eval(input())`，避免執行不可信的程式碼。

---

## Unit 2｜條件判斷 If／Elif／Else

### 學習目標

- 使用關係運算子與 `and`、`or`、`not` 組合條件。
- 使用 `if / elif / else` 表達互斥規則。
- 能追蹤程式只會進入其中一個分支。

```python
score = int(input("成績："))

if score < 0 or score > 100:
    print("輸入範圍錯誤")
elif score >= 90:
    print("A")
elif score >= 80:
    print("B")
elif score >= 70:
    print("C")
elif score >= 60:
    print("D")
else:
    print("F")
```

### 判斷設計原則

1. 先處理無效輸入。
2. 範圍由嚴格到寬鬆排列。
3. 測試邊界值，例如 59、60、89、90。

### 實作任務

- 奇偶數與正負數判斷。
- BMI 分級。
- 閏年判斷：能被 400 整除，或能被 4 整除但不能被 100 整除。
- 簡易票價系統：依年齡與學生身分計價。

---

## Unit 3｜For／While 與基礎演算法

### 學習目標

- 分辨已知次數的 `for` 與未知次數的 `while`。
- 使用 `range(start, stop, step)`。
- 掌握累加、計數、極值搜尋與輸入驗證。

```python
total = 0
for number in range(1, 101):
    total += number
print(total)
```

```python
while True:
    password = input("密碼：")
    if password == "1234":
        print("登入成功")
        break
    print("密碼錯誤")
```

### 四種基礎演算法樣板

```python
numbers = [8, 3, 12, 5]

total = 0
count = 0
maximum = numbers[0]

for number in numbers:
    total += number
    count += 1
    if number > maximum:
        maximum = number

print(total, count, maximum)
```

### 實作任務

- 計算 1 到 n 的總和。
- 統計輸入資料中的正數、負數與零。
- 找出串列最大值，不使用 `max()`。
- 使用 `continue` 略過不合格資料。

---

## Unit 4｜迴圈實作與基礎題庫

### 學習目標

- 將題目拆成初始化、重複處理、更新與輸出。
- 使用巢狀迴圈處理表格與圖形。
- 能以測試資料驗證演算法。

### 題型一：乘法表

```python
for row in range(1, 10):
    for column in range(1, 10):
        print(f"{row}×{column}={row * column:2}", end="  ")
    print()
```

### 題型二：質數判斷

```python
n = int(input("正整數："))
is_prime = n >= 2

for divisor in range(2, int(n ** 0.5) + 1):
    if n % divisor == 0:
        is_prime = False
        break

print("質數" if is_prime else "不是質數")
```

### 題庫練習

1. 印出直角三角形與倒三角形。
2. 計算階乘與費波那契數列前 n 項。
3. 猜數字：限制次數並提示太大或太小。
4. 讀入成績直到輸入 `-1`，輸出平均、最高與最低分。
5. 挑戰：實作 1A2B 的比對核心。

---

## Unit 5｜List 與 String 進階操作

### 學習目標

- 使用索引、負索引與切片讀寫串列。
- 使用 `append`、`insert`、`pop`、`remove`、`sort`。
- 使用字串切片及 `split`、`join`、`strip`、`find`。

```python
scores = [88, 72, 95, 61]
scores.append(84)
scores.sort(reverse=True)
print(scores[:3])
```

```python
raw = " Amy, Bob, Cindy "
names = [name.strip() for name in raw.split(",")]
print(" / ".join(names))
```

### 資料複製注意事項

```python
original = [1, 2, 3]
same_object = original
copied = original.copy()
```

修改 `same_object` 會影響 `original`；修改 `copied` 不會。

### 延伸：Tuple

元組使用小括號且不可修改，適合保存固定資料。

```python
point = (25.04, 121.56)
latitude, longitude = point
```

---

## Unit 6｜串列與字串實戰題庫

### 學習目標

- 將原始字串清理後轉換成可分析的串列。
- 使用迴圈完成搜尋、統計、排序與分組。
- 能說明輸入、處理、輸出的資料流程。

### 綜合示範：成績分析

```python
raw = input("請以空格輸入成績：")
scores = [int(value) for value in raw.split()]

passed = [score for score in scores if score >= 60]
average = sum(scores) / len(scores)

print(f"平均：{average:.1f}")
print(f"及格：{passed}")
print(f"最高：{max(scores)}，最低：{min(scores)}")
```

### 實戰題庫

1. 統計一句話中各母音出現次數。
2. 判斷忽略空白與大小寫後是否為回文。
3. 將姓名清單去除空白、統一格式並排序。
4. 找出兩個串列的共同元素，結果不可重複。
5. 將二維成績串列轉換成每位學生的平均分數。
6. 挑戰：不用 `sort()` 實作氣泡排序。

---

## Unit 7｜函式與模組化

### 學習目標

- 使用 `def`、參數與 `return` 封裝重複邏輯。
- 理解區域變數、預設參數與關鍵字參數。
- 將大型程式拆成輸入、計算與輸出函式。

```python
def calculate_bmi(weight, height_cm):
    """回傳 BMI，height_cm 的單位是公分。"""
    height_m = height_cm / 100
    return weight / height_m ** 2


def bmi_level(bmi):
    if bmi < 18.5:
        return "過輕"
    if bmi < 24:
        return "正常"
    if bmi < 27:
        return "過重"
    return "肥胖"
```

### 模組化原則

- 一個函式只負責一件事。
- 優先回傳資料，不要讓每個函式都直接 `print()`。
- 避免依賴全域變數。
- 用清楚的名稱與 docstring 說明輸入與輸出。

### 實作任務

- 將 Unit 2 成績分級改寫成函式。
- 建立 `statistics(numbers)`，回傳總和、平均、最大與最小值。
- 將猜數字拆成產生答案、取得輸入、判斷結果三個函式。

---

## Unit 8｜遞迴與 Dictionary 應用

### 學習目標

- 理解遞迴的終止條件與遞迴步驟。
- 使用字典的鍵值結構增刪查改。
- 使用 `items()`、`keys()`、`values()` 遍歷字典。

### 遞迴

```python
def factorial(n):
    if n <= 1:          # 終止條件
        return 1
    return n * factorial(n - 1)
```

遞迴必須讓問題逐步縮小，否則會造成無限遞迴。

### Dictionary

```python
scores = {"Amy": 88, "Bob": 72, "Cindy": 95}
scores["David"] = 84
scores["Bob"] = 78

for name, score in scores.items():
    print(f"{name}: {score}")
```

### 綜合實作：文字詞頻

```python
words = input("輸入句子：").lower().split()
frequency = {}

for word in words:
    frequency[word] = frequency.get(word, 0) + 1

for word, count in sorted(frequency.items()):
    print(word, count)
```

### 延伸：Set

集合元素不重複，支援交集 `&`、聯集 `|`、差集 `-`。

```python
python_class = {"Amy", "Bob", "Cindy"}
ai_class = {"Bob", "David"}
print(python_class & ai_class)
```

### 期末整合任務

建立「學生成績管理系統」：以字典保存學生與成績，使用函式完成新增、查詢、統計與排序；至少使用一次遞迴或以迴圈版本比較其差異。

---

## 完課檢核

- 我能把需求拆成輸入、處理、輸出。
- 我能選擇條件、迴圈、串列、字典或函式解題。
- 我會用邊界值與一般值測試程式。
- 我能閱讀錯誤訊息並定位問題。
