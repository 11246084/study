"""Assessment banks aligned with the four-day, eight-unit curriculum."""


def mc(content, correct, *distractors, concept='', pattern=''):
    choices = [(correct, True), *[(item, False) for item in distractors]]
    return {'content': content, 'choices': choices, 'explanation': f'正確答案：{correct}',
            'concept': concept, 'pattern': pattern}


def short(content, answer, explanation='', concept='', pattern=''):
    return {'content': content, 'correct_answer': answer, 'explanation': explanation or f'答案：{answer}',
            'concept': concept, 'pattern': pattern}


def fb(content, *answers, explanation=''):
    """程式填空題：內文以 __1__、__2__ 標記空格。

    每個位置參數對應一格答案；傳 list/tuple 代表同一格的多個可接受寫法。
    空格只挖「答案唯一」的位置（運算子、關鍵字、方法名、參數），
    比對時忽略空白、保留大小寫，逐格計分。
    """
    lines = []
    for answer in answers:
        if isinstance(answer, (list, tuple)):
            lines.append('|||'.join(answer))
        else:
            lines.append(answer)
    display = '；'.join(f'空格{i}: {line.split("|||")[0]}' for i, line in enumerate(lines, start=1))
    return {'content': content, 'correct_answer': '\n'.join(lines),
            'explanation': explanation or f'答案 — {display}'}


QUIZ_QUESTIONS = [
    [
        mc('input() 回傳的預設資料型態是？', 'str', 'int', 'float', 'bool'),
        mc('哪一個運算子可取得整除後的商？', '//', '/', '%', '**'),
        mc('要把文字 "25" 轉為整數，應使用？', 'int("25")', 'str(25)', 'float("25")', 'type("25")'),
        mc('哪一個是合法的變數名稱？', 'student_score', '2score', 'student-score', 'class'),
    ],
    [
        mc('Python 判斷相等使用哪個運算子？', '==', '=', '!=', '>='),
        mc('if 條件成立後的程式區塊靠什麼表示？', '縮排', '大括號', '小括號', '分號'),
        mc('多個互斥範圍判斷最適合使用？', 'if / elif / else', 'for / while', 'try / except', 'def / return'),
        mc('條件「年齡介於 13 到 17」可寫成？', '13 <= age <= 17', 'age >= 13 or age <= 17', '13 < age > 17', 'age = 13..17'),
    ],
    [
        mc('已知重複次數時通常優先使用？', 'for', 'while', 'if', 'def'),
        mc('range(1, 6) 最後一個數字是？', '5', '6', '4', '1'),
        mc('while 迴圈最容易因哪個問題無法停止？', '條件所需的變數沒有更新', '使用 print()', '使用整數', '有縮排'),
        mc('累加器 total 通常應先設定為？', '0', '1', '-1', 'None'),
    ],
    [
        mc('在迴圈中立刻停止重複應使用？', 'break', 'continue', 'return', 'pass'),
        mc('略過本次、繼續下一次迴圈應使用？', 'continue', 'break', 'else', 'input'),
        mc('巢狀迴圈最適合處理哪種資料？', '列與欄組成的表格', '單一布林值', '單一字串', '一個變數名稱'),
        mc('找最大值時，largest 最安全的初值是？', '第一個資料', '固定為 0', '固定為 100', '空字串'),
    ],
    [
        mc('Python 串列的第一個索引是？', '0', '1', '-1', '視長度而定'),
        mc('在串列末端加入元素使用？', 'append()', 'add()', 'push()', 'join()'),
        mc('字串與串列都支援哪項操作？', '切片', '直接修改任意元素', 'append()', 'sort()'),
        mc('哪個方法會移除字串兩端空白？', 'strip()', 'split()', 'join()', 'find()'),
    ],
    [
        mc('把 "Amy,88" 依逗號拆開使用？', 'split(",")', 'join(",")', 'strip(",")', 'find(",")'),
        mc('將字串串列接成一行使用？', '分隔字串.join(串列)', '串列.split()', '串列.append()', 'str.sort()'),
        mc('取得串列元素數量使用？', 'len()', 'count()', 'size()', 'type()'),
        mc('建立排序後的新串列且保留原串列使用？', 'sorted()', 'sort()', 'reverse()', 'index()'),
    ],
    [
        mc('函式定義使用哪個關鍵字？', 'def', 'func', 'function', 'return'),
        mc('函式將結果交回呼叫端使用？', 'return', 'print', 'input', 'break'),
        mc('只在函式內有效的變數稱為？', '區域變數', '全域變數', '常數', '模組'),
        mc('把程式拆成多個單一職責函式的主要好處是？', '容易理解、測試與重用', '一定執行更快', '不需要變數', '不會發生錯誤'),
    ],
    [
        mc('遞迴函式不可缺少的是？', '終止條件', '全域變數', 'while 迴圈', '字串'),
        mc('字典以什麼方式保存資料？', '鍵與值', '只有索引', '只有字串', '固定順序的數字'),
        mc('同時遍歷字典的鍵和值使用？', 'items()', 'keys()', 'values()', 'append()'),
        mc('移除重複元素最適合使用？', 'set', 'list', 'str', 'float'),
    ],
]


SHORT_ANSWER_QUESTIONS = [
    [
        short('input("年齡：") 的回傳型態名稱是？', 'str'),
        short('17 // 5 的結果是？', '3'),
        short('17 % 5 的結果是？', '2'),
        short('將變數 value 轉成浮點數的函式名稱是？', 'float'),
    ],
    [
        short('Python 的「不等於」運算子是？', '!='),
        short('條件同時成立使用哪個邏輯運算子？', 'and'),
        short('score=60 時，score >= 60 的布林結果是？', 'True'),
        short('if 與 else 之間的其他條件分支關鍵字是？', 'elif'),
    ],
    [
        short('range(2, 10, 2) 會產生幾個數字？', '4'),
        short('sum(range(1, 6)) 的結果是？', '15'),
        short('while 迴圈每次執行前會先檢查什麼？', '條件'),
        short('for ch in "Python" 會執行幾次？', '6'),
    ],
    [
        short('停止整個迴圈的關鍵字是？', 'break'),
        short('略過本次迴圈的關鍵字是？', 'continue'),
        short('5 的階乘結果是？', '120'),
        short('1 到 10 的偶數總和是？', '30'),
    ],
    [
        short('[10, 20, 30][-1] 的結果是？', '30'),
        short('"Python"[1:4] 的結果是？', 'yth'),
        short('在串列尾端加入元素的方法名稱是？', 'append'),
        short('將字串轉成小寫的方法名稱是？', 'lower'),
    ],
    [
        short('"Amy,Bob".split(",") 會得到幾個元素？', '2'),
        short('len([3, 1, 4, 1, 5]) 的結果是？', '5'),
        short('[1,2,3,4][::-1] 的第一個元素是？', '4'),
        short('判斷元素是否在串列中的關鍵字是？', 'in'),
    ],
    [
        short('定義函式的關鍵字是？', 'def'),
        short('將函式結果傳回的關鍵字是？', 'return'),
        short('def add(a, b): return a+b；add(2,3) 的結果是？', '5'),
        short('函式說明文字通常稱為？', 'docstring\n---OR---\n文件字串'),
    ],
    [
        short('factorial(4) 的結果是？', '24'),
        short('{"A": 90, "B": 80}["B"] 的結果是？', '80'),
        short('取得字典中不存在的鍵並提供預設值可使用哪個方法？', 'get'),
        short('集合交集使用的運算子是？', '&'),
    ],
]


