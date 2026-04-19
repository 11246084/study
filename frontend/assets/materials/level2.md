# Python 程式設計教材 — Level 2 標準版

> **適合對象**：理解基礎概念，需要熟練語法與實際應用的同學  
> **教材風格**：一般說明 ＋ 部分程式碼需補全 ＋ 方向性提示  
> **認知負荷**：中 ── 說明與練習並重，部分程式需自行補全  
> **學習方式**：練習與應用達成目標

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

- 掌握 `print()` 的完整語法參數（sep、end）
- 使用 `%`、`format()`、`f-string` 三種格式化輸出方式
- 精準控制數字的輸出寬度與小數位數

---

### 📖 概念說明

#### 4-2-1 print() 基本語法

```python
print(value, ..., sep=" ", end="\n", file=sys.stdout, flush=False)
```

| 參數 | 說明 | 預設值 |
|------|------|------|
| `value` | 要輸出的資料，可同時輸出多筆（逗號分隔）| — |
| `sep` | 多筆資料之間的分隔字元 | 一個空格 |
| `end` | 輸出結束後插入的字元 | 換行 `\n` |
| `file` | 輸出位置 | 螢幕（sys.stdout）|

```python
# 程式實例 ch4_1.py
print(1 + 2, 3 + 4)                   # 輸出：3 7
print(1 + 2, 3 + 4, sep=" $$$ ")      # 輸出：3 $$$ 7
print("A", end="")
print("B")                             # 輸出：AB（不換行）
```

---

#### 4-2-2 格式化輸出（% 方式）

```python
print("…格式區…" % (變數, ...))
```

| 格式符 | 說明 |
|-------|------|
| `%d` | 整數 |
| `%f` | 浮點數 |
| `%s` | 字串 |
| `%x` | 16 進位整數（小寫）|
| `%e` | 科學記號（小寫 e）|

```python
# 程式實例 ch4_3.py
name = "Alice"
score = 92.5
print("姓名：%s，分數：%f" % (name, score))
# 輸出：姓名：Alice，分數：92.500000
```

---

#### 4-2-3 精準控制格式化輸出

| 格式 | 說明 |
|------|------|
| `%5d` | 整數，寬度 5，靠右對齊 |
| `%-5d` | 整數，寬度 5，靠左對齊 |
| `%8.2f` | 浮點數，總寬度 8，小數 2 位 |
| `%.2f` | 浮點數，小數 2 位 |
| `%+d` | 顯示正負號 |

```python
# 程式實例 ch4_5.py
pi = 3.14159
print("%10.3f" % pi)    # 輸出：     3.142（總寬度10，小數3位）
print("%-10.3f|" % pi)  # 輸出：3.142     |（靠左對齊）
```

---

#### 4-2-4 format() 函式

```python
print("…格式區…".format(變數, ...))
```

```python
# 程式實例 ch4_9.py
name = "Bob"
score = 88
print("姓名：{}，分數：{}".format(name, score))
print("姓名：{0}，分數：{1}".format(name, score))  # 指定編號

# 對齊方式
print("{:>10}".format("right"))   # 靠右對齊，寬度 10
print("{:<10}".format("left"))    # 靠左對齊，寬度 10
print("{:^10}".format("center"))  # 置中對齊，寬度 10
```

---

#### 4-2-5 f-string（推薦使用，Python 3.6+）

```python
name = "Carol"
score = 95.5
print(f"姓名：{name}，分數：{score:.2f}")
# 輸出：姓名：Carol，分數：95.50
```

---

### ✏️ 練習題

**題目 1：填空（格式符）**

填入正確的格式符，讓輸出結果符合說明：

```python
name = "Alice"
score = 92.5
rank = 3

# 請將 ___ 填入正確格式符
print("姓名：___，分數：___，名次：___" % (name, score, rank))
# 預期輸出：姓名：Alice，分數：92.500000，名次：3
```

> 💡 **提示**：字串用 `%s`，浮點數用 `%f`，整數用 `%d`

---

**題目 2：修改程式**

修改下面程式，讓 pi 只顯示到小數點後 2 位，且總寬度為 8：

```python
pi = 3.14159
print("圓周率 = %f" % pi)   # 請修改此行
```

> 💡 **提示**：使用 `%8.2f` 控制寬度和小數位數

---

**題目 3：改寫為 f-string**

將下面的 `%` 格式化改寫成 f-string：

```python
item = "咖啡"
price = 120
qty = 3
total = price * qty
print("品項：%s，單價：%d，數量：%d，總價：%d" % (item, price, qty, total))
```

---

