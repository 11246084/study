# 113 學年度全國高級中等學校商業類技藝競賽【程式設計】學科正式試題

> 來源：教育部依法令舉辦之競賽試題（著作權法第 9 條不受著作權保護，可直接收錄）。
> 選擇題共 25 題、每題 4 分。本檔為掃描卷人工轉錄，供題庫收錄比對用。
> 標注【單元對應】以本平台 8 單元分類；★答案為轉錄時人工推算，待與官方答案核對。

## 第 1 頁（題 1–4）

1. 執行以下 Python 程式片段，其結果為何？
   ```python
   x = 5; y = 3
   print((x ** y) % 4)
   ```
   (A) 0 (B) 1 (C) 2 (D) 3
   ★答案：(B)（125 % 4 = 1）【單元對應：U1 運算子】

2. 執行以下 Python 程式片段，其結果為何？
   ```python
   a = [1, 2, 3, 4]
   b = [2, 3, 4, 5]
   total = 0
   for i in range(4):
       total += a[i] * b[i]
   print(total % 4)
   ```
   (A) 0 (B) 1 (C) 2 (D) 3
   ★答案：(A)（2+6+12+20=40，40%4=0）【單元對應：U5/U6 串列＋迴圈】

3. 執行以下 Python 程式片段，其結果為何？
   ```python
   count = 0
   for i in range(3):
       for j in range(i, 5):
           count += 1
   print(count % 4)
   ```
   (A) 0 (B) 1 (C) 2 (D) 3
   ★答案：(A)（5+4+3=12，12%4=0）【單元對應：U3/U4 巢狀迴圈】

4. 執行以下 Python 程式片段，其結果為何？
   ```python
   a = 7; b = 3
   while a > b:
       a -= b
   print(a % 4)
   ```
   (A) 0 (B) 1 (C) 2 (D) 3
   ★答案：(B)（7→4→1，1%4=1）【單元對應：U3 while 迴圈】

## 第 2 頁（題 5–10）

5. 執行以下 Python 程式片段，其結果為何？
   ```python
   a, b = 8, 4
   c = 0
   while b > 0:
       c += a % b
       b -= 1
   print(c % 4)
   ```
   (A) 0 (B) 1 (C) 2 (D) 3
   ★答案：(C)（8%4=0、8%3=2、8%2=0、8%1=0，c=2）【單元對應：U3 while】

6. 執行以下 Python 程式片段，其結果為何？
   ```python
   def calculate(n):
       if n == 0:
           return 0
       return n + calculate(n - 1)
   print(calculate(4) % 4)
   ```
   (A) 0 (B) 1 (C) 2 (D) 3
   ★答案：(C)（4+3+2+1=10，10%4=2）【單元對應：U8 遞迴】

7. 執行以下 Python 程式片段，其結果為何？
   ```python
   values = [i * 2 for i in range(1, 6)]
   print(sum(values) % 4)
   ```
   (A) 0 (B) 1 (C) 2 (D) 3
   ★答案：(C)（[2,4,6,8,10] 和 30，30%4=2）【單元對應：U6 串列生成式】

8. 執行以下 Python 程式片段，其結果為何？
   ```python
   print('NO' if str(101) != str(101)[::-1] else 'YES', end=" ")
   print('NO' if str(11) != str(11)[::-1] else 'YES')
   ```
   (A) YES YES (B) NO NO (C) YES NO (D) NO YES
   ★答案：(A)（101 與 11 都是回文）【單元對應：U5 字串切片】

9. 執行以下 Python 程式片段，其結果為何？
   ```python
   result = 0
   for i in range(1, 6):
       if i % 2 == 0:
           result += i
   print(result % 4)
   ```
   (A) 0 (B) 1 (C) 2 (D) 3
   ★答案：(C)（2+4=6，6%4=2）【單元對應：U3/U4 迴圈＋條件】

10. 執行以下 Python 程式片段，其結果為何？
    ```python
    def factorial(n):
        if n == 0:
            return 1
        return n * factorial(n-1)
    print(factorial(3) % 4)
    ```
    (A) 0 (B) 1 (C) 2 (D) 3
    ★答案：(C)（3!=6，6%4=2）【單元對應：U8 遞迴】

## 第 3 頁（題 11–16）

11. 執行以下 Python 程式片段，其結果為何？
    ```python
    x = 5
    y = 7
    result = (x << 1) + (y >> 1)
    print(result % 4)
    ```
    (A) 0 (B) 1 (C) 2 (D) 3
    ★答案：(B)（10+3=13，13%4=1）【單元對應：超綱（位元運算，課程未教）— 收錄需改寫或棄用】

12. 執行以下 Python 程式片段，其結果為何？
    ```python
    n = 0
    for i in range(10):
        if i % 3 == 0:
            n += i
    print(n % 4)
    ```
    (A) 0 (B) 1 (C) 2 (D) 3
    ★答案：(C)（0+3+6+9=18，18%4=2）【單元對應：U3/U4 迴圈＋條件】

13. 執行以下 Python 程式片段，其結果為何？
    ```python
    total = 0
    for i in range(1, 11):
        if i % 3 == 0:
            total += 1
    print(total % 4)
    ```
    (A) 0 (B) 1 (C) 2 (D) 3
    ★答案：(D)（3、6、9 共 3 個，3%4=3）【單元對應：U3/U4 計數器】