FILL_BLANK_QUESTIONS = [
    [
        fb('讀入名字並輸出「Hello, 名字」。\n\n```python\nname = __1__()\nprint(f"Hello, {name}")\n```', 'input'),
        fb('讀入兩個整數並輸出總和。\n\n```python\na = __1__(input())\nb = int(input())\nprint(a __2__ b)\n```', 'int', '+'),
        fb('讀入圓半徑並輸出面積，圓周率使用 3.14。\n\n```python\nr = float(input())\nprint(3.14 * r __1__ 2)\n```', '**'),
        fb('讀入秒數，輸出整數分鐘與剩餘秒數。\n\n```python\ns = int(input())\nprint(s __1__ 60, s __2__ 60)\n```', '//', '%'),
    ],
    [
        fb('讀入整數，輸出「偶數」或「奇數」。\n\n```python\nn = int(input())\nif n % 2 __1__ 0:\n    print("偶數")\n__2__:\n    print("奇數")\n```', '==', 'else'),
        fb('讀入成績，60 分以上輸出「及格」，否則輸出「不及格」。\n\n```python\nscore = int(input())\nif score __1__ 60:\n    print("及格")\nelse:\n    print("不及格")\n```', '>='),
        fb('讀入整數，輸出「正數」、「負數」或「零」。\n\n```python\nn = int(input())\nif n > 0:\n    print("正數")\n__1__ n < 0:\n    print("負數")\nelse:\n    print("零")\n```', 'elif'),
        fb('讀入年份，輸出是否為閏年的布林值。\n\n```python\nyear = int(input())\nprint(year % 400 == 0 __1__ (year % 4 == 0 __2__ year % 100 != 0))\n```', 'or', 'and'),
    ],
    [
        fb('使用 for 輸出 1 到 5，每個數字一行。\n\n```python\nfor i in __1__(1, __2__):\n    print(i)\n```', 'range', '6'),
        fb('輸出 1 到 100 的總和。\n\n```python\ntotal = 0\nfor i in range(1, 101):\n    total __1__ i\nprint(total)\n```', '+='),
        fb('使用 while 輸出 1 到 5。\n\n```python\ni = 1\nwhile i __1__ 5:\n    print(i)\n    i += __2__\n```', '<=', '1'),
        fb('輸入 n，輸出 1 到 n 的所有偶數。\n\n```python\nn = int(input())\nfor i in range(2, n + 1, __1__):\n    print(i)\n```', '2'),
    ],
    [
        fb('輸出 1 到 5 的階乘結果（5! = 120）。\n\n```python\nresult = 1\nfor i in range(1, 6):\n    result __1__ i\nprint(result)\n```', '*='),
        fb('印出五列遞增星號三角形。\n\n```python\nfor i in range(1, 6):\n    print("*" __1__ i)\n```', '*'),
        fb('找出 [4, 7, 2, 9, 1] 最大值，不使用 max。\n\n```python\nnums = [4, 7, 2, 9, 1]\nlargest = nums[0]\nfor n in nums:\n    if n __1__ largest:\n        largest = n\nprint(largest)\n```', '>'),
        fb('輸出 1 到 10，但略過 5。\n\n```python\nfor i in range(1, 11):\n    if i == 5:\n        __1__\n    print(i)\n```', 'continue'),
    ],
    [
        fb('建立 [10, 5, 8, 3]，由小到大排序後輸出。\n\n```python\nnums = [10, 5, 8, 3]\nnums.__1__()\nprint(nums)\n```', 'sort'),
        fb('輸出字串 Python 的反轉結果。\n\n```python\ntext = "Python"\nprint(text[::__1__])\n```', '-1'),
        fb('將 "Amy,Bob,Cindy" 依逗號拆開並輸出串列。\n\n```python\ntext = "Amy,Bob,Cindy"\nprint(text.__1__(","))\n```', 'split'),
        fb('建立串列 [1, 2, 3]，加入 4 後輸出。\n\n```python\nnums = [1, 2, 3]\nnums.__1__(4)\nprint(nums)\n```', 'append'),
    ],
    [
        fb('讀入文字，忽略空格與大小寫後判斷是否回文。\n\n```python\ntext = input().replace(" ", "").__1__()\nprint(text __2__ text[::-1])\n```', 'lower', '=='),
        fb('輸出 [88, 45, 72, 95, 60] 中所有及格成績。\n\n```python\nscores = [88, 45, 72, 95, 60]\nprint([s for s in scores __1__ s >= 60])\n```', 'if'),
        fb('輸出 [3, 1, 4, 1, 5] 的平均值。\n\n```python\nnums = [3, 1, 4, 1, 5]\nprint(sum(nums) __1__ len(nums))\n```', '/'),
        fb('將名字串列以「 / 」連接後輸出。\n\n```python\nnames = ["Amy", "Bob", "Cindy"]\nprint(" / ".__1__(names))\n```', 'join'),
    ],
    [
        fb('定義 add(a, b) 回傳總和，並輸出 add(2, 3)。\n\n```python\n__1__ add(a, b):\n    __2__ a + b\nprint(add(2, 3))\n```', 'def', 'return'),
        fb('定義 is_even(n)，回傳是否為偶數。\n\n```python\ndef is_even(n):\n    return n % 2 __1__ 0\n```', '=='),
        fb('定義 area(w, h) 回傳長方形面積。\n\n```python\ndef area(w, h):\n    return w __1__ h\n```', '*'),
        fb('定義 average(numbers) 回傳平均值。\n\n```python\ndef average(numbers):\n    return __1__(numbers) / len(numbers)\n```', 'sum'),
    ],
    [
        fb('用遞迴定義 factorial(n)。\n\n```python\ndef factorial(n):\n    if n <= 1:\n        return __1__\n    return n * __2__(n - 1)\n```', '1', 'factorial'),
        fb('建立 Amy=88、Bob=72 的字典並輸出 Amy 的分數。\n\n```python\nscores = {"Amy": 88, "Bob": 72}\nprint(scores[__1__])\n```', ['"Amy"', "'Amy'"]),
        fb('統計單字串列中每個單字的次數並輸出字典。\n\n```python\nwords = ["a", "b", "a"]\ncounts = {}\nfor word in words:\n    counts[word] = counts.__1__(word, 0) + 1\nprint(counts)\n```', 'get'),
        fb('輸出集合 {1, 2, 3} 與 {2, 3, 4} 的交集。\n\n```python\na = {1, 2, 3}\nb = {2, 3, 4}\nprint(a __1__ b)\n```', '&'),
    ],
]


