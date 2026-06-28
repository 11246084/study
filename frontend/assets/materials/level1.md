# Python 四日實作課程 — Level 1 補救版

> 適合第一次接觸程式，或需要較多範例與步驟提示的學習者。
> 每個單元採「看懂 → 跟著做 → 改一點 → 自己做」四步驟。

## 四日學習路線

| 日期 | 上午 | 下午 |
|---|---|---|
| 7/6 | Unit 1 基礎環境與 I/O | Unit 2 條件判斷 |
| 7/7 | Unit 3 迴圈入門 | Unit 4 迴圈練習 |
| 7/8 | Unit 5 List／String | Unit 6 資料實戰 |
| 7/9 | Unit 7 函式 | Unit 8 遞迴／字典 |

> 遇到錯誤很正常。先看錯誤發生的列，再檢查括號、引號、冒號與縮排。

---

## Unit 1｜環境、變數、資料型態與 I/O

### 今天只要掌握四件事

1. `print()` 把結果顯示出來。
2. 變數替資料取名字。
3. `input()` 取得使用者輸入。
4. `int()`、`float()` 把文字轉成數字。

```python
print("Hello, Python!")

name = input("你的名字：")
age = int(input("你的年齡："))
next_age = age + 1

print(f"你好 {name}，明年你是 {next_age} 歲")
```

### 逐行理解

- `name = ...`：把輸入內容交給 `name`。
- `int(...)`：因為 `input()` 得到的是文字，所以先轉成整數。
- `f"...{name}..."`：把變數放入文字。

### 跟著做

```python
width = float(input("長方形的寬："))
height = float(input("長方形的高："))
area = width * height
print(f"面積是 {area}")
```

### 小任務

- 把面積程式增加「周長」。
- 輸入攝氏溫度，計算華氏溫度：`C * 9 / 5 + 32`。

---

## Unit 2｜條件判斷 If／Elif／Else

條件判斷讓程式根據不同情況做不同事情。

```python
temperature = float(input("體溫："))

if temperature > 37.5:
    print("發燒")
elif temperature < 36:
    print("體溫偏低")
else:
    print("正常")
```

### 記住

- 條件後面要有冒號 `:`。
- 分支裡面的程式要縮排四格。
- `if` 是第一個條件，`elif` 是其他條件，`else` 是剩餘情況。

### 比較與組合

| 寫法 | 意思 |
|---|---|
| `a == b` | 相等 |
| `a != b` | 不相等 |
| `a >= b` | 大於等於 |
| `x >= 1 and x <= 10` | 兩個條件都成立 |
| `day == 6 or day == 7` | 至少一個成立 |

### 小任務

1. 判斷整數是正數、負數或零。
2. 判斷成績是否及格。
3. 將成績分成 A、B、C、D、F。

---

## Unit 3｜For／While 與基礎演算法

### For：已經知道要做幾次

```python
for number in range(1, 6):
    print(number)
```

`range(1, 6)` 會產生 1、2、3、4、5，不包含 6。

### While：做到條件不成立為止

```python
count = 1
while count <= 5:
    print(count)
    count += 1
```

若忘記 `count += 1`，條件會一直成立，形成無限迴圈。

### 累加器

```python
total = 0
for number in range(1, 6):
    total = total + number
print(total)
```

### 小任務

- 印出 1 到 10 的偶數。
- 計算 1 到 100 的總和。
- 持續輸入數字，輸入 0 時停止。

---

## Unit 4｜迴圈實作與基礎題庫

### 解題四步驟

1. 寫出一組輸入與預期輸出。
2. 找出「重複做的事情」。
3. 決定使用 `for` 或 `while`。
4. 用簡單資料測試，再測試邊界。

### 範例：星號三角形

```python
for row in range(1, 6):
    print("*" * row)
```

### 範例：找最大值

```python
numbers = [3, 8, 2, 10, 5]
largest = numbers[0]

for number in numbers:
    if number > largest:
        largest = number

print(largest)
```

### 練習階梯

- 基礎：印出 2、4、6、8、10。
- 基礎：計算 5 的階乘。
- 標準：印出九九乘法表。
- 挑戰：猜數字，提示太大或太小。

---

## Unit 5｜List 與 String 進階操作

### List 是一排可以修改的資料

```python
fruits = ["蘋果", "香蕉", "西瓜"]
print(fruits[0])
print(fruits[-1])

fruits.append("芒果")
fruits[1] = "草莓"
print(fruits)
```

索引從 0 開始。`-1` 代表最後一個。

### String 也是有順序的資料

```python
text = "  Hello Python  "
cleaned = text.strip()
print(cleaned.lower())
print(cleaned[0:5])
```

### 拆開與組合

```python
data = "Amy,88,92"
parts = data.split(",")
print(parts)
print(" / ".join(parts))
```

### 延伸：Tuple

`("Amy", 88)` 是元組。它和串列相似，但建立後不能修改。

---

## Unit 6｜串列與字串實戰題庫

### 範例：成績統計

```python
scores = [80, 65, 92, 58, 77]
passed = []

for score in scores:
    if score >= 60:
        passed.append(score)

print(f"及格成績：{passed}")
print(f"及格人數：{len(passed)}")
```

### 範例：回文

```python
text = input("輸入文字：").replace(" ", "").lower()

if text == text[::-1]:
    print("是回文")
else:
    print("不是回文")
```

### 練習階梯

1. 找出串列中的所有偶數。
2. 統計字串中有幾個英文字母。
3. 將逗號分隔的名字清理空白後排序。
4. 找出兩個串列共同擁有的元素。

---

## Unit 7｜函式與模組化

函式把一段工作包起來，之後可以重複呼叫。

```python
def greet(name):
    message = f"你好，{name}！"
    return message


result = greet("Amy")
print(result)
```

### 函式的三個部分

- 函式名稱：`greet`
- 參數：`name`
- 回傳值：`return message`

```python
def rectangle_area(width, height):
    return width * height


print(rectangle_area(8, 5))
```

### 小任務

- 寫 `is_even(number)`，回傳布林值。
- 寫 `grade(score)`，回傳成績等第。
- 把 BMI 程式拆成「計算」與「判斷」兩個函式。

---

## Unit 8｜遞迴與 Dictionary 應用

### Dictionary 用鍵找到值

```python
student = {
    "name": "Amy",
    "score": 88,
}

print(student["name"])
student["score"] = 92
student["class"] = "A"
```

### 遍歷字典

```python
for key, value in student.items():
    print(key, value)
```

### 遞迴是函式呼叫自己

```python
def countdown(number):
    if number == 0:
        print("完成")
        return
    print(number)
    countdown(number - 1)
```

`number == 0` 是終止條件。沒有終止條件，函式就不會停。

### 延伸：Set

```python
names = ["Amy", "Bob", "Amy"]
unique_names = set(names)
print(unique_names)
```

### 整合任務

建立簡易成績簿：使用字典保存三位學生的成績，使用函式新增資料，最後輸出全班平均。

---

## 我的除錯清單

- [ ] 引號與括號有成對嗎？
- [ ] `if`、`for`、`while`、`def` 後面有冒號嗎？
- [ ] 縮排是否一致？
- [ ] `input()` 的文字需要轉成數字嗎？
- [ ] 變數名稱是否拼錯？
- [ ] 迴圈是否真的會停止？