## Unit 2｜input 輸入與運算

### 🎯 學習目標

- 使用 `input()` 取得使用者輸入
- 使用 `int()`、`float()` 進行型別轉換
- 了解 `eval()` 的用途與使用時機

---

### 📖 概念說明

#### 4-3 input() 基本語法

```python
value = input("prompt: ")
```

- `value` 是字串型別（str）
- 需要數值運算時，必須用 `int()` 或 `float()` 轉換

```python
# 程式實例 ch4_16.py
x = input("請輸入數字：")     # x 是字串
x = int(x)                    # 轉為整數
print("輸入值的兩倍是：", x * 2)
```

---

#### 4-4 eval() 處理字串運算式

```python
result = eval(expression)    # expression 是字串
```

`eval()` 可以解析字串為 Python 運算式，直接計算結果。

```python
# 程式實例 ch4_17.py
formula = input("請輸入公式：")   # 例如輸入：3 + 5 * 2
result = eval(formula)
print("計算結果：", result)       # 輸出：13
```

```python
# 程式實例 ch4_19.py：輸入三個數字計算平均（各數字用逗號分隔）
data = input("輸入三個數字（逗號分隔）：")   # 例如：10,20,30
a, b, c = eval(data)
print("平均值：", (a + b + c) / 3)
```

> ⚠️ `eval()` 會執行任意 Python 程式碼，使用時需注意安全性。

---

### ✏️ 練習題

**題目 1：填空（型別轉換）**

填入正確的函式，完成 BMI 計算程式：

```python
height = ___(input("請輸入身高（公尺）："))    # 需要小數，用哪個函式？
weight = ___(input("請輸入體重（公斤）："))    # 需要小數，用哪個函式？
bmi = weight / (height ** 2)
print(f"您的 BMI 是：{bmi:.1f}")
```

---

**題目 2：修改程式**

下面程式有錯誤，請找出並修正：

```python
a = input("第一個數：")
b = input("第二個數：")
print("相乘結果：", a * b)
```

> 💡 **提示**：想想 `a` 和 `b` 現在是什麼型別？

---

**題目 3：應用**

使用 `eval()` 設計一個「公式計算器」，讓使用者輸入任意數學算式，輸出計算結果（保留 2 位小數）。

---

## Unit 3｜if 條件判斷

### 🎯 學習目標

- 使用關係運算子和邏輯運算子組合條件
- 使用 `if`、`if...else` 語法
- 了解 PEP 8 建議的 if 寫作風格

---

### 📖 概念說明

#### 5-1 關係運算子

| 運算子 | 意義 | 範例 |
|-------|------|------|
| `==` | 等於 | `x == 5` |
| `!=` | 不等於 | `x != 0` |
| `>` | 大於 | `score > 60` |
| `<` | 小於 | `age < 18` |
| `>=` | 大於等於 | `score >= 90` |
| `<=` | 小於等於 | `bmi <= 24.9` |

---

#### 5-2 邏輯運算子

| 運算子 | 意義 | 說明 |
|-------|------|------|
| `and` | 且 | 兩個條件都要成立 |
| `or` | 或 | 至少一個條件成立 |
| `not` | 非 | 反轉條件 |

```python
# 範例
if score >= 60 and score < 70:
    print("D 等第")
if age < 6 or age > 65:
    print("優惠票")
if not is_raining:
    print("今天適合出門")
```

---

#### 5-3 / 5-4 if 與 if...else 語法

```python
# if 語法
if 條件:
    程式碼區塊

# if...else 語法
if 條件:
    條件成立時執行
else:
    條件不成立時執行
```

#### PEP 8 風格建議

```python
# 傳統寫法（可以但不建議）
if x % 2 == 0:
    print("偶數")

# PEP 8 建議（直接判斷 True/False）
is_even = (x % 2 == 0)
if is_even:
    print("偶數")

# 三元運算式（Python 精神）
max_val = x if x > y else y
```

---

### ✏️ 練習題

**題目 1：填空**

完成判斷使用者是否符合投票資格的程式（年齡 >= 20 且為台灣公民）：

```python
age = int(input("年齡："))
citizen = input("是否為台灣公民？(y/n)：")

if ___ and ___:           # 填入兩個條件
    print("您有投票資格")
else:
    print("您沒有投票資格")
```

---

**題目 2：修改程式**

將下面程式改寫成 Python 三元運算式（一行解決）：

```python
x = int(input("輸入數字："))
y = int(input("輸入數字："))
if x > y:
    bigger = x
else:
    bigger = y
print("較大值：", bigger)
```

---

**題目 3：應用**