# 每單元再補 6 個共同概念檢核；Level 1 轉成選擇題，Level 2 使用相同核心概念作簡答。
EXTRA_FACTS = [
    [
        ('print(3 ** 2) 的結果是？', '9', ('6', '8', '32')),
        ('10 / 4 的資料型態名稱是？', 'float', ('int', 'str', 'bool')),
        ('f-string 開頭使用哪個字母？', 'f', ('s', 'p', 'i')),
        ('布林值只有 True 與什麼？', 'False', ('None', '0', 'No')),
        ('type(10) 顯示的核心型態名稱是？', 'int', ('float', 'str', 'bool')),
        ('字串連接通常使用哪個運算子？', '+', ('-', '/', '%')),
    ],
    [
        ('「至少一個條件成立」使用哪個運算子？', 'or', ('and', 'not', 'in')),
        ('反轉布林條件使用哪個運算子？', 'not', ('or', 'and', 'else')),
        ('if True: 下方縮排區塊會執行幾次？', '1', ('0', '2', '無限次')),
        ('判斷 x 在 1 到 10 之間可使用哪種比較？', '1 <= x <= 10', ('x = 1..10', '1 < x > 10', 'x in 1,10')),
        ('else 後面是否需要條件？', '不需要', ('需要', '只能放 True', '只能放 False')),
        ('條件運算式 True and False 的結果是？', 'False', ('True', 'None', '0')),
    ],
    [
        ('range(5) 的第一個數字是？', '0', ('1', '-1', '5')),
        ('range(5) 共產生幾個數字？', '5', ('4', '6', '1')),
        ('range(10, 0, -2) 的最後一個數字是？', '2', ('0', '1', '4')),
        ('每次迴圈讓 count 增加 1 的寫法是？', 'count += 1', ('count = 1', 'count == 1', 'count + 1 ==')),
        ('for 迴圈可以直接走訪字串嗎？', '可以', ('不可以', '只能走訪整數', '只能走訪 range')),
        ('while False: 的區塊會執行幾次？', '0', ('1', '2', '無限次')),
    ],
    [
        ('兩層迴圈各執行 3 次，內層共執行幾次？', '9', ('3', '6', '12')),
        ('判斷 n 是否能被 3 整除使用？', 'n % 3 == 0', ('n / 3 == 0', 'n // 3', 'n == 3')),
        ('找第一個符合條件的資料後通常搭配？', 'break', ('continue', 'pass', 'else')),
        ('計數器 count 記錄符合資料筆數，初值應為？', '0', ('1', '-1', 'None')),
        ('空心圖形通常需要迴圈加上什麼？', '條件判斷', ('函式匯入', '浮點數', '字典')),
        ('演算法測試應包含一般值與什麼？', '邊界值', ('只有最大值', '只有零', '隨意值')),
    ],
    [
        ('[1,2,3][1] 的結果是？', '2', ('1', '3', '0')),
        ('刪除並回傳串列最後元素的方法是？', 'pop', ('remove', 'delete', 'clear')),
        ('依內容刪除第一個符合元素的方法是？', 'remove', ('pop', 'strip', 'find')),
        ('取得元素第一次出現索引的方法是？', 'index', ('count', 'findall', 'position')),
        ('元組建立後可以修改元素嗎？', '不可以', ('可以', '只有數字可以', '只有字串可以')),
        ('"python".upper() 的結果是？', 'PYTHON', ('Python', 'python', 'pYTHON')),
    ],
    [
        ('"a b c".split() 會得到幾個元素？', '3', ('1', '2', '5')),
        ('[1,2,2,3].count(2) 的結果是？', '2', ('1', '3', '4')),
        ('字串是否以指定內容開頭使用哪個方法？', 'startswith', ('endswith', 'find', 'strip')),
        ('串列生成式通常使用哪個迴圈關鍵字？', 'for', ('while', 'if', 'def')),
        ('建立原串列的淺層副本可使用？', 'copy', ('same', 'clone', 'join')),
        ('enumerate() 可同時取得元素與什麼？', '索引', ('型態', '長度', '記憶體')),
    ],
    [
        ('沒有明確 return 的函式預設回傳？', 'None', ('0', 'False', '空字串')),
        ('具有預設值的參數通常放在參數列哪側？', '右側', ('左側', '中間', '任意且無規則')),
        ('呼叫函式時指定參數名稱稱為？', '關鍵字參數', ('區域參數', '匿名參數', '迴圈參數')),
        ('函式內修改全域名稱需使用哪個關鍵字？', 'global', ('public', 'outer', 'static')),
        ('匯入模組使用哪個關鍵字？', 'import', ('include', 'using', 'module')),
        ('lambda 建立的是哪種函式？', '匿名函式', ('遞迴函式', '內建函式', '輸入函式')),
    ],
    [
        ('字典新增或修改資料使用什麼作為索引？', '鍵', ('位置', '長度', '型態')),
        ('取得所有字典鍵的方法是？', 'keys', ('values', 'items', 'getall')),
        ('取得所有字典值的方法是？', 'values', ('keys', 'items', 'append')),
        ('集合聯集運算子是？', '|', ('&', '-', '^')),
        ('集合差集運算子是？', '-', ('+', '&', '|')),
        ('遞迴每次呼叫應讓問題規模如何變化？', '縮小', ('放大', '不變', '隨機')),
    ],
]


