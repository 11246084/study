# Python 程式設計教材 — Level 2 標準版

> **適合對象**：理解基礎概念，需要熟練語法與實際應用的同學  
> **教材風格**：標準說明 ＋ 程式碼範例 ＋ 部分需補全的練習  
> **認知負荷**：中 ── 說明與練習並重，部分程式需自行補全  
> **練習方式**：填空題 ＋ 程式補全，訓練你實際動手寫

---

## 目錄

- [Unit 1｜print 輸出](#unit-1print-輸出)
- [Unit 2｜input 輸入與運算](#unit-2input-輸入與運算)
- [Unit 3｜if 條件判斷](#unit-3if-條件判斷)
- [Unit 4｜多條件 if](#unit-4多條件-if)
- [Unit 5｜list 串列](#unit-5list-串列)
- [Unit 6｜range 數列](#unit-6range-數列)
- [Unit 7｜for 迴圈](#unit-7for-迴圈)
- [Unit 8｜迴圈應用](#unit-8迴圈應用)

---

## Unit 1｜print 輸出

### 🎯 學習目標

- 掌握 `print()` 的 `sep` 和 `end` 參數
- 使用 f-string 進行格式化輸出
- 控制數字的小數位數與對齊方式

---

### 📖 概念說明

#### print() 進階參數

```python
print(value, ..., sep=" ", end="\n")
```

| 參數 | 說明 | 預設值 |
|------|------|------|
| `sep` | 多筆資料之間的分隔字元 | 一個空格 |
| `end` | 輸出結束後的字元 | 換行 `\n` |

```python
print(1, 2, 3, sep="-")       # 輸出：1-2-3
print("A", end="")
print("B")                     # 輸出：AB（不換行繼續）
```

#### f-string 格式化

```python
name = "小明"
score = 92.5
print(f"姓名：{name}，分數：{score:.1f}")  # 輸出：姓名：小明，分數：92.5
```

f-string 格式控制：

| 格式 | 說明 | 範例 |
|------|------|------|
| `:.2f` | 小數 2 位 | `f"{3.14159:.2f}"` → `3.14` |
| `:>10` | 靠右對齊，寬度 10 | `f"{'hi':>10}"` → `        hi` |
| `:<10` | 靠左對齊，寬度 10 | `f"{'hi':<10}"` → `hi        ` |
| `:^10` | 置中對齊，寬度 10 | `f"{'hi':^10}"` → `    hi    ` |
| `:05d` | 整數補零，寬度 5 | `f"{42:05d}"` → `00042` |

---

### 💻 範例程式

```python
# 商品清單輸出
items = [("咖啡", 120, 2), ("三明治", 85, 1), ("果汁", 60, 3)]

print(f"{'品名':<8} {'單價':>6} {'數量':>4} {'小計':>6}")
print("-" * 30)
total = 0
for name, price, qty in items:
    subtotal = price * qty
    total += subtotal
    print(f"{name:<8} {price:>6} {qty:>4} {subtotal:>6}")
print("-" * 30)
print(f"{'總計':<8} {total:>17}")
```

**輸出：**
```
品名        單價   數量   小計
------------------------------
咖啡         120      2    240
三明治        85      1     85
果汁          60      3    180
------------------------------
總計                        505
```

---

### ✏️ 練習題

**題目 1：填空，讓輸出符合預期**

```python
name = "Alice"
score = 92.5
rank = 3

# 預期輸出：姓名：Alice，分數：92.50，名次：03
print(f"姓名：{name}，分數：{score:___}，名次：{rank:___}")
```

> **提示**：小數保留 2 位用 `.2f`，整數補零寬度 2 用 `02d`

<details>
<summary>✅ 答案</summary>

```python
print(f"姓名：{name}，分數：{score:.2f}，名次：{rank:02d}")
```

</details>

---

**題目 2：修改程式，讓三行輸出在同一行，用 ` | ` 分隔**

```python
print("Python")
print("Java")
print("C++")
# 預期輸出：Python | Java | C++
```

<details>
<summary>✅ 答案</summary>

```python
print("Python", "Java", "C++", sep=" | ")
```

</details>

---

**題目 3：補全程式，輸出對齊的九九乘法表（只要第 2、3 段）**

```python
for i in range(2, 4):
    for j in range(1, 10):
        print(f"{i}x{j}=___", end="  ")   # 填入格式，結果靠右對齊寬度 2
    print()
```

<details>
<summary>✅ 答案</summary>

```python
for i in range(2, 4):
    for j in range(1, 10):
        print(f"{i}x{j}={i*j:>2}", end="  ")
    print()
```

</details>

---

## Unit 2｜input 輸入與運算

### 🎯 學習目標

- 熟練使用 `input()` 搭配型別轉換
- 使用 `eval()` 處理字串運算式
- 設計互動式計算程式

---

### 📖 概念說明

#### input() 與型別轉換

```python
# input() 回傳值永遠是字串，數值計算前必須轉型
x = int(input("整數："))
y = float(input("小數："))
```

#### eval() 解析運算式

```python
formula = input("輸入算式：")   # 例如：3 + 5 * 2
result = eval(formula)          # 直接計算字串中的算式 → 13
```

> ⚠️ `eval()` 會執行任意 Python 程式碼，只用在信任的輸入來源。

#### 一行輸入多個值

```python
# 用 split() 分割，再各別轉型
a, b = input("輸入兩個整數（空格分隔）：").split()
a, b = int(a), int(b)
print(a + b)
```

---

### 💻 範例程式

```python
# BMI 計算器
height = float(input("請輸入身高（公尺）："))
weight = float(input("請輸入體重（公斤）："))
bmi = weight / (height ** 2)

if bmi < 18.5:
    status = "體重過輕"
elif bmi < 24:
    status = "正常範圍"
elif bmi < 27:
    status = "過重"
else:
    status = "肥胖"

print(f"BMI = {bmi:.1f}，{status}")
```

---

### ✏️ 練習題

**題目 1：填入正確的轉換函式**

```python
# 計算圓面積，π ≈ 3.14159
r = ___(input("輸入半徑："))    # 半徑可能是小數
area = 3.14159 * r ** 2
print(f"面積 = {area:.2f}")
```

<details>
<summary>✅ 答案</summary>

```python
r = float(input("輸入半徑："))
```

</details>

---

**題目 2：補全程式，計算三科成績平均**

```python
scores = []
for subject in ["國文", "數學", "英文"]:
    s = ___(input(f"{subject}成績："))
    scores.___（s）             # 把分數加入串列

avg = ___（scores）/ len(scores)
print(f"平均：{avg:.1f}")
```

<details>
<summary>✅ 答案</summary>

```python
scores = []
for subject in ["國文", "數學", "英文"]:
    s = int(input(f"{subject}成績："))
    scores.append(s)

avg = sum(scores) / len(scores)
print(f"平均：{avg:.1f}")
```

</details>

---

**題目 3：使用 eval() 補全簡易計算機**

```python
print("簡易計算機（輸入算式，例如：3+5*2）")
formula = input("算式：")
result = ___（formula）
print(f"結果：{result}")
```

<details>
<summary>✅ 答案</summary>

```python
result = eval(formula)
```

</details>

---

## Unit 3｜if 條件判斷

### 🎯 學習目標

- 使用關係運算子和邏輯運算子組合條件
- 使用巢狀 if 處理多層條件
- 了解三元運算式

---

### 📖 概念說明

#### 邏輯運算子

| 運算子 | 說明 | 範例 |
|-------|------|------|
| `and` | 兩個條件都要成立 | `x > 0 and x < 10` |
| `or` | 其中一個成立即可 | `x < 0 or x > 100` |
| `not` | 反轉條件 | `not (x == 5)` |

#### 巢狀 if

```python
age = int(input("年齡："))
has_id = input("有帶證件嗎？(y/n)：")

if age >= 18:
    if has_id == "y":
        print("可以進入")
    else:
        print("需要出示證件")
else:
    print("未成年，不可進入")
```

#### 三元運算式

```python
# 一行寫完 if/else
result = "及格" if score >= 60 else "不及格"
```

---

### 💻 範例程式

```python
# 判斷能否借書（需為會員且無逾期）
is_member = input("是會員嗎？(y/n)：") == "y"
overdue = int(input("逾期書籍數量："))

if is_member and overdue == 0:
    print("可以借書")
elif is_member and overdue > 0:
    print(f"請先歸還 {overdue} 本逾期書籍")
else:
    print("請先辦理會員")
```

---

### ✏️ 練習題

**題目 1：補全條件，判斷某年是否為閏年**

閏年條件：能被 4 整除且不被 100 整除，或能被 400 整除

```python
year = int(input("輸入年份："))
if (year % 4 == 0 ___ year % 100 != 0) ___ (year % 400 == 0):
    print("閏年")
else:
    print("平年")
```

> 括號內的兩個條件要「同時成立」，括號之間是「其中一個成立即可」

<details>
<summary>✅ 答案</summary>

```python
if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
```

</details>

---

**題目 2：用三元運算式改寫下面的 if/else**

```python
x = int(input("輸入整數："))
if x >= 0:
    sign = "非負數"
else:
    sign = "負數"
print(sign)
```

<details>
<summary>✅ 答案</summary>

```python
x = int(input("輸入整數："))
sign = "非負數" if x >= 0 else "負數"
print(sign)
```

</details>

---

**題目 3：補全程式，驗證密碼強度**

密碼強度規則：長度 >= 8 為「強」，>= 6 為「中」，否則為「弱」

```python
pwd = input("輸入密碼：")
length = len(pwd)

if ___:
    strength = "強"
elif ___:
    strength = "中"
else:
    strength = "弱"
print(f"密碼強度：{strength}")
```

<details>
<summary>✅ 答案</summary>

```python
if length >= 8:
    strength = "強"
elif length >= 6:
    strength = "中"
else:
    strength = "弱"
```

</details>

---

## Unit 4｜多條件 if

### 🎯 學習目標

- 使用 `if/elif/else` 設計多段條件邏輯
- 掌握條件順序對結果的影響
- 組合邏輯運算子減少 elif 數量

---

### 📖 概念說明

#### elif 重點

```python
score = int(input("分數："))

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"
```

條件要從**嚴格（高分）到寬鬆（低分）**寫，因為走到 `elif score >= 80` 時，已確定 score < 90。

#### 組合邏輯減少 elif

```python
# 判斷季節（月份）
month = int(input("月份："))
if 3 <= month <= 5:
    season = "春"
elif 6 <= month <= 8:
    season = "夏"
elif 9 <= month <= 11:
    season = "秋"
else:
    season = "冬"
```

Python 支援連鎖比較：`3 <= month <= 5` 等同於 `month >= 3 and month <= 5`。

---

### 💻 範例程式

```python
# 快遞費用計算（依重量分段）
weight = float(input("包裹重量（kg）："))

if weight <= 1:
    fee = 60
elif weight <= 3:
    fee = 80
elif weight <= 5:
    fee = 120
else:
    extra_kg = weight - 5
    fee = 120 + extra_kg * 20

print(f"運費：{fee} 元")
```

---

### ✏️ 練習題

**題目 1：補全成績等第程式（A/B/C/D/F）**

```python
score = int(input("輸入成績（0-100）："))

if score >= ___:
    grade = "A"
elif score >= ___:
    grade = "B"
elif score >= ___:
    grade = "C"
elif score >= ___:
    grade = "D"
else:
    grade = "F"

print(f"等第：{grade}")
```

> 參考：A≥90, B≥80, C≥70, D≥60

<details>
<summary>✅ 答案</summary>

```python
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"
```

</details>

---

**題目 2：補全月份判斷季節的程式**

```python
month = int(input("輸入月份（1-12）："))

if ___ <= month <= ___:
    season = "春（3-5月）"
elif ___ <= month <= ___:
    season = "夏（6-8月）"
elif ___ <= month <= ___:
    season = "秋（9-11月）"
else:
    season = "冬（12-2月）"

print(season)
```

<details>
<summary>✅ 答案</summary>

```python
if 3 <= month <= 5:
    season = "春（3-5月）"
elif 6 <= month <= 8:
    season = "夏（6-8月）"
elif 9 <= month <= 11:
    season = "秋（9-11月）"
else:
    season = "冬（12-2月）"
```

</details>

---

**題目 3：以下程式輸入 85 時輸出為何？說明原因。**

```python
x = 85
if x > 60:
    print("及格")
elif x > 70:
    print("良好")
elif x > 80:
    print("優良")
```

填入輸出結果：`___`，原因：___

<details>
<summary>✅ 答案</summary>

輸出：`及格`  
原因：85 > 60 成立，第一個 if 區塊執行後，後面的 elif 不再判斷。條件應從嚴格（高分）到寬鬆（低分）排列。

</details>

---

## Unit 5｜list 串列

### 🎯 學習目標

- 熟練串列的建立、存取、切片操作
- 使用常用串列方法：append、insert、pop、sort
- 使用統計函式 max、min、sum、len

---

### 📖 概念說明

#### 基本操作

```python
nums = [5, 3, 8, 1, 9, 2]

# 索引存取
print(nums[0])     # 5（第一個）
print(nums[-1])    # 2（最後一個）

# 切片
print(nums[1:4])   # [3, 8, 1]（索引 1 到 3）
print(nums[::2])   # [5, 8, 9]（每隔一個取）
```

#### 常用方法

| 方法 | 說明 | 範例 |
|------|------|------|
| `append(x)` | 末尾新增 | `nums.append(7)` |
| `insert(i, x)` | 在索引 i 插入 | `nums.insert(0, 99)` |
| `pop()` | 移除並回傳最後一個 | `nums.pop()` |
| `pop(i)` | 移除並回傳索引 i | `nums.pop(2)` |
| `sort()` | 原地排序（升冪） | `nums.sort()` |
| `sort(reverse=True)` | 原地排序（降冪） | `nums.sort(reverse=True)` |
| `remove(x)` | 移除第一個值為 x | `nums.remove(3)` |
| `index(x)` | 取得 x 的索引 | `nums.index(8)` |
| `count(x)` | 計算 x 出現次數 | `nums.count(1)` |

#### 統計函式

```python
scores = [85, 92, 78, 65, 90]
print(max(scores))    # 92
print(min(scores))    # 65
print(sum(scores))    # 410
print(len(scores))    # 5
```

---

### 💻 範例程式

```python
# 成績管理程式
scores = []
names = ["小明", "小華", "小麗", "阿強"]

for name in names:
    s = int(input(f"{name} 的成績："))
    scores.append(s)

avg = sum(scores) / len(scores)
print(f"\n班級平均：{avg:.1f}")
print(f"最高分：{max(scores)} — {names[scores.index(max(scores))]}")
print(f"最低分：{min(scores)} — {names[scores.index(min(scores))]}")
```

---

### ✏️ 練習題

**題目 1：填空，完成串列操作**

```python
fruits = ["apple", "banana", "cherry"]

# 1. 在末尾加入 "date"
fruits.___("date")

# 2. 取出並移除 "banana"（索引 1）
removed = fruits.___(1)

# 3. 排序
fruits.___()

print(fruits)    # 預期：['apple', 'cherry', 'date']
print(removed)   # 預期：banana
```

<details>
<summary>✅ 答案</summary>

```python
fruits.append("date")
removed = fruits.pop(1)
fruits.sort()
```

</details>

---

**題目 2：補全切片操作**

```python
nums = [10, 20, 30, 40, 50, 60, 70, 80]

print(nums[___:___])    # 取出 [30, 40, 50]（索引 2 到 4）
print(nums[___:___:___])  # 取出 [10, 30, 50, 70]（每隔一個）
print(nums[___:])       # 取出後半段 [50, 60, 70, 80]
```

<details>
<summary>✅ 答案</summary>

```python
print(nums[2:5])      # [30, 40, 50]
print(nums[::2])      # [10, 30, 50, 70]
print(nums[4:])       # [50, 60, 70, 80]
```

</details>

---

**題目 3：找出串列中所有大於 60 的分數，存入新串列**

```python
scores = [45, 78, 92, 55, 63, 88, 41, 70]
passing = []

for s in scores:
    if ___:
        passing.___

print("及格分數：", passing)
```

<details>
<summary>✅ 答案</summary>

```python
for s in scores:
    if s > 60:
        passing.append(s)
```

</details>

---

## Unit 6｜range 數列

### 🎯 學習目標

- 熟練 `range(start, stop, step)` 三參數用法
- 使用負數 step 產生遞減數列
- 搭配 `sum()` 計算數列總和

---

### 📖 概念說明

#### range() 詳細用法

```python
range(stop)           # 0 到 stop-1
range(start, stop)    # start 到 stop-1
range(start, stop, step)  # start 到 stop-1，間距 step
```

| 範例 | 產生的數字 |
|------|----------|
| `range(5)` | 0, 1, 2, 3, 4 |
| `range(1, 6)` | 1, 2, 3, 4, 5 |
| `range(0, 10, 2)` | 0, 2, 4, 6, 8 |
| `range(10, 0, -1)` | 10, 9, 8, ..., 1 |
| `range(10, 0, -2)` | 10, 8, 6, 4, 2 |

#### 轉換與計算

```python
print(list(range(1, 6)))             # [1, 2, 3, 4, 5]
print(sum(range(1, 101)))            # 5050（1 到 100 的總和）
print(list(range(10, 0, -1)))        # [10, 9, 8, ..., 1]
```

---

### 💻 範例程式

```python
# 列印星號三角形
n = int(input("輸入層數："))
for i in range(1, n + 1):
    print("*" * i)

# 反向倒數
print("\n倒數計時：")
for i in range(5, 0, -1):
    print(i, end=" ")
print("發射！")
```

---

### ✏️ 練習題

**題目 1：填空，產生指定數列**

```python
# 產生 [2, 4, 6, 8, 10]
print(list(range(___, ___, ___)))

# 產生 [10, 7, 4, 1]
print(list(range(___, ___, ___)))

# 計算 1 到 50 中所有奇數的總和
odd_sum = sum(range(___, ___, ___))
print(odd_sum)    # 預期：625
```

<details>
<summary>✅ 答案</summary>

```python
print(list(range(2, 11, 2)))       # [2, 4, 6, 8, 10]
print(list(range(10, 0, -3)))      # [10, 7, 4, 1]
odd_sum = sum(range(1, 51, 2))     # 625
```

</details>

---

**題目 2：補全程式，印出乘法表（1 到 9 的 5 倍數）**

```python
for i in range(___, ___, ___):
    print(f"5 x {i // 5} = {i}")
```

> 提示：直接產生 5, 10, 15, ..., 45

<details>
<summary>✅ 答案</summary>

```python
for i in range(5, 50, 5):
    print(f"5 x {i // 5} = {i}")
```

</details>

---

**題目 3：利用 range 計算以下總和**

```python
# 計算 100 + 98 + 96 + ... + 2 的總和
total = sum(range(___, ___, ___))
print(total)    # 預期：2550
```

<details>
<summary>✅ 答案</summary>

```python
total = sum(range(100, 0, -2))    # 100, 98, ..., 2
print(total)    # 2550
```

</details>

---

## Unit 7｜for 迴圈

### 🎯 學習目標

- 熟練 for 迴圈走訪串列和 range
- 使用 `enumerate()` 同時取得索引和值
- 使用 `zip()` 同時走訪多個串列

---

### 📖 概念說明

#### 基本走訪

```python
for 元素 in 串列:
    # 每次取出一個元素
```

#### enumerate() — 同時取索引和值

```python
fruits = ["蘋果", "香蕉", "橘子"]
for i, fruit in enumerate(fruits):
    print(f"{i}. {fruit}")
# 輸出：
# 0. 蘋果
# 1. 香蕉
# 2. 橘子
```

#### zip() — 同時走訪兩個串列

```python
names = ["小明", "小華", "小麗"]
scores = [85, 92, 78]

for name, score in zip(names, scores):
    print(f"{name}：{score} 分")
```

#### 計數與累加模式

```python
# 累加
total = 0
for x in nums:
    total += x

# 計數符合條件的元素
count = 0
for x in nums:
    if x > 60:
        count += 1
```

---

### 💻 範例程式

```python
# 成績分析
scores = [78, 65, 92, 88, 45, 73, 56, 84]
names = [f"學生{i+1}" for i in range(len(scores))]

passing = 0
total = 0
for name, score in zip(names, scores):
    total += score
    if score >= 60:
        passing += 1
    status = "✓" if score >= 60 else "✗"
    print(f"{name}: {score:3d} {status}")

print(f"\n平均：{total/len(scores):.1f}，及格人數：{passing}/{len(scores)}")
```

---

### ✏️ 練習題

**題目 1：用 enumerate 改寫，加入編號（從 1 開始）**

```python
items = ["Python", "Java", "C++", "JavaScript"]
for ___, ___ in enumerate(items, ___):   # 從 1 開始編號
    print(f"{num}. {lang}")
```

<details>
<summary>✅ 答案</summary>

```python
for num, lang in enumerate(items, 1):
    print(f"{num}. {lang}")
```

</details>

---

**題目 2：補全程式，找出串列中最大值和其索引**

```python
nums = [34, 67, 12, 89, 45, 78]
max_val = nums[0]
max_idx = 0

for ___, ___ in enumerate(nums):
    if ___ > max_val:
        max_val = ___
        max_idx = ___

print(f"最大值：{max_val}，位於索引 {max_idx}")
```

<details>
<summary>✅ 答案</summary>

```python
for i, val in enumerate(nums):
    if val > max_val:
        max_val = val
        max_idx = i
```

</details>

---

**題目 3：用 zip 計算每位學生的總分**

```python
names = ["小明", "小華", "小麗"]
chinese = [88, 75, 92]
math = [76, 83, 68]
english = [90, 70, 85]

for name, c, m, e in zip(___, ___, ___, ___):
    total = c + m + e
    print(f"{name} 總分：{total}")
```

<details>
<summary>✅ 答案</summary>

```python
for name, c, m, e in zip(names, chinese, math, english):
    total = c + m + e
    print(f"{name} 總分：{total}")
```

</details>

---

## Unit 8｜迴圈應用

### 🎯 學習目標

- 使用 `while` 迴圈配合條件控制
- 使用 `break` 和 `continue` 控制迴圈流程
- 設計巢狀迴圈解決二維問題

---

### 📖 概念說明

#### while 迴圈

```python
while 條件:
    執行內容
    # 記得更新條件，否則無窮迴圈！
```

#### break 與 continue

```python
# break：立即跳出迴圈
for i in range(10):
    if i == 5:
        break       # i=5 時跳出
    print(i)        # 印出 0, 1, 2, 3, 4

# continue：跳過這次，繼續下一次
for i in range(10):
    if i % 2 == 0:
        continue    # 跳過偶數
    print(i)        # 印出 1, 3, 5, 7, 9
```

#### 巢狀迴圈

```python
for i in range(1, 4):
    for j in range(1, 4):
        print(f"({i},{j})", end=" ")
    print()
```

---

### 💻 範例程式

```python
# 猜數字遊戲
import random
secret = random.randint(1, 100)
attempts = 0

while True:
    guess = int(input("猜一個 1-100 的數字："))
    attempts += 1
    
    if guess < secret:
        print("太小了！")
    elif guess > secret:
        print("太大了！")
    else:
        print(f"答對了！共猜了 {attempts} 次")
        break
```

---

### ✏️ 練習題

**題目 1：補全 while 迴圈，計算輸入數字的總和（輸入 0 結束）**

```python
total = 0
while ___:
    n = int(input("輸入數字（0 結束）："))
    if n == ___:
        ___
    total += n

print(f"總和：{total}")
```

<details>
<summary>✅ 答案</summary>

```python
total = 0
while True:
    n = int(input("輸入數字（0 結束）："))
    if n == 0:
        break
    total += n

print(f"總和：{total}")
```

</details>

---

**題目 2：用 continue 跳過 3 的倍數，印出 1-20 中非 3 的倍數**

```python
for i in range(1, 21):
    if i % 3 == ___:
        ___
    print(i, end=" ")
```

<details>
<summary>✅ 答案</summary>

```python
for i in range(1, 21):
    if i % 3 == 0:
        continue
    print(i, end=" ")
```

</details>

---

**題目 3：補全巢狀迴圈，印出九九乘法表的前三段（1-3）**

```python
for i in range(1, ___):
    for j in range(1, ___):
        print(f"{i}x{j}={i*j:2d}", end="  ")
    print()
```

<details>
<summary>✅ 答案</summary>

```python
for i in range(1, 4):
    for j in range(1, 10):
        print(f"{i}x{j}={i*j:2d}", end="  ")
    print()
```

</details>