設計程式，輸入一個整數，判斷它是「正數」、「負數」還是「零」，並以 `if...else` 輸出結果。

---

## Unit 4｜多條件 if

### 🎯 學習目標

- 使用 `if...elif...else` 處理多個條件分支
- 設計 BMI 判斷程式
- 理解條件判斷的執行順序

---

### 📖 概念說明

#### 5-5 if...elif...else 語法

```python
if 條件一:
    執行區塊一
elif 條件二:
    執行區塊二
elif 條件三:
    執行區塊三
else:
    以上都不符合時執行
```

```python
# 程式實例 ch5_6.py：成績等第
score = int(input("請輸入分數："))
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
print(f"等第：{grade}")
```

---

#### 5-6 專題：BMI 判斷

BMI = 體重(kg) / 身高(m)²

| BMI 範圍 | 判斷 |
|---------|------|
| < 18.5 | 體重過輕 |
| 18.5 ~ 24.9 | 體重正常 |
| 25.0 ~ 29.9 | 體重過重 |
| ≥ 30.0 | 肥胖 |

```python
# 程式實例 ch5_7.py
height = float(input("請輸入身高（公尺）："))
weight = float(input("請輸入體重（公斤）："))
bmi = weight / height ** 2
print(f"BMI = {bmi:.1f}")

if bmi < 18.5:
    print("體重過輕")
elif bmi < 25:
    print("體重正常")
elif bmi < 30:
    print("體重過重")
else:
    print("肥胖")
```

---

### ✏️ 練習題

**題目 1：填空**

完成計程車計費程式（前 1.5 公里基本費 85 元，之後每 0.3 公里 5 元）：

```python
km = float(input("請輸入里程（公里）："))

if km <= 1.5:
    fee = 85
elif ___:                        # 填入條件
    extra = ___                  # 計算超出的公里數
    fee = 85 + int(extra / 0.3) * 5
print(f"費用：{fee} 元")
```

---

**題目 2：修改程式**

下面的程式邏輯有問題，請找出並修正（測試輸入 95）：

```python
score = 95
if score >= 60:
    print("D")
elif score >= 70:
    print("C")
elif score >= 80:
    print("B")
elif score >= 90:
    print("A")
```

> 💡 **提示**：思考條件判斷的執行順序。

---

**題目 3：應用**

設計「電費計算程式」，輸入用電度數，依下列費率計算電費：
- 前 120 度：每度 1.63 元
- 121~330 度：每度 2.38 元
- 331 度以上：每度 3.52 元

---

## Unit 5｜list 串列

### 🎯 學習目標

- 建立、讀取、修改、刪除串列元素
- 使用切片（slice）存取串列範圍
- 使用常用方法：`append`、`insert`、`pop`、`remove`、`sort`
- 理解串列常用統計函式

---

### 📖 概念說明

#### 6-1 串列基本操作

```python
# 建立串列
fruits = ["蘋果", "香蕉", "西瓜", "葡萄"]

# 讀取（正向索引從 0，反向從 -1）
print(fruits[0])    # 蘋果
print(fruits[-1])   # 葡萄

# 修改
fruits[1] = "草莓"

# 刪除
del fruits[2]
```

#### 串列切片 [start:end:step]

```python
x = [10, 20, 30, 40, 50]
print(x[1:3])    # [20, 30]（含start，不含end）
print(x[:3])     # [10, 20, 30]（前三個）
print(x[2:])     # [30, 40, 50]（從索引2到最後）
print(x[-2:])    # [40, 50]（後兩個）
print(x[::2])    # [10, 30, 50]（每隔一個取一個）
```

#### 串列統計函式

```python
scores = [80, 92, 75, 88, 95]
print(max(scores))   # 95
print(min(scores))   # 75
print(sum(scores))   # 430
print(len(scores))   # 5
```

---

#### 6-4 增加與刪除元素

```python
lst = ["A", "B", "C"]
lst.append("D")        # 末端新增 → ['A','B','C','D']
lst.insert(1, "X")     # 索引1插入 → ['A','X','B','C','D']
lst.pop()              # 刪除末端 → ['A','X','B','C']
lst.pop(0)             # 刪除索引0 → ['X','B','C']
lst.remove("B")        # 刪除第一個 'B' → ['X','C']
```

---

#### 6-5 串列排序

```python
nums = [3, 1, 4, 1, 5, 9, 2]
nums.sort()                    # 原地排序（由小到大）
nums.sort(reverse=True)        # 原地排序（由大到小）
new_nums = sorted(nums)        # 回傳新串列（不改變原串列）
nums.reverse()                 # 顛倒排列
```

