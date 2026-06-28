"""Assessment banks aligned with the four-day, eight-unit curriculum."""


def mc(content, correct, *distractors):
    choices = [(correct, True), *[(item, False) for item in distractors]]
    return {'content': content, 'choices': choices, 'explanation': f'正確答案：{correct}'}


def short(content, answer, explanation=''):
    return {'content': content, 'correct_answer': answer, 'explanation': explanation or f'答案：{answer}'}


def code(content, answer, explanation='', *alternatives):
    accepted = '\n---OR---\n'.join((answer, *alternatives))
    return {'content': content, 'correct_answer': accepted, 'explanation': explanation or answer}


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


CODING_QUESTIONS = [
    [
        code('讀入名字並輸出「Hello, 名字」。', 'name=input()\nprint(f"Hello, {name}")'),
        code('讀入兩個整數並輸出總和。', 'a=int(input())\nb=int(input())\nprint(a+b)'),
        code('讀入圓半徑並輸出面積，圓周率使用 3.14。', 'r=float(input())\nprint(3.14*r**2)'),
        code('讀入秒數，輸出整數分鐘與剩餘秒數。', 's=int(input())\nprint(s//60,s%60)'),
    ],
    [
        code('讀入整數，輸出「偶數」或「奇數」。', 'n=int(input())\nif n%2==0:\n    print("偶數")\nelse:\n    print("奇數")'),
        code('讀入成績，60 分以上輸出「及格」，否則輸出「不及格」。', 'score=int(input())\nif score>=60:\n    print("及格")\nelse:\n    print("不及格")'),
        code('讀入整數，輸出「正數」、「負數」或「零」。', 'n=int(input())\nif n>0:\n    print("正數")\nelif n<0:\n    print("負數")\nelse:\n    print("零")'),
        code('讀入年份，輸出是否為閏年的布林值。', 'year=int(input())\nprint(year%400==0 or (year%4==0 and year%100!=0))'),
    ],
    [
        code('使用 for 輸出 1 到 5，每個數字一行。', 'for i in range(1,6):\n    print(i)'),
        code('輸出 1 到 100 的總和。', 'total=0\nfor i in range(1,101):\n    total+=i\nprint(total)', '', 'print(sum(range(1,101)))'),
        code('使用 while 輸出 1 到 5。', 'i=1\nwhile i<=5:\n    print(i)\n    i+=1'),
        code('輸入 n，輸出 1 到 n 的所有偶數。', 'n=int(input())\nfor i in range(2,n+1,2):\n    print(i)'),
    ],
    [
        code('輸出 1 到 5 的階乘結果。', 'result=1\nfor i in range(1,6):\n    result*=i\nprint(result)'),
        code('印出五列星號三角形。', 'for i in range(1,6):\n    print("*"*i)'),
        code('找出 [4,7,2,9,1] 最大值，不使用 max。', 'nums=[4,7,2,9,1]\nlargest=nums[0]\nfor n in nums:\n    if n>largest:\n        largest=n\nprint(largest)'),
        code('輸出 1 到 10，但略過 5。', 'for i in range(1,11):\n    if i==5:\n        continue\n    print(i)'),
    ],
    [
        code('建立 [10,5,8,3]，由小到大排序後輸出。', 'nums=[10,5,8,3]\nnums.sort()\nprint(nums)'),
        code('輸出字串 Python 的反轉結果。', 'text="Python"\nprint(text[::-1])'),
        code('將 "Amy,Bob,Cindy" 依逗號拆開並輸出串列。', 'text="Amy,Bob,Cindy"\nprint(text.split(","))'),
        code('建立串列 [1,2,3]，加入 4 後輸出。', 'nums=[1,2,3]\nnums.append(4)\nprint(nums)'),
    ],
    [
        code('讀入文字，忽略空格與大小寫後判斷是否回文。', 'text=input().replace(" ","").lower()\nprint(text==text[::-1])'),
        code('輸出 [88,45,72,95,60] 中所有及格成績。', 'scores=[88,45,72,95,60]\nprint([s for s in scores if s>=60])'),
        code('輸出 [3,1,4,1,5] 的平均值。', 'nums=[3,1,4,1,5]\nprint(sum(nums)/len(nums))'),
        code('將名字串列以「 / 」連接後輸出。', 'names=["Amy","Bob","Cindy"]\nprint(" / ".join(names))'),
    ],
    [
        code('定義 add(a,b) 並輸出 add(2,3)。', 'def add(a,b):\n    return a+b\nprint(add(2,3))'),
        code('定義 is_even(n)，回傳是否為偶數。', 'def is_even(n):\n    return n%2==0'),
        code('定義 area(w,h) 回傳長方形面積。', 'def area(w,h):\n    return w*h'),
        code('定義 average(numbers) 回傳平均值。', 'def average(numbers):\n    return sum(numbers)/len(numbers)'),
    ],
    [
        code('用遞迴定義 factorial(n)。', 'def factorial(n):\n    if n<=1:\n        return 1\n    return n*factorial(n-1)'),
        code('建立 Amy=88、Bob=72 的字典並輸出 Amy 的分數。', 'scores={"Amy":88,"Bob":72}\nprint(scores["Amy"])'),
        code('統計單字串列中每個單字的次數並輸出字典。', 'words=["a","b","a"]\ncounts={}\nfor word in words:\n    counts[word]=counts.get(word,0)+1\nprint(counts)'),
        code('輸出集合 {1,2,3} 與 {2,3,4} 的交集。', 'a={1,2,3}\nb={2,3,4}\nprint(a&b)'),
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


CODING_EXTRA = [
    [
        code('輸出文字 Hello Python。', 'print("Hello Python")', '', "print('Hello Python')"),
        code('建立變數 x=10、y=3，輸出 x 乘 y。', 'x=10\ny=3\nprint(x*y)'),
        code('讀入整數並輸出它的平方。', 'n=int(input())\nprint(n**2)'),
        code('讀入攝氏溫度並輸出華氏溫度。', 'c=float(input())\nprint(c*9/5+32)'),
        code('輸出 10 除以 3 的商與餘數。', 'print(10//3,10%3)'),
        code('建立 name="Amy" 並用 f-string 輸出 Hello Amy。', 'name="Amy"\nprint(f"Hello {name}")'),
    ],
    [
        code('讀入整數，若大於 10 就輸出「大」。', 'n=int(input())\nif n>10:\n    print("大")'),
        code('讀入兩數並輸出較大者。', 'a=int(input())\nb=int(input())\nif a>b:\n    print(a)\nelse:\n    print(b)'),
        code('讀入年齡，13 到 17 輸出「青少年」。', 'age=int(input())\nif 13<=age<=17:\n    print("青少年")'),
        code('讀入月份，1 到 12 以外輸出「錯誤」。', 'month=int(input())\nif month<1 or month>12:\n    print("錯誤")'),
        code('讀入兩個布林值 a、b，輸出兩者是否同時為真。', 'a=bool(int(input()))\nb=bool(int(input()))\nprint(a and b)'),
        code('讀入分數，依序輸出 A、B 或 C（90、80 為界）。', 'score=int(input())\nif score>=90:\n    print("A")\nelif score>=80:\n    print("B")\nelse:\n    print("C")'),
    ],
    [
        code('輸出 0 到 4。', 'for i in range(5):\n    print(i)'),
        code('輸出 2 到 10 的偶數。', 'for i in range(2,11,2):\n    print(i)'),
        code('使用 while 從 5 倒數到 1。', 'i=5\nwhile i>=1:\n    print(i)\n    i-=1'),
        code('輸入 n，輸出 1 到 n 的總和。', 'n=int(input())\ntotal=0\nfor i in range(1,n+1):\n    total+=i\nprint(total)'),
        code('輸出字串 Python 的每個字元。', 'for ch in "Python":\n    print(ch)'),
        code('計算 [2,4,6,8] 的總和並輸出。', 'total=0\nfor n in [2,4,6,8]:\n    total+=n\nprint(total)'),
    ],
    [
        code('輸出 1 到 20 第一個可被 7 整除的數。', 'for i in range(1,21):\n    if i%7==0:\n        print(i)\n        break'),
        code('輸出 1 到 10 中不可被 3 整除的數。', 'for i in range(1,11):\n    if i%3==0:\n        continue\n    print(i)'),
        code('用巢狀迴圈輸出 2×2 個星號。', 'for i in range(2):\n    for j in range(2):\n        print("*",end="")\n    print()'),
        code('計算 [3,7,2,9] 中大於 5 的個數。', 'count=0\nfor n in [3,7,2,9]:\n    if n>5:\n        count+=1\nprint(count)'),
        code('輸出 3 的 1 到 5 倍。', 'for i in range(1,6):\n    print(3*i)'),
        code('找出 [8,3,12,5] 最小值，不使用 min。', 'nums=[8,3,12,5]\nsmallest=nums[0]\nfor n in nums:\n    if n<smallest:\n        smallest=n\nprint(smallest)'),
    ],
    [
        code('輸出 [1,2,3,4] 的前兩個元素。', 'nums=[1,2,3,4]\nprint(nums[:2])'),
        code('將 [3,1,2] 反向排序後輸出。', 'nums=[3,1,2]\nnums.sort(reverse=True)\nprint(nums)'),
        code('移除字串兩端空白並輸出。', 'text="  Python  "\nprint(text.strip())'),
        code('輸出 "banana" 中字母 a 的數量。', 'text="banana"\nprint(text.count("a"))'),
        code('將 (10,20) 解包成 x、y 並輸出。', 'x,y=(10,20)\nprint(x,y)'),
        code('合併 [1,2] 與 [3,4] 後輸出。', 'a=[1,2]\nb=[3,4]\nprint(a+b)'),
    ],
    [
        code('讀入空格分隔整數並輸出串列。', 'nums=[int(x) for x in input().split()]\nprint(nums)'),
        code('輸出 [1,2,3,4,5] 中的奇數串列。', 'nums=[1,2,3,4,5]\nprint([n for n in nums if n%2==1])'),
        code('將 ["a","b","c"] 連成 a-b-c。', 'items=["a","b","c"]\nprint("-".join(items))'),
        code('輸出 "Python" 是否以 Py 開頭。', 'print("Python".startswith("Py"))'),
        code('複製 [1,2,3]，在副本加入 4 並輸出副本。', 'original=[1,2,3]\ncopied=original.copy()\ncopied.append(4)\nprint(copied)'),
        code('使用 enumerate 輸出 ["A","B"] 的索引與內容。', 'for i,value in enumerate(["A","B"]):\n    print(i,value)'),
    ],
    [
        code('定義 square(n) 回傳平方。', 'def square(n):\n    return n**2'),
        code('定義 greet(name="Guest") 回傳 Hello 加名字。', 'def greet(name="Guest"):\n    return f"Hello {name}"'),
        code('定義 maximum(a,b) 回傳較大值。', 'def maximum(a,b):\n    if a>b:\n        return a\n    return b'),
        code('定義 count_even(numbers) 回傳偶數個數。', 'def count_even(numbers):\n    return sum(1 for n in numbers if n%2==0)'),
        code('定義 first_last(items) 回傳第一與最後元素。', 'def first_last(items):\n    return items[0],items[-1]'),
        code('定義 total(*numbers) 回傳所有參數總和。', 'def total(*numbers):\n    return sum(numbers)'),
    ],
    [
        code('用遞迴定義從 1 加到 n 的函式。', 'def total(n):\n    if n<=1:\n        return n\n    return n+total(n-1)'),
        code('建立空字典，加入鍵 name、值 Amy 並輸出。', 'data={}\ndata["name"]="Amy"\nprint(data)'),
        code('遍歷 {"A":1,"B":2} 並輸出鍵和值。', 'data={"A":1,"B":2}\nfor key,value in data.items():\n    print(key,value)'),
        code('輸出字典中 x 的值，沒有時輸出 0。', 'data={}\nprint(data.get("x",0))'),
        code('輸出 {1,2,3} 與 {3,4} 的聯集。', 'a={1,2,3}\nb={3,4}\nprint(a|b)'),
        code('將 [1,1,2,3,3] 去重後輸出集合。', 'nums=[1,1,2,3,3]\nprint(set(nums))'),
    ],
]


for unit_index, facts in enumerate(EXTRA_FACTS):
    for prompt, answer, distractors in facts:
        QUIZ_QUESTIONS[unit_index].append(mc(prompt, answer, *distractors))
        SHORT_ANSWER_QUESTIONS[unit_index].append(short(prompt, answer))
    CODING_QUESTIONS[unit_index].extend(CODING_EXTRA[unit_index])