FILL_BLANK_EXTRA = [
    [
        fb('輸出文字 Hello Python。\n\n```python\n__1__("Hello Python")\n```', 'print'),
        fb('建立變數 x=10、y=3，輸出 x 乘 y。\n\n```python\nx = 10\ny = 3\nprint(x __1__ y)\n```', '*'),
        fb('讀入整數並輸出它的平方。\n\n```python\nn = int(input())\nprint(n __1__ 2)\n```', '**'),
        fb('讀入攝氏溫度並輸出華氏溫度（公式：C × 9 / 5 + 32）。\n\n```python\nc = __1__(input())\nprint(c * 9 / 5 + __2__)\n```', 'float', '32'),
        fb('輸出 10 除以 3 的商與餘數。\n\n```python\nprint(10 __1__ 3, 10 __2__ 3)\n```', '//', '%'),
        fb('建立 name="Amy" 並用 f-string 輸出 Hello Amy。\n\n```python\nname = "Amy"\nprint(__1__"Hello {name}")\n```', 'f'),
    ],
    [
        fb('讀入整數，若大於 10 就輸出「大」。\n\n```python\nn = int(input())\nif n __1__ 10:\n    print("大")\n```', '>'),
        fb('讀入兩數並輸出較大者。\n\n```python\na = int(input())\nb = int(input())\nif a > b:\n    print(a)\n__1__:\n    print(b)\n```', 'else'),
        fb('讀入年齡，13 到 17 輸出「青少年」。\n\n```python\nage = int(input())\nif 13 __1__ age __2__ 17:\n    print("青少年")\n```', '<=', '<='),
        fb('讀入月份，1 到 12 以外輸出「錯誤」。\n\n```python\nmonth = int(input())\nif month < 1 __1__ month > 12:\n    print("錯誤")\n```', 'or'),
        fb('讀入兩個布林值 a、b，輸出兩者是否同時為真。\n\n```python\na = bool(int(input()))\nb = bool(int(input()))\nprint(a __1__ b)\n```', 'and'),
        fb('讀入分數，依序輸出 A、B 或 C（90、80 為界）。\n\n```python\nscore = int(input())\nif score >= 90:\n    print("A")\n__1__ score >= 80:\n    print("B")\nelse:\n    print("C")\n```', 'elif'),
    ],
    [
        fb('輸出 0 到 4。\n\n```python\nfor i in range(__1__):\n    print(i)\n```', '5'),
        fb('輸出 2 到 10 的偶數。\n\n```python\nfor i in range(2, 11, __1__):\n    print(i)\n```', '2'),
        fb('使用 while 從 5 倒數到 1。\n\n```python\ni = 5\nwhile i >= 1:\n    print(i)\n    i __1__ 1\n```', '-='),
        fb('輸入 n，輸出 1 到 n 的總和。\n\n```python\nn = int(input())\ntotal = 0\nfor i in range(1, n __1__ 1):\n    total += i\nprint(total)\n```', '+'),
        fb('輸出字串 Python 的每個字元。\n\n```python\nfor ch __1__ "Python":\n    print(ch)\n```', 'in'),
        fb('計算 [2, 4, 6, 8] 的總和並輸出。\n\n```python\ntotal = 0\nfor n in [2, 4, 6, 8]:\n    total += n\nprint(__1__)\n```', 'total'),
    ],
    [
        fb('輸出 1 到 20 第一個可被 7 整除的數，之後停止迴圈。\n\n```python\nfor i in range(1, 21):\n    if i % 7 == 0:\n        print(i)\n        __1__\n```', 'break'),
        fb('輸出 1 到 10 中不可被 3 整除的數。\n\n```python\nfor i in range(1, 11):\n    if i % 3 == 0:\n        __1__\n    print(i)\n```', 'continue'),
        fb('用巢狀迴圈輸出 2×2 個星號（同列不換行）。\n\n```python\nfor i in range(2):\n    for j in range(2):\n        print("*", end=__1__)\n    print()\n```', ['""', "''"]),
        fb('計算 [3, 7, 2, 9] 中大於 5 的個數。\n\n```python\ncount = 0\nfor n in [3, 7, 2, 9]:\n    if n > 5:\n        count __1__ 1\nprint(count)\n```', '+='),
        fb('輸出 3 的 1 到 5 倍。\n\n```python\nfor i in range(1, 6):\n    print(3 __1__ i)\n```', '*'),
        fb('找出 [8, 3, 12, 5] 最小值，不使用 min。\n\n```python\nnums = [8, 3, 12, 5]\nsmallest = nums[0]\nfor n in nums:\n    if n __1__ smallest:\n        smallest = n\nprint(smallest)\n```', '<'),
    ],
    [
        fb('輸出 [1, 2, 3, 4] 的前兩個元素。\n\n```python\nnums = [1, 2, 3, 4]\nprint(nums[:__1__])\n```', '2'),
        fb('將 [3, 1, 2] 反向（由大到小）排序後輸出。\n\n```python\nnums = [3, 1, 2]\nnums.sort(reverse=__1__)\nprint(nums)\n```', 'True'),
        fb('移除字串兩端空白並輸出。\n\n```python\ntext = "  Python  "\nprint(text.__1__())\n```', 'strip'),
        fb('輸出 "banana" 中字母 a 的數量。\n\n```python\ntext = "banana"\nprint(text.__1__("a"))\n```', 'count'),
        fb('將 (10, 20) 解包成 x、y 並輸出。\n\n```python\nx, __1__ = (10, 20)\nprint(x, y)\n```', 'y'),
        fb('合併 [1, 2] 與 [3, 4] 後輸出。\n\n```python\na = [1, 2]\nb = [3, 4]\nprint(a __1__ b)\n```', '+'),
    ],
    [
        fb('讀入空格分隔整數並輸出串列。\n\n```python\nnums = [int(x) for x in input().__1__()]\nprint(nums)\n```', 'split'),
        fb('輸出 [1, 2, 3, 4, 5] 中的奇數串列。\n\n```python\nnums = [1, 2, 3, 4, 5]\nprint([n for n in nums if n % 2 == __1__])\n```', '1'),
        fb('將 ["a", "b", "c"] 連成 a-b-c。\n\n```python\nitems = ["a", "b", "c"]\nprint("-".__1__(items))\n```', 'join'),
        fb('輸出 "Python" 是否以 Py 開頭。\n\n```python\nprint("Python".__1__("Py"))\n```', 'startswith'),
        fb('複製 [1, 2, 3]，在副本加入 4 並輸出副本。\n\n```python\noriginal = [1, 2, 3]\ncopied = original.__1__()\ncopied.append(4)\nprint(copied)\n```', 'copy'),
        fb('使用 enumerate 輸出 ["A", "B"] 的索引與內容。\n\n```python\nfor i, value in __1__(["A", "B"]):\n    print(i, value)\n```', 'enumerate'),
    ],
    [
        fb('定義 square(n) 回傳平方。\n\n```python\ndef square(n):\n    return n ** __1__\n```', '2'),
        fb('定義 greet(name="Guest") 回傳 Hello 加名字。\n\n```python\ndef greet(__1__="Guest"):\n    return f"Hello {name}"\n```', 'name'),
        fb('定義 maximum(a, b) 回傳較大值。\n\n```python\ndef maximum(a, b):\n    if a > b:\n        return a\n    __1__ b\n```', 'return'),
        fb('定義 count_even(numbers) 回傳偶數個數。\n\n```python\ndef count_even(numbers):\n    return sum(1 for n in numbers if n % 2 __1__ 0)\n```', '=='),
        fb('定義 first_last(items) 回傳第一與最後元素。\n\n```python\ndef first_last(items):\n    return items[0], items[__1__]\n```', '-1'),
        fb('定義 total(*numbers) 回傳所有參數總和。\n\n```python\ndef total(__1__numbers):\n    return sum(numbers)\n```', '*'),
    ],
    [
        fb('用遞迴定義從 1 加到 n 的函式。\n\n```python\ndef total(n):\n    if n <= 1:\n        return n\n    return n + total(n __1__ 1)\n```', '-'),
        fb('建立空字典，加入鍵 name、值 Amy 並輸出。\n\n```python\ndata = {}\ndata[__1__] = "Amy"\nprint(data)\n```', ['"name"', "'name'"]),
        fb('遍歷 {"A": 1, "B": 2} 並輸出鍵和值。\n\n```python\ndata = {"A": 1, "B": 2}\nfor key, value in data.__1__():\n    print(key, value)\n```', 'items'),
        fb('輸出字典中 x 的值，沒有時輸出 0。\n\n```python\ndata = {}\nprint(data.__1__("x", 0))\n```', 'get'),
        fb('輸出 {1, 2, 3} 與 {3, 4} 的聯集。\n\n```python\na = {1, 2, 3}\nb = {3, 4}\nprint(a __1__ b)\n```', '|'),
        fb('將 [1, 1, 2, 3, 3] 去重後輸出集合。\n\n```python\nnums = [1, 1, 2, 3, 3]\nprint(__1__(nums))\n```', 'set'),
    ],
]