---

#### 6-7 二維串列

```python
scores = [
    ["Alice", 85, 90, 78],
    ["Bob",   92, 88, 95],
    ["Carol", 70, 75, 80],
]
print(scores[0][0])   # Alice
print(scores[1][2])   # 88
```

---

### ✏️ 練習題

**題目 1：填空**

完成計算串列平均值的程式：

```python
grades = [78, 85, 92, 60, 74]
total = ___            # 用一個函式取得總和
count = ___            # 用一個函式取得元素數量
avg = total / count
print(f"平均分數：{avg:.1f}")
```

---

**題目 2：修改程式**

下面是管理學生名單的程式，請修改讓它能正確執行：

```python
students = ["Alice", "Bob", "Carol", "David"]
students.append["Eve"]          # 第一個錯誤
students.remove("Bob", "Carol") # 第二個錯誤
print(sorted(students, True))   # 第三個錯誤
```

---

**題目 3：應用**

給定以下 James 球員的得分串列，請計算：
1. 最高分、最低分
2. 平均分（保留 1 位小數）
3. 前三場比賽的得分

```python
james = [23, 35, 18, 42, 29, 31, 27, 38, 20, 33]
```

---

## Unit 6｜range 數列

### 🎯 學習目標

- 使用 `range()` 的三種參數形式
- 使用串列生成式（list comprehension）
- 在串列生成式中加入條件過濾

---

### 📖 概念說明

#### 7-2 range() 函式

```python
range(stop)              # 0 到 stop-1
range(start, stop)       # start 到 stop-1
range(start, stop, step) # start 到 stop-1，間隔 step
```

```python
# 範例
print(list(range(5)))          # [0, 1, 2, 3, 4]
print(list(range(2, 7)))       # [2, 3, 4, 5, 6]
print(list(range(0, 11, 2)))   # [0, 2, 4, 6, 8, 10]
print(list(range(10, 0, -2)))  # [10, 8, 6, 4, 2]
```

---

#### 7-2-5 串列生成式（List Comprehension）

```python
# 傳統寫法
squares = []
for n in range(1, 6):
    squares.append(n ** 2)

# 串列生成式（Python 精神）
squares = [n ** 2 for n in range(1, 6)]
print(squares)   # [1, 4, 9, 16, 25]
```

---

#### 7-2-6 含條件式的串列生成

```python
# 語法
新串列 = [運算式 for 項目 in 可迭代物件 if 條件式]

# 範例：取 1~10 中的偶數
evens = [n for n in range(1, 11) if n % 2 == 0]
print(evens)   # [2, 4, 6, 8, 10]
```

---

### ✏️ 練習題

**題目 1：填空**

填入正確的 range() 參數，產生指定的數列：

```python
# 產生：5, 6, 7, 8, 9
print(list(range(___, ___)))

# 產生：1, 3, 5, 7, 9
print(list(range(___, ___, ___)))

# 產生：10, 8, 6, 4, 2
print(list(range(___, ___, ___)))
```

---

**題目 2：改寫為串列生成式**

將下面的傳統 for 迴圈改寫成一行串列生成式：

```python
result = []
for n in range(1, 11):
    if n % 3 == 0:
        result.append(n * n)
print(result)
```

---

**題目 3：應用**

使用串列生成式，找出 1~100 中所有能被 3 整除但不能被 9 整除的數字。

> 💡 **提示**：在條件式中同時使用 `%3 == 0` 和 `%9 != 0`

---

## Unit 7｜for 迴圈

### 🎯 學習目標

- 使用 `for` 迴圈遍歷串列和 range()
- 使用 `break` 強制離開迴圈
- 使用 `continue` 跳過當次迴圈
- 理解 `for...else` 語法
- 使用巢狀 for 迴圈

---

### 📖 概念說明

#### 7-1 for 迴圈基本語法

```python
for var in 可迭代物件:
    程式碼區塊
```

```python
# 程式實例 ch7_3.py：多行程式碼區塊
players = ["jordan", "james", "kobe"]
for player in players:
    player_upper = player.upper()   # 轉大寫
    print(f"球員：{player_upper}")
```

---

#### 7-3-2 break 強制離開

```python
# 程式實例 ch7_19.py
scores = [85, 92, 78, 95, 60]
limit = int(input("要顯示幾位球員？"))
for i, score in enumerate(scores):
    if i >= limit:
        break
    print(f"第 {i+1} 位：{score} 分")
```

---

#### 7-3-3 continue 跳過