14. 執行下列 Python 程式片段，輸出結果為何？
    ```python
    def triangle_number(n):
        return n * (n + 1) // 2
    print(triangle_number(10) % 4)
    ```
    (A) 0 (B) 1 (C) 2 (D) 3
    ★答案：(D)（55%4=3）【單元對應：U7 函式】

15. 執行以下 Python 程式片段，其結果為何？
    ```python
    total = 0
    for i in range(1, 6, 2):
        total += i ** 2
    print(total % 4)
    ```
    (A) 0 (B) 1 (C) 2 (D) 3
    ★答案：(D)（1+9+25=35，35%4=3）【單元對應：U3 range 步進】

16. 執行以下 Python 程式片段，其結果為何？
    ```python
    orders = [100, 150, 200, 80, 120]
    avg_orders = sum(orders) / len(orders)
    below_avg = [o for o in orders if o < avg_orders]
    print(len(below_avg) % 4)
    ```
    (A) 0 (B) 1 (C) 2 (D) 3
    ★答案：(D)（平均 130，低於平均 100/80/120 共 3 個）【單元對應：U6 串列生成式】

## 第 4 頁（題 17–21）

17. 執行以下 Python 程式片段，其結果為何？
    ```python
    a = [1, 2, 3, 4, 5]
    b = [x * 2 for x in a if x % 2 == 0]
    print(sum(b) % 4)
    ```
    (A) 0 (B) 1 (C) 2 (D) 3
    ★答案：(A)（偶數 2、4 → [4,8]，和 12，12%4=0）【單元對應：U6 串列生成式＋條件】

18. 執行以下 Python 程式片段，其結果為何？
    ```python
    x = 0
    for i in range(3):
        for j in range(3):
            x += i * j
    print(x % 4)
    ```
    (A) 0 (B) 1 (C) 2 (D) 3
    ★答案：(B)（Σi×Σj＝3×3=9，9%4=1）【單元對應：U4 巢狀迴圈】

19. 執行以下 Python 程式片段，其結果為何？
    ```python
    dp = [0 for _ in range(10)]
    dp[0], dp[1], dp[2] = 1, 2, 2
    for i in range(3, 8):
        dp[i] = dp[i - 2] + dp[i - 3]
    print(dp[5] % 4)
    ```
    (A) 0 (B) 1 (C) 2 (D) 3
    ★答案：(B)（dp[3]=3、dp[4]=4、dp[5]=dp[3]+dp[2]=5，5%4=1）【單元對應：U6/U8 串列＋遞推（難題）】

20. 執行以下 Python 程式片段，其結果為何？
    ```python
    a = [[0] * 3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            a[i][j] = i + j
    print(a[2][2] % 4)
    ```
    (A) 0 (B) 1 (C) 2 (D) 3
    ★答案：(A)（a[2][2]=4，4%4=0）【單元對應：U4/U6 二維串列（難題）】

21. 執行以下 Python 程式片段，其結果為何？
    ```python
    def calc(x):
        if x == 0:
            return 4
        return calc(x - 1) + 4
    print(calc(3) % 4)
    ```
    (A) 0 (B) 1 (C) 2 (D) 3
    ★答案：(A)（4×4=16，16%4=0）【單元對應：U8 遞迴】

## 第 5 頁（題 22–25）

22. 執行以下 Python 程式片段，其結果為何？
    ```python
    total = 0
    for i in range(1, 5):
        total += i * (5 - i)
    print(total % 4)
    ```
    (A) 0 (B) 1 (C) 2 (D) 3
    ★答案：(A)（4+6+6+4=20，20%4=0）【單元對應：U3/U4 迴圈累加】

23. 執行以下 Python 程式片段，其結果為何？
    ```python
    def calc(x):
        if x < 2:
            return x
        return calc(x - 1) + calc(x - 2)
    print(calc(5) % 4)
    ```
    (A) 0 (B) 1 (C) 2 (D) 3
    ★答案：(B)（費氏數列 calc(5)=5，5%4=1）【單元對應：U8 遞迴（難題）】

24. 執行以下 Python 程式片段，其結果為何？
    ```python
    a = 1
    for i in range(1, 4):
        a = a + a * i
    print(a % 4)
    ```
    (A) 0 (B) 1 (C) 2 (D) 3
    ★答案：(A)（1→2→6→24，24%4=0）【單元對應：U3/U4 迴圈追蹤】

25. 執行以下 Python 程式片段，其結果為何？
    ```python
    a = 5; b = 10
    A1 = a < b and b > 15
    A2 = a < b or b < 15
    print(f"{A1} {A2}")
    ```
    (A) True True (B) False False (C) Tru False (D) False True
    ★答案：(D)（A1=True and False=False；A2=True or True=True）【單元對應：U2 邏輯運算子】

## 官方答案卷核對（掃描第 7 頁）

官方答案：1B 2A 3A 4B 5C 6C 7C 8A 9C 10C／11B 12C 13D 14D 15D 16D 17A 18B 19B 20A／21A 22A 23B 24A 25D

**核對結果：本檔 25 題★答案與官方答案卷完全一致，轉錄與驗算均已確認。**

## 收錄建議（按單元分組）

- U2 條件/邏輯：25
- U3 迴圈基礎：4、5、9、12、15、22、24
- U4 巢狀迴圈/演算法：3、13、18、20
- U5 字串：8
- U6 串列/生成式：2、7、16、17、19
- U7 函式：14
- U8 遞迴：6、10、21、23
- U1 運算子：1（(x**y)%4 可直接放 U1 進階）
- 棄用/需改寫：11（位元運算 << >> 課程未教）