for unit_index, facts in enumerate(EXTRA_FACTS):
    for prompt, answer, distractors in facts:
        QUIZ_QUESTIONS[unit_index].append(mc(prompt, answer, *distractors))
        SHORT_ANSWER_QUESTIONS[unit_index].append(short(prompt, answer))
    FILL_BLANK_QUESTIONS[unit_index].extend(FILL_BLANK_EXTRA[unit_index])


def _number_fact(prompt, answer):
    """Build deterministic numeric distractors without duplicating the answer."""
    value = int(answer)
    wrongs = []
    for candidate in (value + 1, value - 1, value + 2, value * 2 + 1):
        text = str(candidate)
        if text != answer and text not in wrongs:
            wrongs.append(text)
        if len(wrongs) == 3:
            break
    return prompt, answer, tuple(wrongs)


def _generated_fact(unit, index):
    """Generate one concept/trace question for Level 1 and Level 2."""
    mode = index % 6
    a = index + 3
    b = index + 2

    if unit == 0:
        if mode == 0:
            return _number_fact(f'print({a} + {b}) 的結果是？', str(a + b))
        if mode == 1:
            return _number_fact(f'print({a} * {b}) 的結果是？', str(a * b))
        if mode == 2:
            return _number_fact(f'print({a} // {b}) 的結果是？', str(a // b))
        if mode == 3:
            return _number_fact(f'print({a} % {b}) 的結果是？', str(a % b))
        if mode == 4:
            return _number_fact(f'print({b} ** 2) 的結果是？', str(b ** 2))
        return (f'type({a}.0) 的核心型態名稱是？', 'float', ('int', 'str', 'bool'))

    if unit == 1:
        x = index
        threshold = index + 4
        expressions = [
            (f'{x} >= {threshold}', x >= threshold),
            (f'{x} == {threshold}', x == threshold),
            (f'{x} != {threshold}', x != threshold),
            (f'{x} < {threshold} and {x} >= 0', x < threshold and x >= 0),
            (f'{x} < 3 or {x} > 10', x < 3 or x > 10),
            (f'not ({x} > {threshold})', not (x > threshold)),
        ]
        expression, result = expressions[mode]
        answer = str(result)
        return (f'{expression} 的結果是？', answer, ('False' if result else 'True', 'None', 'SyntaxError'))

    if unit == 2:
        n = index + 3
        if mode == 0:
            return _number_fact(f'sum(range(1, {n + 1})) 的結果是？', str(n * (n + 1) // 2))
        if mode == 1:
            return _number_fact(f'len(list(range({n}))) 的結果是？', str(n))
        if mode == 2:
            return _number_fact(f'len(list(range(1, {n + 1}, 2))) 的結果是？', str((n + 1) // 2))
        if mode == 3:
            return _number_fact(f'for i in range({b}) 會執行幾次？', str(b))
        if mode == 4:
            return _number_fact(f'while 從 {n} 每次減 1 到 0，共執行幾次？', str(n))
        return _number_fact(f'字串 "Python{index}" 的 for 迴圈會執行幾次？', str(len(f"Python{index}")))

    if unit == 3:
        n = index + 2
        if mode == 0:
            factorial = 1
            for value in range(1, n + 1):
                factorial *= value
            return _number_fact(f'{n}! 的結果是？', str(factorial))
        if mode == 1:
            return _number_fact(f'1 到 {n * 5} 中有幾個 5 的倍數？', str(n))
        if mode == 2:
            return _number_fact(f'兩層迴圈分別執行 {n} 次與 {b} 次，內層共執行幾次？', str(n * b))
        if mode == 3:
            return _number_fact(f'1 到 {n * 2} 的偶數總和是？', str(n * (n + 1)))
        if mode == 4:
            return _number_fact(f'印出 {n} 列星號三角形，最後一列有幾個星號？', str(n))
        return _number_fact(f'range({n}, 0, -1) 共產生幾個數字？', str(n))

    if unit == 4:
        values = [index + 1, index + 2, index + 3, index + 4]
        if mode == 0:
            pos = index % len(values)
            return _number_fact(f'{values}[{pos}] 的結果是？', str(values[pos]))
        if mode == 1:
            return _number_fact(f'len({values}) 的結果是？', str(len(values)))
        if mode == 2:
            target = values[index % len(values)]
            return _number_fact(f'{values}.count({target}) 的結果是？', str(values.count(target)))
        if mode == 3:
            return (f'"unit{index}".upper() 的結果是？', f'UNIT{index}', (f'Unit{index}', f'unit{index}', f'UNIT {index}'))
        if mode == 4:
            word = f'Python{index}'
            position = index % len(word)
            return (f'"{word}"[{position}] 的結果是？', word[position], ('P', 'n', 'y'))
        return _number_fact(f'元組 ({a}, {b}) 有幾個元素？', '2')

    if unit == 5:
        text = f'a,b,c,{index}'
        if mode == 0:
            return _number_fact(f'len("{text}".split(",")) 的結果是？', '4')
        if mode == 1:
            return (f'"-".join(["A","B","{index}"]) 的結果是？', f'A-B-{index}', (f'AB{index}', f'A,B,{index}', f'A B {index}'))
        if mode == 2:
            return _number_fact(f'[n for n in range({a}) if n % 2 == 0] 有幾個元素？', str((a + 1) // 2))
        if mode == 3:
            return (f'"data{index}"[::-1] 的結果是？', f'{index}atad', (f'data{index}', f'{index}data', f'atad{index}'))
        if mode == 4:
            return _number_fact(f'len(set([{b}, {b}, {a}])) 的結果是？', '2')
        return _number_fact(f'enumerate(["A","B","C"], start={b}) 的第一個索引是？', str(b))

    if unit == 6:
        if mode == 0:
            return _number_fact(f'def f(x): return x+{b}；f({a}) 的結果是？', str(a + b))
        if mode == 1:
            return _number_fact(f'def f(x): return x*{b}；f({a}) 的結果是？', str(a * b))
        if mode == 2:
            return _number_fact(f'def f(a={a}): return a；f() 的結果是？', str(a))
        if mode == 3:
            return _number_fact(f'def f(*args): return len(args)；f(1,2,{a}) 的結果是？', '3')
        if mode == 4:
            return (f'def f_{index}(): pass，呼叫 f_{index}() 時回傳什麼？', 'None', ('0', 'False', '空字串'))
        return (f'要以別名 m{index} 載入 math 模組，應使用哪個關鍵字？', 'import', ('include', 'using', 'export'))

    n = index + 2
    if mode == 0:
        factorial = 1
        for value in range(1, n + 1):
            factorial *= value
        return _number_fact(f'遞迴 factorial({n}) 的結果是？', str(factorial))
    if mode == 1:
        return _number_fact(f'{{"A": {a}, "B": {b}}}["A"] 的結果是？', str(a))
    if mode == 2:
        return _number_fact(f'len({{{a}, {b}, {a}}}) 的結果是？', str(len({a, b})))
    if mode == 3:
        return _number_fact(f'{{"x": {a}}}.get("y", {b}) 的結果是？', str(b))
    if mode == 4:
        return _number_fact(f'集合 {{{a}, {b}}} 與 {{{b}, {n}}} 的交集元素數量是？', str(len({a, b} & {b, n})))
    return _number_fact(f'遞迴從 {n} 倒數到 1，函式共輸出幾個數字？', str(n))


def _generated_fill(unit, index):
    """Generate a distinct fill-blank task for one unit（空格只挖答案唯一處）."""
    a = index + 2
    b = index + 2
    mode = index % 6

    if unit == 0:
        tasks = [
            fb(f'建立 a={a}、b={b} 並輸出兩者總和。\n\n```python\na = {a}\nb = {b}\nprint(a __1__ b)\n```', '+'),
            fb(f'建立 a={a}、b={b} 並輸出兩者乘積。\n\n```python\na = {a}\nb = {b}\nprint(a __1__ b)\n```', '*'),
            fb(f'輸出 {a} 除以 {b} 的整數商。\n\n```python\nprint({a} __1__ {b})\n```', '//'),
            fb(f'輸出 {a} 除以 {b} 的餘數。\n\n```python\nprint({a} __1__ {b})\n```', '%'),
            fb(f'輸出 {b} 的平方。\n\n```python\nprint({b} __1__ 2)\n```', '**'),
            fb(f'用 f-string 輸出「答案={a + b}」。\n\n```python\nanswer = {a + b}\nprint(__1__"答案={{answer}}")\n```', 'f'),
        ]
        return tasks[mode]

    if unit == 1:
        tasks = [
            fb(f'讀入整數，若大於等於 {b} 輸出「通過」，否則輸出「未通過」。\n\n```python\nn = int(input())\nif n __1__ {b}:\n    print("通過")\n__2__:\n    print("未通過")\n```', '>=', 'else'),
            fb(f'讀入整數，判斷是否可被 {b} 整除並輸出布林值。\n\n```python\nn = int(input())\nprint(n % {b} __1__ 0)\n```', '=='),
            fb(f'讀入年齡，介於 {b} 到 {a} 時輸出「符合」。\n\n```python\nage = int(input())\nif {b} __1__ age __2__ {a}:\n    print("符合")\n```', '<=', '<='),
            fb(f'設定 x={a}，用 if/else 輸出「偶數」或「奇數」。\n\n```python\nx = {a}\nif x __1__ 2 == 0:\n    print("偶數")\nelse:\n    print("奇數")\n```', '%'),
            fb('讀入兩個整數，輸出較小值。\n\n```python\na = int(input())\nb = int(input())\nif a < b:\n    print(a)\n__1__:\n    print(b)\n```', 'else'),
            fb(f'讀入分數，{a} 分以上輸出 A，{b} 分以上輸出 B，否則輸出 C。\n\n```python\nscore = int(input())\nif score >= {a}:\n    print("A")\n__1__ score >= {b}:\n    print("B")\nelse:\n    print("C")\n```', 'elif'),
        ]
        return tasks[mode]

    if unit == 2:
        tasks = [
            fb(f'使用 for 輸出 1 到 {b}。\n\n```python\nfor i in range(1, __1__):\n    print(i)\n```', str(b + 1)),
            fb(f'使用 while 輸出 {b} 到 1。\n\n```python\ni = {b}\nwhile i __1__ 1:\n    print(i)\n    i -= 1\n```', '>='),
            fb(f'計算 1 到 {a} 的總和並輸出。\n\n```python\ntotal = 0\nfor i in range(1, {a + 1}):\n    total __1__ i\nprint(total)\n```', '+='),
            fb(f'輸出 0 到 {a} 中可被 {b} 整除的數。\n\n```python\nfor i in range({a + 1}):\n    if i % {b} __1__ 0:\n        print(i)\n```', '=='),
            fb(f'使用 for 將字串 "U{index}" 的字元逐行輸出。\n\n```python\nfor ch __1__ "U{index}":\n    print(ch)\n```', 'in'),
            fb(f'計算 range({b}) 的元素數量並輸出。\n\n```python\ncount = 0\nfor i in range({b}):\n    count += __1__\nprint(count)\n```', '1'),
        ]
        return tasks[mode]

    if unit == 3:
        tasks = [
            fb(f'計算 {b}! 並輸出。\n\n```python\nresult = 1\nfor i in range(1, {b + 1}):\n    result __1__ i\nprint(result)\n```', '*='),
            fb(f'印出 {b} 列遞增星號三角形。\n\n```python\nfor i in range(1, {b + 1}):\n    print("*" __1__ i)\n```', '*'),
            fb(f'輸出 1 到 {a} 第一個可被 {b} 整除的數，之後停止迴圈。\n\n```python\nfor i in range(1, {a + 1}):\n    if i % {b} == 0:\n        print(i)\n        __1__\n```', 'break'),
            fb(f'統計 1 到 {a} 中偶數的個數。\n\n```python\ncount = 0\nfor i in range(1, {a + 1}):\n    if i __1__ 2 == 0:\n        count += 1\nprint(count)\n```', '%'),
            fb(f'用兩層迴圈輸出 {b} 列、每列 {b} 個 #（同列不換行）。\n\n```python\nfor i in range({b}):\n    for j in range({b}):\n        print("#", end=__1__)\n    print()\n```', ['""', "''"]),
            fb(f'輸出 1 到 {a}，但略過 {b}。\n\n```python\nfor i in range(1, {a + 1}):\n    if i == {b}:\n        __1__\n    print(i)\n```', 'continue'),
        ]
        return tasks[mode]

    if unit == 4:
        values = [a, b, a + b, a - b]
        tasks = [
            fb(f'建立串列 {values} 並輸出第一個元素。\n\n```python\nvalues = {values}\nprint(values[__1__])\n```', '0'),
            fb(f'建立串列 {values}，由小到大排序後輸出。\n\n```python\nvalues = {values}\nvalues.__1__()\nprint(values)\n```', 'sort'),
            fb(f'建立串列 {values}，加入 {index} 後輸出。\n\n```python\nvalues = {values}\nvalues.__1__({index})\nprint(values)\n```', 'append'),
            fb(f'輸出字串 "Unit{index}" 的反轉結果。\n\n```python\ntext = "Unit{index}"\nprint(text[::__1__])\n```', '-1'),
            fb(f'將字串 "A,B,{index}" 依逗號拆開並輸出。\n\n```python\ntext = "A,B,{index}"\nprint(text.__1__(","))\n```', 'split'),
            fb(f'建立元組 ({a}, {b})，解包後輸出兩值。\n\n```python\nx, __1__ = ({a}, {b})\nprint(x, y)\n```', 'y'),
        ]
        return tasks[mode]

    if unit == 5:
        tasks = [
            fb(f'輸出 range({a}) 中所有偶數組成的串列。\n\n```python\nprint([n for n in range({a}) __1__ n % 2 == 0])\n```', 'if'),
            fb(f'將 ["A","B","{index}"] 以斜線連接後輸出。\n\n```python\nitems = ["A", "B", "{index}"]\nprint("/".__1__(items))\n```', 'join'),
            fb(f'輸出 "banana{index}" 中 a 的數量。\n\n```python\ntext = "banana{index}"\nprint(text.__1__("a"))\n```', 'count'),
            fb(f'建立 [{a}, {b}, {a}]，去重後輸出元素數量。\n\n```python\nvalues = [{a}, {b}, {a}]\nprint(len(__1__(values)))\n```', 'set'),
            fb(f'複製 [{a}, {b}]，在副本加入 {index} 後輸出。\n\n```python\noriginal = [{a}, {b}]\ncopied = original.__1__()\ncopied.append({index})\nprint(copied)\n```', 'copy'),
            fb(f'使用 enumerate 從 {b} 開始輸出 ["A","B"] 的索引與值。\n\n```python\nfor i, value in enumerate(["A", "B"], start=__1__):\n    print(i, value)\n```', str(b)),
        ]
        return tasks[mode]

    if unit == 6:
        tasks = [
            fb(f'定義 add_{index}(x) 回傳 x+{b}。\n\n```python\ndef add_{index}(x):\n    return x __1__ {b}\n```', '+'),
            fb(f'定義 multiply_{index}(x) 回傳 x*{b}。\n\n```python\ndef multiply_{index}(x):\n    return x __1__ {b}\n```', '*'),
            fb(f'定義 is_multiple_{index}(n) 回傳 n 是否可被 {b} 整除。\n\n```python\ndef is_multiple_{index}(n):\n    return n % {b} __1__ 0\n```', '=='),
            fb(f'定義 total_{index}(numbers) 回傳串列總和。\n\n```python\ndef total_{index}(numbers):\n    return __1__(numbers)\n```', 'sum'),
            fb(f'定義 first_{index}(items) 回傳第一個元素。\n\n```python\ndef first_{index}(items):\n    return items[__1__]\n```', '0'),
            fb(f'定義 power_{index}(x, exponent={b}) 回傳次方。\n\n```python\ndef power_{index}(x, exponent={b}):\n    return x __1__ exponent\n```', '**'),
        ]
        return tasks[mode]

    tasks = [
        fb(f'使用遞迴定義 sum_to_{index}(n)，回傳 1 到 n 總和。\n\n```python\ndef sum_to_{index}(n):\n    if n <= 1:\n        return n\n    return n + sum_to_{index}(n __1__ 1)\n```', '-'),
        fb(f'建立字典 {{{{"A": {a}, "B": {b}}}}} 並輸出 A 的值。\n\n```python\ndata = {{"A": {a}, "B": {b}}}\nprint(data[__1__])\n```', ['"A"', "'A'"]),
        fb(f'建立空字典並以 get 取得不存在的 x，預設 {b}。\n\n```python\ndata = {{}}\nprint(data.__1__("x", {b}))\n```', 'get'),
        fb(f'輸出集合 {{{{{a}, {b}}}}} 與 {{{{{b}, {index}}}}} 的交集。\n\n```python\na = {{{a}, {b}}}\nb = {{{b}, {index}}}\nprint(a __1__ b)\n```', '&'),
        fb(f'統計 ["A","B","A","U{index}"] 的詞頻並輸出字典。\n\n```python\nwords = ["A", "B", "A", "U{index}"]\ncounts = {{}}\nfor word in words:\n    counts[word] = counts.__1__(word, 0) + 1\nprint(counts)\n```', 'get'),
        fb(f'使用遞迴定義 countdown_{index}(n)，從 n 輸出到 1。\n\n```python\ndef countdown_{index}(n):\n    if n <= 0:\n        __1__\n    print(n)\n    countdown_{index}(n - 1)\n```', 'return'),
    ]
    return tasks[mode]


def _unit1_concept_question(index):
    """Level 1: knowledge and meaning only; no execution tracing."""
    variant = index // 15
    contexts = ('成績登錄', '購物結帳', '溫度換算', '座位預約', '健康紀錄', '活動報名', '圖書借閱')
    templates = [
        ('input_type', 'input() 讀入的資料預設是哪一種型態？', 'str', ('int', 'float', 'bool'), 'io'),
        ('valid_name', f'下列哪一個是合法的 Python 變數名稱？（版本 {variant + 1}）', f'score_{variant}', (f'{variant}score', 'student-score', 'class'), 'variable'),
        ('assignment', '指定運算子 = 的用途是什麼？', '把右側的值交給左側名稱', ('比較兩值是否相等', '輸出資料', '標示註解'), 'variable'),
        ('type_int', 'int() 最主要的用途是什麼？', '將可轉換的資料轉成整數', ('永遠捨去小數', '把資料輸出', '檢查變數名稱'), 'type'),
        ('type_float', '哪個型態適合表示含小數點的測量值？', 'float', ('int', 'str', 'bool'), 'type'),
        ('print_purpose', 'print() 在程式中的主要用途是什麼？', '將資訊顯示在畫面上', ('接收鍵盤輸入', '建立迴圈', '定義函式'), 'io'),
        ('fstring', 'f-string 中的大括號 { } 用來做什麼？', '插入運算式或變數的值', ('建立集合', '開始註解', '表示縮排'), 'format'),
        ('comment', 'Python 單行註解以哪個符號開始？', '#', ('//', '<!--', '**'), 'syntax'),
        ('division', '運算子 / 與 // 的主要差異是什麼？', '/ 是一般除法，// 是整除', ('兩者完全相同', '/ 是餘數', '// 是次方'), 'operator'),
        ('modulo', '餘數運算子 % 常用來判斷什麼？', '整除或奇偶', ('文字長度', '變數型態', '輸入次數'), 'operator'),
        ('power', 'Python 的次方運算子是哪一個？', '**', ('^', '%%', '//'), 'operator'),
        ('conversion_need', '為什麼用 input() 取得年齡後，通常要先用 int() 轉換？', 'input() 回傳文字，文字不能直接做數值加法', ('input() 回傳浮點數', 'int() 會輸出結果', '年齡必須是變數名稱'), 'type'),
        ('error_type', '把無法轉成數字的文字交給 int()，最可能發生什麼？', '產生 ValueError', ('自動變成 0', '變成 None', '忽略該文字'), 'error'),
        ('precedence', '不確定算術運算順序時，最清楚的寫法是什麼？', '使用括號標明順序', ('刪除運算子', '改用 input()', '加上逗號'), 'operator'),
        ('program_purpose', '一段程式依序讀入單價與數量、相乘後輸出；它的目的是什麼？', '計算總價', ('比較兩個字串', '重複輸入', '判斷奇偶'), 'program_reading'),
    ]
    pattern, prompt, answer, distractors, concept = templates[index % len(templates)]
    prompt = f'在「{contexts[variant]}」程式的設計討論中，{prompt}'
    return mc(prompt, answer, *distractors, concept=concept, pattern=f'u1-{pattern}')


def _unit1_logic_question(index):
    """Level 2: every item requires tracing a short program."""
    v = index // 15 + 2
    templates = [
        ('assign_update', f'x = {v}\nx = x + 3\nprint(x)', str(v + 3), 'variable'),
        ('swap', f'a = {v}\nb = {v + 1}\na, b = b, a\nprint(a, b)', f'{v + 1} {v}', 'variable'),
        ('int_input_model', f'text = "{v}"\nn = int(text)\nprint(n + 1)', str(v + 1), 'type'),
        ('floor_division', f'n = {v * 5 + 2}\nprint(n // 5)\nprint(n % 5)', f'{v}\n2', 'operator'),
        ('precedence', f'x = {v} + 2 * 3\nprint(x)', str(v + 6), 'operator'),
        ('parentheses', f'x = ({v} + 2) * 3\nprint(x)', str((v + 2) * 3), 'operator'),
        ('string_concat', f'a = "{v}"\nb = "3"\nprint(a + b)', f'{v}3', 'type'),
        ('fstring_trace', f'name = "Amy"\nscore = {80 + v}\nprint(f"{{name}}:{{score}}")', f'Amy:{80 + v}', 'format'),
        ('overwrite', f'x = {v}\ny = x\nx = {v + 4}\nprint(y)', str(v), 'variable'),
        ('augmented', f'total = {v}\ntotal += 4\ntotal *= 2\nprint(total)', str((v + 4) * 2), 'variable'),
        ('float_result', f'x = {v}\ny = 2\nprint(x / y)', str(v / 2), 'operator'),
        ('bool_value', f'age = {10 + v}\nis_student = True\nprint(age, is_student)', f'{10 + v} True', 'type'),
        ('multi_print', f'a = {v}\nb = a + 1\nprint(a)\nprint(b)', f'{v}\n{v + 1}', 'io'),
        ('expression_chain', f'a = {v}\nb = a * 2\nc = b - 1\nprint(c)', str(v * 2 - 1), 'operator'),
        ('conversion_flow', f'raw = "{v}.5"\nvalue = float(raw)\nprint(value + 1)', str(v + 1.5), 'type'),
    ]
    pattern, code, answer, concept = templates[index % len(templates)]
    return short(f'請追蹤下列程式，寫出完整輸出：\n\n```python\n{code}\n```', answer,
                 concept=concept, pattern=f'u1-{pattern}')


# Unit 1 is the reviewed specification sample: same objectives, distinct cognition.
QUIZ_QUESTIONS[0] = [_unit1_concept_question(i) for i in range(100)]
SHORT_ANSWER_QUESTIONS[0] = [_unit1_logic_question(i) for i in range(100)]


for unit_index in range(8):
    generated_index = 0
    while len(QUIZ_QUESTIONS[unit_index]) < 100:
        prompt, answer, distractors = _generated_fact(unit_index, generated_index)
        generated_index += 1
        existing_mc = {question['content'] for question in QUIZ_QUESTIONS[unit_index]}
        existing_short = {question['content'] for question in SHORT_ANSWER_QUESTIONS[unit_index]}
        if prompt in existing_mc or prompt in existing_short:
            continue
        QUIZ_QUESTIONS[unit_index].append(mc(prompt, answer, *distractors))
        SHORT_ANSWER_QUESTIONS[unit_index].append(short(prompt, answer))

    generated_index = 0
    while len(FILL_BLANK_QUESTIONS[unit_index]) < 100:
        fill_question = _generated_fill(unit_index, generated_index)
        generated_index += 1
        existing_fill = {question['content'] for question in FILL_BLANK_QUESTIONS[unit_index]}
        if fill_question['content'] in existing_fill:
            continue
        FILL_BLANK_QUESTIONS[unit_index].append(fill_question)