```python
# 計算 scores 中大於等於 80 分的場次
scores = [85, 62, 78, 95, 55, 91]
count = 0
for s in scores:
    if s < 80:
        continue        # 低於 80 跳過
    count += 1
print(f"80分以上共 {count} 場")
```

---

#### 7-3-4 for...else

```python
# 只要迴圈正常結束（沒有 break），才執行 else
for n in range(2, 10):
    for i in range(2, n):
        if n % i == 0:
            break
    else:
        print(f"{n} 是質數")
```

---

#### 7-3-1 巢狀 for 迴圈

```python
# 程式實例 ch7_17.py：九九乘法表
for i in range(1, 10):
    for j in range(1, 10):
        print(f"{i}×{j}={i*j:2d}", end="  ")
    print()   # 換行
```

---

### ✏️ 練習題

**題目 1：填空（continue 應用）**

填入缺少的程式碼，跳過串列中的負數，只印出正數：

```python
nums = [3, -1, 7, -5, 2, -8, 4]
for n in nums:
    if ___:           # 填入跳過的條件
        ___           # 填入跳過的指令
    print(n)
```

---

**題目 2：修改程式**

下面程式想在找到目標值後立即停止，但有問題，請修正：

```python
target = 42
data = [15, 28, 42, 67, 33]
for n in data:
    if n == target:
        print(f"找到了！位置：{data.index(n)}")
    continue          # 這行是否正確？
print("搜尋結束")
```

---

**題目 3：應用**

使用巢狀 for 迴圈，印出以下圖案（n = 4）：

```
*
**
***
****
```

---

## Unit 8｜迴圈應用

### 🎯 學習目標

- 使用 `while` 迴圈和巢狀 while
- 在 while 迴圈中使用 `break` 和 `continue`
- 結合串列與 while 迴圈進行資料處理
- 熟悉累加、計數等常見迴圈應用模式

---

### 📖 概念說明

#### 7-4 while 迴圈語法

```python
while 條件運算:
    程式區塊
```

```python
# 程式實例 ch7_22.py：持續輸入直到輸入 q
active = True
while active:
    text = input("請輸入（q 結束）：")
    if text == "q":
        active = False
    else:
        print(f"你輸入了：{text}")
```

---

#### 7-4-3 while + break

```python
while True:                         # 永遠執行
    text = input("請輸入（q 結束）：")
    if text == "q":
        break                       # 符合條件才離開
    print(f"你說：{text}")
```

---

#### 7-4-4 while + continue

```python
# 跳過偶數，只印奇數
i = 0
while i < 10:
    i += 1
    if i % 2 == 0:
        continue
    print(i)
```

---

#### while 結合串列：移除特定元素

```python
# 程式實例 ch7_26.py：刪除所有 apple
fruits = ["apple", "banana", "apple", "cherry", "apple"]
while "apple" in fruits:
    fruits.remove("apple")
print(fruits)   # ['banana', 'cherry']
```

---

#### while 結合串列：分類資料

```python
# 程式實例 ch7_27.py：依消費金額分類 VIP 和 Gold 買家
buyers = [["Alice", 1200], ["Bob", 800], ["Carol", 1500], ["David", 600]]
vip = []
gold = []
while buyers:
    buyer = buyers.pop(0)          # 取出第一個
    if buyer[1] >= 1000:
        vip.append(buyer)
    else:
        gold.append(buyer)
print("VIP:", vip)
print("Gold:", gold)
```

---

### ✏️ 練習題

**題目 1：填空**

完成一個「猜數字」程式，讓使用者猜 1~10 之間的數字（答案是 7），猜對才結束：

```python
answer = 7
while ___:                               # 填入迴圈條件
    guess = int(input("猜一個 1~10 的數字："))
    if guess == answer:
        print("猜對了！")
        ___                              # 填入離開迴圈的指令
    elif guess < answer:
        print("太小了")
    else:
        print("太大了")
```

---

**題目 2：修改程式**

下面程式想計算使用者輸入數字的總和（輸入 0 結束），請找出並修正錯誤：

```python
total = 0
while True:
    num = int(input("輸入數字（0 結束）："))
    total = total + num
    if num = 0:           # 錯誤一
        break
print("總和：", Total)    # 錯誤二
```

---

**題目 3：應用**

使用 while 迴圈搭配串列，設計一個「成績輸入系統」：
- 持續輸入學生成績（輸入 -1 結束）
- 輸入結束後，印出所有成績、最高分、最低分和平均分

---

*Level 2 標準版 ── 完*  
*前後測與 Level 1、Level 3 使用相同評量題目，確保跨層次比較公平*
