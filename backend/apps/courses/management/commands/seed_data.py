"""
python manage.py seed_data

讀取 教材/ 資料夾的 MD 教材，建立課程、單元、評量資料。
執行前請確認 DB 已 migrate，且 MATERIALS_DIR 路徑正確。
"""
import re
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.courses.models import Course, Lesson, Enrollment
from apps.assessments.models import Quiz, Question, Choice

User = get_user_model()

# 教材路徑（相對於 manage.py 所在的 backend/ 目錄的上一層）
MATERIALS_DIR = Path(__file__).resolve().parents[5] / '教材'

UNIT_TITLES = [
    'print 輸出',
    'input 輸入與運算',
    'if 條件判斷',
    '多條件 if',
    'list 串列',
    'range 數列',
    'for 迴圈',
    '迴圈應用',
]

COURSES = [
    {
        'title': 'Python 程式設計 — Level 1 補救版',
        'description': '適合對程式執行流程感到困惑、概念尚未建立的同學。非常詳細說明＋流程圖＋完整程式碼＋逐行中文注解，認知負荷低，逐步引導。',
        'difficulty': 'beginner',
        'md_file': 'Python教材_Level1_補救版.md',
    },
    {
        'title': 'Python 程式設計 — Level 2 標準版',
        'description': '適合理解基礎概念、需要熟練語法與實際應用的同學。說明與練習並重，部分程式需自行補全。',
        'difficulty': 'intermediate',
        'md_file': 'Python教材_Level2_標準版.md',
    },
    {
        'title': 'Python 程式設計 — Level 3 進階版',
        'description': '適合語法熟練、準備提升問題解決與設計思維的同學。精簡說明，幾乎由學生獨立設計與撰寫。',
        'difficulty': 'advanced',
        'md_file': 'Python教材_Level3_進階版.md',
    },
]

# ── Level 1 選擇題（10 題 / 單元，純基礎概念確認）───────────────────────
QUIZ_QUESTIONS = [
    # ── Unit 1: print 輸出 ──────────────────────────────────────────
    [
        {'content': '下面這段程式執行後，螢幕會顯示什麼？\n\n```python\nprint("蘋果")\nprint(3 + 5)\n```',
         'explanation': '每個 print() 執行完都會換行，所以兩行輸出分別在不同行。',
         'choices': [('蘋果 8', False), ('蘋果（換行）8', True), ('錯誤，不能這樣寫', False), ('38', False)]},
        {'content': '下面哪一行程式會發生錯誤？\n\n```python\nprint("Hello")\nprint(50 + 30)\nprint(Python)\n```',
         'explanation': '第三行 Python 沒加引號，直譯器會把它當成變數名稱，引發 NameError。',
         'choices': [('第一行', False), ('第二行', False), ('第三行', True), ('全部都對', False)]},
        {'content': 'print("Hello") 的引號可以換成單引號嗎？\n\nprint(\'Hello\')',
         'explanation': 'Python 允許使用單引號或雙引號包住字串，兩種都正確。',
         'choices': [('不行，只能用雙引號', False), ('可以，單雙引號都可以', True), ('只有數字可以用單引號', False), ('會報錯', False)]},
        {'content': 'print(3 + 5) 的輸出是什麼？',
         'explanation': 'print() 可以直接顯示計算結果，3 + 5 = 8。',
         'choices': [('3 + 5', False), ('35', False), ('8', True), ('發生錯誤', False)]},
        {'content': 'print() 函式括號內沒有任何引數，執行結果是什麼？',
         'explanation': 'print() 不帶任何引數時，輸出一個空行（只有換行符）。',
         'choices': [('發生錯誤', False), ('輸出一個空行', True), ('輸出 None', False), ('什麼都不做', False)]},
        {'content': '下列哪一個 print 的寫法會出現 SyntaxError？',
         'explanation': 'Python 3 的 print 是函式，必須有括號；print "Hello" 是 Python 2 的寫法。',
         'choices': [('print("Hello")', False), ('print(100)', False), ('print "Hello"', True), ('print(3+5)', False)]},
        {'content': 'print("結果是", 5 * 3) 的輸出是？',
         'explanation': '逗號分隔的多個參數，print 會在中間自動加一個空格。',
         'choices': [('結果是5*3', False), ('結果是15', False), ('結果是 15', True), ('結果是，15', False)]},
        {'content': '下面哪行程式有錯？\n\nA. print("你好")\nB. print(你好)\nC. print(100)\nD. print("100")',
         'explanation': 'B 的「你好」沒有引號，會被當成變數名稱，找不到會報 NameError。',
         'choices': [('A', False), ('B', True), ('C', False), ('D', False)]},
        {'content': '執行 print("A") 後，再執行 print("B")，結果是什麼？',
         'explanation': '兩個獨立的 print()，每個執行後都換行，所以各自印在不同行。',
         'choices': [('AB（同一行）', False), ('A 換行 B（兩行）', True), ('發生錯誤', False), ('只印 A', False)]},
        {'content': 'print(10, 20) 的輸出是？',
         'explanation': 'print 有多個引數時，預設用空格分隔，輸出 10 20。',
         'choices': [('1020', False), ('10, 20', False), ('10 20', True), ('發生錯誤', False)]},
        {'content': '以下哪個說法正確？',
         'explanation': 'print() 是 Python 3 的內建函式，必須寫括號；Python 3 不支援 Python 2 的 print 陳述句。',
         'choices': [('print 在 Python 3 不需要括號', False), ('print() 是 Python 3 的函式，必須加括號', True),
                     ('print 只能輸出文字，不能輸出數字', False), ('一個 print 只能輸出一個值', False)]},
    ],
    # ── Unit 2: input 輸入與運算 ─────────────────────────────────────
    [
        {'content': '執行下面程式，輸入 5 後，會發生什麼事？\n\n```python\nx = input("輸入數字：")\nprint(x + 10)\n```',
         'explanation': 'input() 回傳字串，字串不能和整數直接相加，會引發 TypeError。',
         'choices': [('顯示 15', False), ('顯示 510', False), ('發生 TypeError 錯誤', True), ('顯示 5 10', False)]},
        {'content': 'input() 函式的回傳值型別是什麼？',
         'explanation': '不論使用者輸入什麼，input() 一律回傳字串（str）型別。',
         'choices': [('int', False), ('float', False), ('str', True), ('視輸入內容而定', False)]},
        {'content': '要讓使用者輸入的值可以做數學加法，應填入什麼？\n\n```python\na = ___(input("輸入整數："))\n```',
         'explanation': 'int() 將字串轉為整數，才能進行加減乘除運算。',
         'choices': [('str()', False), ('int()', True), ('print()', False), ('type()', False)]},
        {'content': '下面程式輸入「20」後，輸出是什麼？\n\n```python\nage = input("年齡：")\nprint("明年你", age + 1, "歲")\n```',
         'explanation': 'age 是字串 "20"，不能直接和整數 1 相加，會引發 TypeError。',
         'choices': [('明年你 21 歲', False), ('明年你 201 歲', False), ('發生 TypeError', True), ('明年你 20 歲', False)]},
        {'content': '修正上題錯誤，正確的寫法是哪個？',
         'explanation': '需要用 int() 把 input() 的結果轉成整數後再加 1。',
         'choices': [('age = input(); print(age + 1)', False),
                     ('age = int(input("年齡：")); print("明年你", age + 1, "歲")', True),
                     ('age = float(input("年齡：")); print(age + 1)', False),
                     ('age = str(input("年齡：")); print(age + 1)', False)]},
        {'content': '想把輸入的小數存進 price，應該用哪個函式？',
         'explanation': 'float() 可以將字串轉為含小數的浮點數，int() 只能轉整數。',
         'choices': [('int(input())', False), ('float(input())', True), ('str(input())', False), ('num(input())', False)]},
        {'content': '下面程式輸入「hello」後會發生什麼？\n\n```python\nx = int(input("輸入數字："))\nprint(x)\n```',
         'explanation': 'int() 無法將非數字字串轉換，輸入 "hello" 會引發 ValueError。',
         'choices': [('顯示 hello', False), ('顯示 0', False), ('引發 ValueError', True), ('程式跳過', False)]},
        {'content': 'input("請輸入：") 括號內的字串有什麼作用？',
         'explanation': '括號內的字串是提示文字（prompt），會顯示在輸入框前，告訴使用者要輸入什麼。',
         'choices': [('設定輸入的預設值', False), ('顯示提示文字', True), ('限制輸入長度', False), ('設定輸入型別', False)]},
        {'content': '以下程式的輸出是什麼？（假設輸入 "3"）\n\n```python\nx = input()\nprint(x * 2)\n```',
         'explanation': 'x 是字串 "3"，字串乘以整數 2 表示重複兩次，輸出 "33"。',
         'choices': [('6', False), ('33', True), ('發生錯誤', False), ('3 3', False)]},
        {'content': '圓面積公式是 π × r²，下面哪行可以正確計算（r 已用 float 取得）？',
         'explanation': 'Python 用 ** 表示次方，3.14159 * r**2 是正確寫法。',
         'choices': [('area = 3.14159 x r x r', False), ('area = 3.14159 * r**2', True),
                     ('area = 3.14159 ^ r ^ 2', False), ('area = pi * r * r', False)]},
    ],
    # ── Unit 3: if 條件判斷 ──────────────────────────────────────────
    [
        {'content': '輸入 7 後，程式會輸出什麼？\n\n```python\nx = int(input("輸入數字："))\nif x > 10:\n    print("大於十")\nelse:\n    print("不大於十")\n```',
         'explanation': '7 不大於 10，條件為 False，執行 else 區塊。',
         'choices': [('大於十', False), ('不大於十', True), ('兩行都印', False), ('什麼都不印', False)]},
        {'content': 'Python 的 if 語法中，條件後面必須加上什麼符號？',
         'explanation': 'Python 規定 if 行尾要加冒號 :，缺少會出現 SyntaxError。',
         'choices': [('分號 ;', False), ('冒號 :', True), ('逗號 ,', False), ('括號 ()', False)]},
        {'content': '下面 if 區塊有沒有問題？\n\n```python\nif True:\nprint("Hello")\n```',
         'explanation': 'if 區塊內的程式碼必須縮排，否則引發 IndentationError。',
         'choices': [('可以，正常印出 Hello', False), ('不行，缺少縮排', True), ('不行，True 不是合法條件', False), ('可以，但輸出是空的', False)]},
        {'content': '哪一個運算子代表「等於」的比較？',
         'explanation': '= 是賦值運算子，== 才是比較兩個值是否相等。',
         'choices': [('=', False), ('==', True), ('!=', False), ('=>', False)]},
        {'content': '以下程式輸出什麼？\n\n```python\nx = 5\nif x % 2 == 0:\n    print("偶數")\nelse:\n    print("奇數")\n```',
         'explanation': '5 % 2 = 1，不等於 0，條件 False，執行 else 印出「奇數」。',
         'choices': [('偶數', False), ('奇數', True), ('0', False), ('什麼都不印', False)]},
        {'content': '執行下面程式，x = 15 時輸出什麼？\n\n```python\nif x > 10:\n    print("大")\nprint("完成")\n```',
         'explanation': '"大" 在 if 區塊內（只有條件成立才印），"完成" 在 if 外（一定會印）。',
         'choices': [('大', False), ('完成', False), ('大（換行）完成', True), ('什麼都不印', False)]},
        {'content': 'score = 60，if score >= 60: 的條件是 True 還是 False？',
         'explanation': '>= 是大於等於，60 >= 60 成立，結果為 True。',
         'choices': [('True', True), ('False', False), ('視情況而定', False), ('發生錯誤', False)]},
        {'content': '執行下面程式，輸入 Y 後輸出什麼？\n\n```python\nans = input("繼續嗎？")\nif ans == "Y":\n    print("繼續")\nelse:\n    print("結束")\n```',
         'explanation': '輸入 "Y" 後，ans == "Y" 成立，執行 if 區塊印出「繼續」。',
         'choices': [('繼續', True), ('結束', False), ('Y', False), ('發生錯誤', False)]},
        {'content': '下面程式有錯誤，錯誤是什麼？\n\n```python\nscore = 80\nif score = 80:\n    print("及格")\n```',
         'explanation': 'if 條件應該用 ==（比較），不能用 =（賦值），= 在這裡會引發 SyntaxError。',
         'choices': [('score 沒有宣告型別', False), ('應該用 == 不是 =', True), ('缺少 else', False), ('print 格式錯誤', False)]},
        {'content': '以下程式，x = 3 時輸出什麼？\n\n```python\nx = 3\nif x > 5:\n    print("A")\nif x > 1:\n    print("B")\n```',
         'explanation': '兩個獨立的 if，各自判斷。x=3：第一個 if（3>5）為 False 不印；第二個 if（3>1）為 True 印 B。',
         'choices': [('A', False), ('B', True), ('A 和 B 都印', False), ('什麼都不印', False)]},
    ],
    # ── Unit 4: 多條件 if ────────────────────────────────────────────
    [
        {'content': '輸入 72，程式會印出什麼？\n\n```python\nscore = 72\nif score >= 90:\n    print("A")\nelif score >= 80:\n    print("B")\nelif score >= 70:\n    print("C")\nelse:\n    print("F")\n```',
         'explanation': '72 不符合 >=90、>=80，但符合 >=70，程式只執行第一個符合的分支印 C。',
         'choices': [('A', False), ('B', False), ('C', True), ('F', False)]},
        {'content': 'if...elif...else 中，第一個 elif 條件成立時，後面的 elif 和 else 會執行嗎？',
         'explanation': '程式找到第一個符合的條件就執行，然後跳過整個 if-elif-else 結構。',
         'choices': [('都會執行', False), ('不會，只執行第一個符合的', True),
                     ('只有 else 會執行', False), ('取決於條件', False)]},
        {'content': 'elif 是哪兩個關鍵字的縮寫？',
         'explanation': 'elif 是 else if 的縮寫，用來串接多個條件分支。',
         'choices': [('else if', True), ('end if', False), ('else elif', False), ('extra if', False)]},
        {'content': 'else 區塊在什麼情況下執行？',
         'explanation': 'else 是「以上條件都不成立時」的最終分支，不需要條件判斷。',
         'choices': [('第一個條件成立時', False), ('所有 if/elif 條件都不成立時', True),
                     ('永遠都執行', False), ('只有 if 為 False 時', False)]},
        {'content': 'score = 45，以下程式輸出什麼？\n\n```python\nif score >= 90:\n    print("A")\nelif score >= 60:\n    print("B")\nelse:\n    print("F")\n```',
         'explanation': '45 不符合 >=90 也不符合 >=60，執行 else 印出 F。',
         'choices': [('A', False), ('B', False), ('F', True), ('什麼都不印', False)]},
        {'content': '以下程式，a=5, b=5 時執行哪個分支？\n\n```python\nif a > b:\n    print("a 大")\nelif a < b:\n    print("b 大")\nelse:\n    print("相等")\n```',
         'explanation': 'a == b，兩個 if/elif 都不成立，所以執行 else 印出「相等」。',
         'choices': [('a 大', False), ('b 大', False), ('相等', True), ('什麼都不印', False)]},
        {'content': '以下程式，score = 95 的輸出是什麼？（注意條件順序！）\n\n```python\nif score >= 60:\n    print("D")\nelif score >= 80:\n    print("B")\nelif score >= 90:\n    print("A")\n```',
         'explanation': '95 >= 60 成立，立刻印出 D，不再檢查後面的 elif，這是條件順序寫錯的典型問題。',
         'choices': [('A', False), ('B', False), ('D', True), ('什麼都不印', False)]},
        {'content': '一個 if 語法可以有幾個 elif？',
         'explanation': 'Python 的 elif 數量沒有限制，可以根據需求加入多個 elif 分支。',
         'choices': [('最多 1 個', False), ('最多 5 個', False), ('沒有限制', True), ('最多 10 個', False)]},
        {'content': 'BMI = 22.5，下列 BMI 判斷程式印出什麼？\n\n```python\nif bmi < 18.5:\n    print("過輕")\nelif bmi < 25:\n    print("正常")\nelif bmi < 30:\n    print("過重")\nelse:\n    print("肥胖")\n```',
         'explanation': '22.5 不小於 18.5，但小於 25，所以印出「正常」。',
         'choices': [('過輕', False), ('正常', True), ('過重', False), ('肥胖', False)]},
        {'content': '以下程式，month = 2 時輸出什麼？\n\n```python\nif month == 1:\n    print("一月")\nelif month == 2:\n    print("二月")\nelif month == 3:\n    print("三月")\nelse:\n    print("其他月份")\n```',
         'explanation': 'month == 2 符合第二個 elif，輸出「二月」。',
         'choices': [('一月', False), ('二月', True), ('三月', False), ('其他月份', False)]},
    ],
    # ── Unit 5: list 串列 ────────────────────────────────────────────
    [
        {'content': '執行後會印出什麼？\n\n```python\nnums = [10, 20, 30, 40]\nprint(nums[1])\n```',
         'explanation': '串列索引從 0 開始，nums[1] 是第二個元素 20。',
         'choices': [('10', False), ('20', True), ('30', False), ('發生 IndexError', False)]},
        {'content': 'fruits = ["蘋果", "香蕉", "西瓜"]，fruits[-1] 的值是？',
         'explanation': '負索引從末端開始，-1 代表最後一個元素「西瓜」。',
         'choices': [('蘋果', False), ('香蕉', False), ('西瓜', True), ('引發 IndexError', False)]},
        {'content': 'len([1, 2, 3, 4, 5]) 的回傳值是？',
         'explanation': 'len() 回傳串列的元素數量，共 5 個元素。',
         'choices': [('4', False), ('5', True), ('6', False), ('None', False)]},
        {'content': '執行 nums.append(99) 後，99 會加在哪裡？',
         'explanation': 'append() 把新元素加在串列**末尾**。',
         'choices': [('第一個位置', False), ('中間位置', False), ('最後一個位置', True), ('取決於 99 的大小', False)]},
        {'content': 'scores = [80, 92, 75]，sum(scores) 的結果是？',
         'explanation': 'sum() 計算所有元素的總和：80 + 92 + 75 = 247。',
         'choices': [('82.3', False), ('247', True), ('75', False), ('92', False)]},
        {'content': 'nums = [1, 2, 3]，執行 nums.append(4) 後，nums 的內容是？',
         'explanation': 'append(4) 在末尾加入 4。',
         'choices': [('[4, 1, 2, 3]', False), ('[1, 2, 3, 4]', True), ('[1, 2, 4, 3]', False), ('[1, 4, 2, 3]', False)]},
        {'content': '"Python" in ["Java", "Python", "C++"] 的結果是？',
         'explanation': 'in 運算子檢查元素是否在串列中，"Python" 確實在裡面，回傳 True。',
         'choices': [('True', True), ('False', False), ('1', False), ('引發錯誤', False)]},
        {'content': 'lst = [3, 1, 4, 1, 5]，執行 lst.sort() 後 lst 的內容是？',
         'explanation': 'sort() 原地由小到大排序串列。',
         'choices': [('[5, 4, 3, 1, 1]', False), ('[1, 1, 3, 4, 5]', True),
                     ('回傳新串列，原串列不變', False), ('[3, 1, 4, 1, 5]', False)]},
        {'content': 'nums = [10, 20, 30]，nums[0] = 99 後，nums 的內容是？',
         'explanation': '直接賦值給索引 0，修改第一個元素。',
         'choices': [('[99, 10, 20, 30]', False), ('[99, 20, 30]', True), ('[10, 20, 30, 99]', False), ('[10, 99, 30]', False)]},
        {'content': '以下哪個寫法可以建立一個空串列？',
         'explanation': '[] 和 list() 都可以建立空串列。',
         'choices': [('empty = {}', False), ('empty = ()', False), ('empty = []', True), ('empty = ""', False)]},
    ],
    # ── Unit 6: range 數列 ───────────────────────────────────────────
    [
        {'content': 'range(3, 8) 會產生哪些數字？',
         'explanation': 'range(start, stop) 從 start 到 stop-1，不含 stop 本身。',
         'choices': [('3,4,5,6,7,8', False), ('3,4,5,6,7', True), ('0,1,2,3,4,5,6,7', False), ('4,5,6,7', False)]},
        {'content': 'list(range(5)) 的結果是？',
         'explanation': 'range(5) 產生 0,1,2,3,4，用 list() 轉為串列。',
         'choices': [('[1,2,3,4,5]', False), ('[0,1,2,3,4]', True), ('[0,1,2,3,4,5]', False), ('range(0,5)', False)]},
        {'content': 'range(1, 10) 共產生幾個數字？',
         'explanation': '從 1 到 9（不含 10），共 9 個數字。',
         'choices': [('8', False), ('9', True), ('10', False), ('11', False)]},
        {'content': 'range(0, 10, 2) 的第一個和最後一個數字是？',
         'explanation': '從 0 開始，步長 2，到 9 之前停止：0, 2, 4, 6, 8。第一個 0，最後一個 8。',
         'choices': [('0 和 10', False), ('0 和 8', True), ('2 和 10', False), ('0 和 9', False)]},
        {'content': 'range(1, 6) 包含數字 6 嗎？',
         'explanation': 'range(start, stop) 不包含 stop（終止值），只到 5 為止。',
         'choices': [('包含', False), ('不包含', True), ('取決於 Python 版本', False), ('包含，但要用 list() 才看得到', False)]},
        {'content': 'sum(range(1, 6)) 的結果是？',
         'explanation': 'range(1,6) = 1,2,3,4,5，加總為 15。',
         'choices': [('6', False), ('10', False), ('15', True), ('21', False)]},
        {'content': 'range(5, 5) 會產生什麼？',
         'explanation': 'start == stop 時，range 產生空序列，沒有任何元素。',
         'choices': [('[5]', False), ('空序列（沒有元素）', True), ('[0,1,2,3,4,5]', False), ('引發錯誤', False)]},
        {'content': 'range() 回傳的物件是串列嗎？',
         'explanation': 'range() 回傳 range 物件，不是串列，需要 list() 轉換才會得到串列。',
         'choices': [('是，直接是 list', False), ('不是，是 range 物件', True),
                     ('是 tuple', False), ('是 generator', False)]},
        {'content': 'list(range(1, 8, 3)) 的結果是？',
         'explanation': '從 1 開始，步長 3，不超過 8：1, 4, 7。',
         'choices': [('[1, 4, 7, 10]', False), ('[1, 4, 7]', True), ('[1, 3, 6]', False), ('[3, 6]', False)]},
        {'content': '要產生 [5, 10, 15, 20, 25]，應用哪個 range？',
         'explanation': '從 5 開始，步長 5，到 25 包含，終止值要設 30（不含）。',
         'choices': [('range(5, 25)', False), ('range(5, 26, 5)', True), ('range(5, 25, 5)', False), ('range(0, 25, 5)', False)]},
    ],
    # ── Unit 7: for 迴圈 ────────────────────────────────────────────
    [
        {'content': '執行後會印出幾行？\n\n```python\nfor i in range(3):\n    print("Hello", i)\n```',
         'explanation': 'range(3) 產生 0,1,2 共 3 個數字，迴圈執行 3 次。',
         'choices': [('1 行', False), ('2 行', False), ('3 行', True), ('4 行', False)]},
        {'content': '下面程式印出的最終 total 是？\n\n```python\ntotal = 0\nfor i in range(1, 6):\n    total = total + i\nprint(total)\n```',
         'explanation': 'range(1,6) = 1,2,3,4,5，累加總和為 15。',
         'choices': [('14', False), ('15', True), ('10', False), ('20', False)]},
        {'content': '以下程式的輸出是什麼？\n\n```python\nfor n in [2, 4, 6]:\n    if n == 4:\n        break\n    print(n)\n```',
         'explanation': 'n=2 時印出 2；n=4 時遇到 break，立刻離開迴圈，不再印 4 和 6。',
         'choices': [('2、4、6 各一行', False), ('只印 2', True), ('只印 2 和 4', False), ('什麼都不印', False)]},
        {'content': '以下程式的輸出是什麼？\n\n```python\nfor n in range(1, 6):\n    if n % 2 == 0:\n        continue\n    print(n)\n```',
         'explanation': 'continue 跳過偶數，只印奇數：1, 3, 5。',
         'choices': [('1 2 3 4 5', False), ('2 4', False), ('1 3 5（各自一行）', True), ('0 2 4', False)]},
        {'content': 'for 迴圈遍歷字串 "Hello" 共執行幾次？',
         'explanation': '"Hello" 有 5 個字元（H,e,l,l,o），迴圈執行 5 次。',
         'choices': [('4', False), ('5', True), ('6', False), ('視情況而定', False)]},
        {'content': '以下程式，total 最後的值是多少？\n\n```python\ntotal = 0\nfor x in [10, 20, 30]:\n    total += x\nprint(total)\n```',
         'explanation': '10 + 20 + 30 = 60。',
         'choices': [('30', False), ('60', True), ('600', False), ('0', False)]},
        {'content': 'break 的作用是？',
         'explanation': 'break 立即跳出它所在的最內層迴圈，不再繼續執行迴圈。',
         'choices': [('跳過本次，繼續下一輪', False), ('立即跳出迴圈', True), ('結束整個程式', False), ('暫停迴圈', False)]},
        {'content': 'continue 的作用是？',
         'explanation': 'continue 跳過本次迴圈剩餘的程式碼，直接進入下一次迭代。',
         'choices': [('立即跳出迴圈', False), ('跳過本次，繼續下一輪', True), ('結束整個程式', False), ('讓迴圈倒退', False)]},
        {'content': '巢狀迴圈 for i in range(2): for j in range(3): 內層程式碼共執行幾次？',
         'explanation': '外層 2 次 × 內層 3 次 = 共 6 次。',
         'choices': [('2', False), ('3', False), ('5', False), ('6', True)]},
        {'content': 'for 迴圈可以走訪哪些資料？',
         'explanation': 'for 迴圈可以走訪任何可迭代物件，包括串列、字串、range 等。',
         'choices': [('只有串列', False), ('只有數字', False), ('串列、字串、range 等都可以', True), ('只有 range', False)]},
    ],
    # ── Unit 8: 迴圈應用（while）────────────────────────────────────
    [
        {'content': '這段程式會印出什麼？\n\n```python\ncount = 0\nwhile count < 3:\n    print(count)\n    count = count + 1\n```',
         'explanation': 'count 從 0 跑到 2（不含 3），依序印出 0、1、2。',
         'choices': [('0 1 2（各自一行）', True), ('0 1 2 3（各自一行）', False),
                     ('1 2 3（各自一行）', False), ('只印一次 0', False)]},
        {'content': '下面程式有什麼問題？\n\n```python\ncount = 0\nwhile count < 5:\n    print(count)\n```',
         'explanation': 'count 永遠是 0，條件永遠 True，形成無限迴圈。修正：在迴圈內加 count += 1。',
         'choices': [('缺少 else 區塊', False), ('count 初始值錯誤', False),
                     ('無限迴圈，缺少更新 count', True), ('while 語法錯誤', False)]},
        {'content': 'while 迴圈和 for 迴圈最主要的差別是？',
         'explanation': 'for 通常用於已知次數的遍歷；while 適合次數不固定、依條件決定的場景。',
         'choices': [('while 速度比較快', False), ('for 只能遍歷串列', False),
                     ('while 適合次數不固定的重複', True), ('兩者完全一樣', False)]},
        {'content': 'while 迴圈什麼時候停止？',
         'explanation': '當 while 後面的條件變成 False 時，迴圈停止執行。',
         'choices': [('執行 10 次後自動停止', False), ('條件變成 False 時停止', True),
                     ('執行完所有元素後停止', False), ('需要手動停止', False)]},
        {'content': '以下程式執行完後，total 的值是？\n\n```python\ntotal = 0\ni = 1\nwhile i <= 5:\n    total += i\n    i += 1\n```',
         'explanation': '1+2+3+4+5 = 15。',
         'choices': [('10', False), ('15', True), ('14', False), ('20', False)]},
        {'content': '下列程式，break 前共印了幾行？\n\n```python\ni = 0\nwhile i < 10:\n    if i == 3:\n        break\n    print(i)\n    i += 1\n```',
         'explanation': 'i = 0,1,2 各印一行（共 3 行），i = 3 時執行 break 離開，不印 3。',
         'choices': [('2 行', False), ('3 行', True), ('4 行', False), ('10 行', False)]},
        {'content': 'while True: ... break 這個模式的意義是？',
         'explanation': 'while True 讓迴圈一直執行，搭配 break 在符合條件時離開，是「直到條件成立才停止」的常見寫法。',
         'choices': [('永遠不結束', False), ('直到 break 條件成立才離開', True),
                     ('只執行一次', False), ('等同於 for 迴圈', False)]},
        {'content': '以下程式，x 從 10 開始減，最後輸出什麼？\n\n```python\nx = 10\nwhile x > 0:\n    x -= 3\nprint(x)\n```',
         'explanation': 'x：10→7→4→1→-2（-2 > 0 為 False 停止），最後 x = -2。',
         'choices': [('0', False), ('-2', True), ('1', False), ('無限迴圈', False)]},
        {'content': '以下累加程式印出的結果是什麼？\n\n```python\ntotal = 0\ni = 2\nwhile i <= 10:\n    total += i\n    i += 2\nprint(total)\n```',
         'explanation': '2+4+6+8+10 = 30。',
         'choices': [('25', False), ('30', True), ('55', False), ('20', False)]},
        {'content': 'while 迴圈結束後，迴圈內的變數還可以使用嗎？',
         'explanation': 'while 迴圈結束後，迴圈內定義的變數仍然存在，保留最後一次的值。',
         'choices': [('不行，變數會消失', False), ('可以，保留最後一次的值', True),
                     ('變數會重設為 0', False), ('取決於變數名稱', False)]},
    ],
]


def split_md_by_units(md_content):
    """將 MD 內容按 ## Unit 切分為各單元字典"""
    sections = {}
    parts = re.split(r'(?m)^## Unit \d+', md_content)
    headers = re.findall(r'(?m)^## Unit (\d+)[^\n]*', md_content)
    for i, header in enumerate(headers):
        unit_num = int(header)
        if i + 1 < len(parts):
            sections[unit_num] = f'## Unit {header}{parts[i + 1]}'
    return sections


class Command(BaseCommand):
    help = '建立 Python 教材課程、單元與評量的初始資料'

    def handle(self, *args, **options):
        # Delegate to module-level _handle function
        _handle(self, *args, **options)


# ── Level 2 填空題（每單元 10 題，需要理解語法才能填對）───────────────────
SHORT_ANSWER_QUESTIONS = [
    # Unit 1: print 輸出
    [
        {'content': 'print("Hello", _____="") 讓輸出後不換行。\n填入參數名稱。', 'correct_answer': 'end', 'explanation': 'end 參數控制結尾字元，設為空字串則不換行。'},
        {'content': 'print(1, 2, 3, _____="-") 輸出 1-2-3。\n填入參數名稱。', 'correct_answer': 'sep', 'explanation': 'sep 參數設定多個值之間的分隔字元。'},
        {'content': 'name = "Alice"\nprint(f"Hello, _____!") 輸出 Hello, Alice!\n填入 f-string 中取得 name 變數的寫法。', 'correct_answer': '{name}', 'explanation': 'f-string 中變數要放在 {} 內。'},
        {'content': 'score = 92.5\nprint(f"分數：{score:_____}") 輸出 分數：92.50\n填入小數保留 2 位的格式指定碼。', 'correct_answer': '.2f', 'explanation': ':.2f 表示浮點數保留兩位小數。'},
        {'content': 'print(f"{"Hi":>_____}") 輸出右對齊、寬度 10 的 Hi（前面有空格）。\n填入寬度數字。', 'correct_answer': '10', 'explanation': ':>10 表示靠右對齊，總寬度 10。'},
        {'content': 'print(f"{42:_____d}") 輸出 00042（寬度 5，不足補零）。\n填入格式指定碼（補零寬度 5）。', 'correct_answer': '05', 'explanation': ':05d 表示整數，寬度 5，不足補零。'},
        {'content': 'pi = 3.14159\nprint(f"{pi:_____}") 輸出 3.14（保留 2 位小數，不補空格）。\n填入格式指定碼。', 'correct_answer': '.2f', 'explanation': ':.2f 表示保留兩位小數。'},
        {'content': 'print("A", end="")\nprint("B", end="")\nprint("C")\n以上程式輸出是什麼？', 'correct_answer': 'ABC', 'explanation': 'end="" 讓前兩個 print 不換行，最後一個用預設換行。'},
        {'content': 'print(10 // 3) 的輸出是什麼？\n// 是整除運算子。', 'correct_answer': '3', 'explanation': '// 是整除運算子，10 ÷ 3 商為 3，捨去餘數。'},
        {'content': 'print(10 % 3) 的輸出是什麼？\n% 是取餘數運算子。', 'correct_answer': '1', 'explanation': '% 取餘數，10 ÷ 3 餘 1。'},
    ],
    # Unit 2: input 輸入與運算
    [
        {'content': 'height = _____(input("輸入身高（公尺）："))\nweight = _____(input("輸入體重（公斤）："))\nbmi = weight / height ** 2\n\n填入相同的型別轉換函式（身高體重可能有小數）。', 'correct_answer': 'float', 'explanation': 'float() 將字串轉為浮點數，適合有小數點的輸入。'},
        {'content': 'a, b = input("輸入兩個整數（空格分隔）：").split()\na, b = int(a), int(b)\nprint(a + b)\n\n如果輸入 "12 8"，輸出是什麼？', 'correct_answer': '20', 'explanation': '12 和 8 分別轉為整數後相加，結果為 20。'},
        {'content': 'result = eval("2 ** 8")\nprint(result)\n\n輸出是什麼？', 'correct_answer': '256', 'explanation': 'eval() 解析並計算字串中的算式，2 的 8 次方 = 256。'},
        {'content': 'x = input("輸入數字：")\nprint(type(x).__name__)\n\n不管使用者輸入什麼，輸出一定是什麼？', 'correct_answer': 'str', 'explanation': 'input() 一律回傳字串型別，type(x).__name__ 輸出 "str"。'},
        {'content': 'n = int(input("輸入整數："))\nprint(n ** 2)\n\n如果輸入 7，輸出是什麼？', 'correct_answer': '49', 'explanation': '7 ** 2 = 49。'},
        {'content': 'a = int(input())\nb = int(input())\nprint(a // b, a % b)\n\n如果依序輸入 17 和 5，輸出是什麼？（格式：商 餘數）', 'correct_answer': '3 2', 'explanation': '17 // 5 = 3（商），17 % 5 = 2（餘數）。'},
        {'content': 'price = float(input("單價："))\nqty = int(input("數量："))\ntotal = price * qty\nprint(f"總價：{total:.2f}")\n\n輸入單價 12.5、數量 3，輸出是什麼？', 'correct_answer': '總價：37.50', 'explanation': '12.5 * 3 = 37.5，:.2f 保留兩位小數。'},
        {'content': 'x = "5"\ny = x * 3\nprint(y)\n\n輸出是什麼？（x 是字串，未做型別轉換）', 'correct_answer': '555', 'explanation': '字串 * 整數 = 字串重複，"5" * 3 = "555"。'},
        {'content': 'print(round(3.567, 2))\n\n輸出是什麼？round() 做四捨五入。', 'correct_answer': '3.57', 'explanation': 'round(3.567, 2) 四捨五入到小數第 2 位，得 3.57。'},
        {'content': 'print(abs(-42))\n\n輸出是什麼？abs() 取絕對值。', 'correct_answer': '42', 'explanation': 'abs(-42) 回傳絕對值 42。'},
    ],
    # Unit 3: if 條件判斷
    [
        {'content': 'x = 5\nif x > 0:\n    print("正數")\n_____:\n    print("非正數")\n\n填入缺少的關鍵字。', 'correct_answer': 'else', 'explanation': 'else 處理 if 條件不成立時的情況。'},
        {'content': 'if x > 0 _____ x < 10:\n    print("介於 1~9")\n\n填入讓「兩個條件都要成立」的邏輯運算子。', 'correct_answer': 'and', 'explanation': 'and 要求兩個條件都成立。'},
        {'content': 'if x < 0 _____ x > 100:\n    print("超出範圍")\n\n填入讓「其中一個條件成立即可」的邏輯運算子。', 'correct_answer': 'or', 'explanation': 'or 只要一個條件成立即可。'},
        {'content': 'score = 85\ngrade = "A" if score >= 90 else "B" if score >= 80 _____ "C"\nprint(grade)\n\n填入關鍵字，讓輸出為 B。', 'correct_answer': 'else', 'explanation': '巢狀三元運算子最後需要 else 作為預設值。'},
        {'content': 'x = 7\nif x _____ [1, 3, 5, 7, 9]:\n    print("奇數")\n\n填入判斷元素是否存在於串列的運算子。', 'correct_answer': 'in', 'explanation': 'in 運算子判斷元素是否在序列中。'},
        {'content': 'is_adult = True\nif _____ is_adult:\n    print("未成年")\n\n填入讓條件取反的運算子。', 'correct_answer': 'not', 'explanation': 'not 對布林值取反，not True = False。'},
        {'content': 'x = 0\nif x:\n    print("True")\nelse:\n    print("False")\n\n輸出是什麼？（0 在 if 中視為？）', 'correct_answer': 'False', 'explanation': '0 在 Python 中被視為 False，執行 else 區塊。'},
        {'content': 'a = 5\nb = 10 if a > 3 else 0\nprint(b)\n\n輸出是什麼？', 'correct_answer': '10', 'explanation': 'a=5 > 3 成立，三元運算式回傳 10。'},
        {'content': 'msg = "hello world"\nif "world" _____ msg:\n    print("找到了")\n\n填入判斷子字串是否在字串中的運算子。', 'correct_answer': 'in', 'explanation': 'in 可判斷子字串是否存在於字串中。'},
        {'content': 'score = 72\nresult = "及格" if score >= 60 else "不及格"\nprint(result)\n\n輸出是什麼？', 'correct_answer': '及格', 'explanation': '72 >= 60 成立，三元運算式回傳 "及格"。'},
    ],
    # Unit 4: 多條件 if
    [
        {'content': 'score = 75\nif score >= 90:\n    grade = "A"\n_____ score >= 80:\n    grade = "B"\nelif score >= 70:\n    grade = "C"\nelse:\n    grade = "F"\n\n填入第一個空缺的關鍵字。', 'correct_answer': 'elif', 'explanation': '多條件分支使用 elif 串接。'},
        {'content': 'x = 15\nif x % 3 == 0 and x % 5 == _____:\n    print("FizzBuzz")\n\n填入數字，讓條件判斷「同時被 3 和 5 整除」。', 'correct_answer': '0', 'explanation': '整除時餘數為 0，x % 5 == 0 判斷能被 5 整除。'},
        {'content': 'year = 2024\nif (year % 4 == 0 and year % 100 != 0) or year % 400 == _____:\n    print("閏年")\n\n填入數字。', 'correct_answer': '0', 'explanation': '能被 400 整除時餘數為 0，是閏年的條件之一。'},
        {'content': 'bmi = 22.5\nif bmi < 18.5:\n    status = "過輕"\nelif bmi < _____:\n    status = "正常"\nelif bmi < 27:\n    status = "過重"\nelse:\n    status = "肥胖"\n\n填入正常體重的 BMI 上限（台灣標準）。', 'correct_answer': '24', 'explanation': 'BMI 18.5~24 為正常體重（台灣衛福部標準）。'},
        {'content': 'a, b = 3, 7\nprint(_____(a, b))\n\n填入函式名稱，輸出兩數中較大的值 7。', 'correct_answer': 'max', 'explanation': 'max() 回傳傳入值中的最大值。'},
        {'content': 'a, b = 3, 7\nprint(_____(a, b))\n\n填入函式名稱，輸出兩數中較小的值 3。', 'correct_answer': 'min', 'explanation': 'min() 回傳傳入值中的最小值。'},
        {'content': 'month = 4\nif month in [1, 3, 5, 7, 8, 10, 12]:\n    days = 31\nelif month == 2:\n    days = 28\nelse:\n    days = _____\nprint(days)\n\n填入四月的天數。', 'correct_answer': '30', 'explanation': '4 月不在 31 天的月份列表，也不是 2 月，所以走 else，4 月有 30 天。'},
        {'content': 'score = 55\nresult = "通過" if score >= 60 else "_____"\nprint(result)\n\n填入 score < 60 時應顯示的字串。', 'correct_answer': '未通過', 'explanation': '55 < 60，三元運算式執行 else 部分。'},
        {'content': 'x = 7\nif x % 2 == 0:\n    parity = "偶數"\nelse:\n    parity = "_____"\nprint(parity)\n\n填入奇數的中文。', 'correct_answer': '奇數', 'explanation': '7 不被 2 整除，餘數為 1，不為偶數，所以是奇數。'},
        {'content': 'grade = "B"\nif grade == "A":\n    point = 4.0\nelif grade == "B":\n    point = 3.0\nelif grade == "C":\n    point = 2.0\nelse:\n    point = 0.0\nprint(point)\n\n輸出是什麼？', 'correct_answer': '3.0', 'explanation': 'grade == "B" 成立，執行 elif 區塊，point = 3.0。'},
    ],
    # Unit 5: list 串列
    [
        {'content': 'nums = [3, 1, 4, 1, 5]\nnums._()\nprint(nums)\n\n填入讓串列由小到大排序的方法名稱（原地修改）。', 'correct_answer': 'sort', 'explanation': 'sort() 將串列原地由小到大排序。'},
        {'content': 'nums = [10, 20, 30, 40, 50]\nprint(nums[1:4])\n\n輸出是什麼？（切片 [1:4] 取索引 1 到 3）', 'correct_answer': '[20, 30, 40]', 'explanation': '[1:4] 取索引 1、2、3 的元素，即 20、30、40。'},
        {'content': 'nums = [10, 20, 30, 40, 50]\nprint(nums[::2])\n\n輸出是什麼？（每隔一個取一個）', 'correct_answer': '[10, 30, 50]', 'explanation': '[::2] 步長為 2，取索引 0、2、4 的元素。'},
        {'content': 'a = [1, 2]\nb = [3, 4]\nc = a + b\nprint(c)\n\n輸出是什麼？', 'correct_answer': '[1, 2, 3, 4]', 'explanation': '+ 運算子合併兩個串列，回傳新串列。'},
        {'content': 'nums = [5, 3, 8, 1, 9, 2]\nprint(sorted(nums))\nprint(nums)\n\nsorted() 和 sort() 的差別是什麼？sorted() 後 nums 有改變嗎？\n回答：nums___改變。', 'correct_answer': '沒有', 'explanation': 'sorted() 回傳新排序串列，原串列不變；sort() 才是原地修改。'},
        {'content': 'scores = [88, 72, 95, 63, 80]\npassing = [s for s in scores if s >= 70]\nprint(len(passing))\n\n輸出是什麼？（及格分數 >= 70）', 'correct_answer': '4', 'explanation': '88、72、95、80 都 >= 70，共 4 個及格。'},
        {'content': 'names = ["Alice", "Bob", "Carol"]\nprint(names.index("Bob"))\n\n輸出是什麼？index() 回傳元素的索引。', 'correct_answer': '1', 'explanation': '"Bob" 在索引 1 的位置。'},
        {'content': 'nums = [1, 2, 3, 2, 1]\nprint(nums.count(2))\n\n輸出是什麼？count() 計算元素出現次數。', 'correct_answer': '2', 'explanation': '2 在串列中出現兩次。'},
        {'content': 'nums = [1, 2, 3]\nnums.insert(0, 99)\nprint(nums)\n\n輸出是什麼？insert(位置, 值) 在指定位置插入元素。', 'correct_answer': '[99, 1, 2, 3]', 'explanation': 'insert(0, 99) 在索引 0（開頭）插入 99。'},
        {'content': 'students = [("Alice", 92), ("Bob", 75), ("Carol", 88)]\nsorted_s = sorted(students, key=lambda x: x[1], reverse=True)\nprint(sorted_s[0][0])\n\n輸出是什麼？（依分數降冪排序後的第一名姓名）', 'correct_answer': 'Alice', 'explanation': '依分數降冪排序：Alice(92) > Carol(88) > Bob(75)，第一名是 Alice。'},
    ],
    # Unit 6: range 數列
    [
        {'content': 'print(list(range(0, 10, 2)))\n\n輸出是什麼？', 'correct_answer': '[0, 2, 4, 6, 8]', 'explanation': 'range(0, 10, 2) 從 0 開始，步長 2，到 9：0, 2, 4, 6, 8。'},
        {'content': 'print(list(range(5, 0, -1)))\n\n輸出是什麼？', 'correct_answer': '[5, 4, 3, 2, 1]', 'explanation': 'step=-1 產生遞減數列，從 5 到 1。'},
        {'content': 'print(sum(range(1, 101)))\n\n1 加到 100 的總和是多少？', 'correct_answer': '5050', 'explanation': '等差數列和公式：n*(n+1)/2 = 100*101/2 = 5050。'},
        {'content': 'print(sum(range(1, 51, 2)))\n\n1 到 49 所有奇數的總和是多少？', 'correct_answer': '625', 'explanation': '共 25 個奇數（1,3,5,...,49），總和 = 25² = 625。'},
        {'content': 'r = range(10)\nprint(50 in r)\n\n輸出是什麼？', 'correct_answer': 'False', 'explanation': 'range(10) 只包含 0~9，50 不在其中，回傳 False。'},
        {'content': 'nums = list(range(2, 11, 2))\nprint(nums[-1])\n\n輸出是什麼？', 'correct_answer': '10', 'explanation': 'range(2, 11, 2) = [2,4,6,8,10]，最後一個是 10。'},
        {'content': 'print(len(range(1, 101)))\n\n輸出是什麼？', 'correct_answer': '100', 'explanation': 'range(1, 101) 包含 1 到 100，共 100 個元素。'},
        {'content': 'squares = [x**2 for x in range(1, 6)]\nprint(squares)\n\n輸出是什麼？', 'correct_answer': '[1, 4, 9, 16, 25]', 'explanation': '1², 2², 3², 4², 5² = 1, 4, 9, 16, 25。'},
        {'content': 'evens = [x for x in range(1, 21) if x % 2 == 0]\nprint(len(evens))\n\n1 到 20 的偶數共有幾個？', 'correct_answer': '10', 'explanation': '2, 4, 6, ..., 20，共 10 個偶數。'},
        {'content': 'print(list(range(10, 0, -3)))\n\n輸出是什麼？', 'correct_answer': '[10, 7, 4, 1]', 'explanation': '從 10 開始，每次 -3：10, 7, 4, 1（-2 不在範圍內）。'},
    ],
    # Unit 7: for 迴圈
    [
        {'content': 'total = 0\nfor i in range(1, 11):\n    total += i\nprint(total)\n\n輸出是什麼？（1 加到 10）', 'correct_answer': '55', 'explanation': '1+2+...+10 = 55。'},
        {'content': 'fruits = ["apple", "banana", "cherry"]\nfor i, fruit in enumerate(fruits, 1):\n    print(f"{i}. {fruit}")\n\n第一行輸出是什麼？', 'correct_answer': '1. apple', 'explanation': 'enumerate(fruits, 1) 讓索引從 1 開始，第一次迭代輸出 "1. apple"。'},
        {'content': 'names = ["小明", "小華"]\nscores = [88, 72]\nfor name, score in zip(names, scores):\n    print(f"{name}：{score}")\n\n第一行輸出是什麼？', 'correct_answer': '小明：88', 'explanation': 'zip 配對第一個 (小明, 88)，輸出 "小明：88"。'},
        {'content': 'result = 1\nfor i in range(1, 6):\n    result *= i\nprint(result)\n\n輸出是什麼？（計算 5!）', 'correct_answer': '120', 'explanation': '5! = 1×2×3×4×5 = 120。'},
        {'content': 'count = 0\nfor x in range(1, 21):\n    if x % 3 == 0:\n        count += 1\nprint(count)\n\n1 到 20 中，3 的倍數有幾個？', 'correct_answer': '6', 'explanation': '3, 6, 9, 12, 15, 18，共 6 個。'},
        {'content': 'squares = [x**2 for x in range(1, 6) if x % 2 != 0]\nprint(squares)\n\n輸出是什麼？（取奇數的平方）', 'correct_answer': '[1, 9, 25]', 'explanation': '奇數 1, 3, 5 的平方分別是 1, 9, 25。'},
        {'content': 'for i in range(5):\n    if i == 3:\n        break\n    print(i, end=" ")\n\n輸出是什麼？', 'correct_answer': '0 1 2 ', 'explanation': 'i=0,1,2 時印出，i=3 時執行 break 離開迴圈。'},
        {'content': 'nums = [4, 7, 2, 9, 1]\nmax_val = nums[0]\nfor n in nums:\n    if n > max_val:\n        max_val = n\nprint(max_val)\n\n輸出是什麼？', 'correct_answer': '9', 'explanation': '走訪串列找最大值，結果為 9。'},
        {'content': 'matrix = [[1,2,3],[4,5,6],[7,8,9]]\nfor row in matrix:\n    print(row[1], end=" ")\n\n輸出是什麼？（取每列的索引 1 元素）', 'correct_answer': '2 5 8 ', 'explanation': '三列的索引 1 元素分別是 2, 5, 8。'},
        {'content': 'words = ["cat", "elephant", "dog", "bee"]\nlongest = max(words, key=len)\nprint(longest)\n\n輸出是什麼？（找最長的單字）', 'correct_answer': 'elephant', 'explanation': 'max() 配合 key=len 找長度最大的字串，elephant 有 8 個字元。'},
    ],
    # Unit 8: 迴圈應用
    [
        {'content': 'total = 0\nwhile True:\n    n = int(input())\n    if n == 0:\n        break\n    total += n\nprint(total)\n\n依序輸入 5, 3, 8, 0，輸出是什麼？', 'correct_answer': '16', 'explanation': '5+3+8=16，輸入 0 時 break 離開，輸出 16。'},
        {'content': 'result = 1\nfor i in range(1, 6):\n    result *= i\nprint(result)\n\n輸出是什麼？（5 的階乘）', 'correct_answer': '120', 'explanation': '5! = 1×2×3×4×5 = 120。'},
        {'content': 'nums = [3, 1, 4, 1, 5, 9, 2, 6]\nprint(max(nums))\nprint(min(nums))\nprint(sum(nums) / len(nums))\n\n第三行輸出的平均值是多少？', 'correct_answer': '3.875', 'explanation': '(3+1+4+1+5+9+2+6)/8 = 31/8 = 3.875。'},
        {'content': 'i = 1\ntotal = 0\nwhile i <= 100:\n    if i % 2 == 0:\n        total += i\n    i += 1\nprint(total)\n\n輸出是什麼？（1 到 100 所有偶數的總和）', 'correct_answer': '2550', 'explanation': '2+4+...+100 = 50×51 = 2550。'},
        {'content': 'matrix = [[1,2,3],[4,5,6],[7,8,9]]\nfor row in matrix:\n    print(row[0], end=" ")\n\n輸出是什麼？（取每列第一個元素）', 'correct_answer': '1 4 7 ', 'explanation': '三列的第一個元素（索引 0）分別是 1, 4, 7。'},
        {'content': 'pairs = list(zip(range(1, 4), ["a", "b", "c"]))\nprint(pairs)\n\n輸出是什麼？', 'correct_answer': '[(1, "a"), (2, "b"), (3, "c")]', 'explanation': 'zip 將兩個序列逐一配對成元組。'},
        {'content': 'count = 0\nfor i in range(2, 20):\n    is_prime = True\n    for j in range(2, i):\n        if i % j == 0:\n            is_prime = False\n            break\n    if is_prime:\n        count += 1\nprint(count)\n\n2 到 19 的質數有幾個？', 'correct_answer': '8', 'explanation': '2,3,5,7,11,13,17,19 共 8 個質數。'},
        {'content': 'data = [10, 25, 8, 42, 15]\nresult = [x for x in data if x > 20]\nprint(result)\n\n輸出是什麼？（篩選大於 20 的元素）', 'correct_answer': '[25, 42]', 'explanation': '25 和 42 都大於 20。'},
        {'content': 'n = 5\nfor i in range(1, n+1):\n    print("*" * i)\n\n最後一行輸出幾個星號？', 'correct_answer': '5', 'explanation': 'i=5 時印出 "*" * 5 = "*****"，共 5 個星號。'},
        {'content': 'nums = [1, 2, 3, 4, 5]\nresult = list(map(lambda x: x**2, nums))\nprint(result)\n\n輸出是什麼？', 'correct_answer': '[1, 4, 9, 16, 25]', 'explanation': 'map() 將 lambda x: x**2 套用到每個元素，得到各元素的平方。'},
    ],
]

# ── Level 3 程式設計題（每單元 10 題，學生撰寫完整程式）──────────────────
CODING_QUESTIONS = [
    # Unit 1: print 輸出
    [
        {'content': '撰寫程式，使用 print() 輸出以下格式的收據（至少 3 項商品）：\n```\n========== 收據 ==========\n商品A        $100\n商品B        $200\n==========================\n合計：$300\n```', 'correct_answer': '', 'explanation': '使用 print() 搭配字串格式化或 f-string 輸出對齊的收據格式。'},
        {'content': '撰寫程式，輸出一個 5×5 的星號方形：\n```\n*****\n*****\n*****\n*****\n*****\n```', 'correct_answer': '', 'explanation': '使用 for 迴圈搭配 print("*" * 5) 輸出五行。'},
        {'content': '撰寫程式，將以下數字以不同格式輸出：數字 3.14159\n- 一般輸出\n- 保留 2 位小數\n- 科學記號\n- 靠右對齊 10 個字元', 'correct_answer': '', 'explanation': '使用 f-string 格式控制：:.2f、:e、:>10。'},
        {'content': '撰寫程式，輸出 9×9 乘法表（只輸出上三角形部分）。', 'correct_answer': '', 'explanation': '外層迴圈 i=1~9，內層迴圈 j=i~9，使用 print(f"{i}×{j}={i*j}", end=" ")。'},
        {'content': '撰寫程式，接受一個英文句子作為字串常數，輸出：\n1. 原句\n2. 全大寫\n3. 全小寫\n4. 每個單字首字母大寫\n5. 單字數量', 'correct_answer': '', 'explanation': '使用 str.upper(), str.lower(), str.title(), len(str.split())。'},
        {'content': '撰寫程式，輸出前 10 個費波那契數列，每個數字占 5 格寬度靠右對齊。', 'correct_answer': '', 'explanation': '初始化 a,b=0,1，迴圈計算並用 f"{num:>5}" 格式化輸出。'},
        {'content': '撰寫程式，將一個二維串列（3×3 矩陣）以表格形式輸出，每個元素占 4 格寬度。', 'correct_answer': '', 'explanation': '外層迴圈遍歷列，內層遍歷行，用 print(f"{val:4}", end="") 格式化。'},
        {'content': '撰寫程式，以星號輸出一個中空的 7×5 矩形框。', 'correct_answer': '', 'explanation': '第一列和最後一列全星號，中間列只有首尾是星號，中間是空格。'},
        {'content': '撰寫程式，輸出攝氏 0~100 度（每隔 10 度）對應的華氏溫度，使用 f-string 格式化輸出。', 'correct_answer': '', 'explanation': '公式：F = C × 9/5 + 32，用 range(0,101,10) 迭代。'},
        {'content': '撰寫程式，輸出一個向右的數字三角形：\n```\n1\n12\n123\n1234\n12345\n```', 'correct_answer': '', 'explanation': '外層迴圈 i=1~5，內層 j=1~i，print(j, end="")，每列結束 print()。'},
    ],
    # Unit 2: input 輸入與運算
    [
        {'content': '撰寫程式，接受使用者輸入身高（公分）與體重（公斤），計算並輸出 BMI 值及對應的體重狀態（過輕/正常/過重/肥胖）。', 'correct_answer': '', 'explanation': 'BMI = 體重(kg) / 身高(m)²，需將公分轉為公尺後計算。'},
        {'content': '撰寫程式，輸入兩個整數，輸出這兩個數的最大公因數（GCD）。不可使用 math.gcd()。', 'correct_answer': '', 'explanation': '使用輾轉相除法（歐幾里得演算法）計算 GCD。'},
        {'content': '撰寫程式，輸入一個整數，判斷是否為質數，並輸出原因。', 'correct_answer': '', 'explanation': '從 2 到 sqrt(n) 逐一嘗試整除，使用 ** 0.5 計算平方根。'},
        {'content': '撰寫程式，實作簡單計算機：輸入兩個數字和運算符號（+, -, *, /），輸出計算結果，並處理除以零的情況。', 'correct_answer': '', 'explanation': '使用 if/elif/else 判斷運算符號，try/except 或 if 處理除零。'},
        {'content': '撰寫程式，輸入攝氏溫度，輸出對應的華氏和克氏溫度，並說明哪個溫度最低（克氏 = 攝氏 + 273.15）。', 'correct_answer': '', 'explanation': '三種溫度互相比較，使用 min() 或 if/elif 找最小值。'},
        {'content': '撰寫程式，輸入三角形三邊長，判斷是否能構成三角形，若可以則輸出三角形種類（等邊/等腰/不等邊）及面積（海龍公式）。', 'correct_answer': '', 'explanation': '三角形條件：任兩邊之和大於第三邊；面積用海龍公式計算。'},
        {'content': '撰寫程式，輸入本金、年利率（%）、年數，計算並輸出每年的複利金額。', 'correct_answer': '', 'explanation': '複利公式：A = P × (1 + r)^n，用 for 迴圈逐年計算。'},
        {'content': '撰寫程式，輸入一個正整數 n，輸出 1 到 n 的所有整數的平方和。', 'correct_answer': '', 'explanation': '公式：n(n+1)(2n+1)/6，或用 for 迴圈累加。'},
        {'content': '撰寫程式，輸入一個整數，輸出其所有因數，並判斷是否為完全數（因數之和等於自身）。', 'correct_answer': '', 'explanation': '從 1 到 n-1 逐一判斷整除，加總因數後比較。'},
        {'content': '撰寫程式，模擬找零系統：輸入商品價格與付款金額，輸出最少硬幣數的找零方案（500, 100, 50, 10, 5, 1 元）。', 'correct_answer': '', 'explanation': '貪心演算法：每次選最大面額的硬幣，依序計算數量。'},
    ],
    # Unit 3: if 條件判斷
    [
        {'content': '撰寫程式，輸入年份，判斷是否為閏年，並輸出從西元 1 年至今共有幾個閏年。', 'correct_answer': '', 'explanation': '閏年條件：(year%4==0 and year%100!=0) or year%400==0。'},
        {'content': '撰寫程式，實作石頭剪刀布遊戲：玩家輸入選擇，電腦隨機選擇，輸出勝負結果。需使用 random 模組。', 'correct_answer': '', 'explanation': '使用 random.choice() 產生電腦選擇，用 if/elif 判斷勝負。'},
        {'content': '撰寫程式，輸入一個字元，判斷是大寫字母、小寫字母、數字還是其他符號。使用 ord() 函式。', 'correct_answer': '', 'explanation': '使用 ord() 取得 ASCII 碼，比較範圍判斷字元類型。'},
        {'content': '撰寫程式，輸入三個邊長，判斷能否組成三角形，若可以判斷是銳角、直角還是鈍角三角形。', 'correct_answer': '', 'explanation': '先排序三邊，再用畢氏定理 a²+b² 與 c² 的關係判斷角形類型。'},
        {'content': '撰寫程式，實作密碼強度檢查：輸入密碼，判斷長度是否>=8，是否含大小寫字母、數字、特殊符號，輸出強度等級。', 'correct_answer': '', 'explanation': '用 any() 和字串方法（isupper, islower, isdigit）逐條檢查。'},
        {'content': '撰寫程式，輸入一個 3 位數整數，判斷是否為水仙花數（各位數字的立方和等於本身，如 153 = 1³+5³+3³）。', 'correct_answer': '', 'explanation': '用 // 和 % 分解百位、十位、個位，計算立方和後比較。'},
        {'content': '撰寫程式，模擬電梯系統：輸入目前樓層和目標樓層（1-10 樓），判斷方向（上/下），計算移動層數，輸出每一層的狀態。', 'correct_answer': '', 'explanation': '用 range 和 if 判斷方向，逐層輸出狀態。'},
        {'content': '撰寫程式，輸入月份，輸出該月的天數（需考慮閏年，年份也由使用者輸入）。', 'correct_answer': '', 'explanation': '使用 if/elif/else 處理 31/30/28/29 天的月份。'},
        {'content': '撰寫程式，輸入一個整數，判斷它是哪個數字範圍（個位數/十位數/百位數/千位數/更大），並說明判斷方法。', 'correct_answer': '', 'explanation': '使用 abs() 取絕對值後，逐步比較 1~9, 10~99 等範圍。'},
        {'content': '撰寫程式，實作成績等第系統：輸入 5 科成績，計算平均，依平均輸出等第（A+/A/B+/B/C/F），並輸出各科是否及格。', 'correct_answer': '', 'explanation': '用串列儲存成績，sum()/len() 計算平均，if/elif 判斷等第。'},
    ],
    # Unit 4: 多條件 if
    [
        {'content': '撰寫程式，實作自動販賣機：使用者輸入商品編號（1-5，各有不同價格）和投入金額，輸出是否足夠、找零或提示不足。', 'correct_answer': '', 'explanation': '用字典或 if/elif 儲存商品價格，計算差額後判斷是否足夠。'},
        {'content': '撰寫程式，模擬簡單的銀行系統：輸入帳號密碼（固定值），登入後可查詢餘額、存款、提款，提款需判斷餘額是否足夠。', 'correct_answer': '', 'explanation': '用 if 驗證帳號密碼，再用 if/elif 判斷操作類型。'},
        {'content': '撰寫程式，輸入身分證字號（10 碼），驗證格式是否正確：第一碼為英文字母，後九碼為數字。', 'correct_answer': '', 'explanation': '使用 len() 確認長度，[0].isalpha() 確認首碼，[1:].isdigit() 確認其餘。'},
        {'content': '撰寫程式，實作多幣別匯率換算：輸入金額和原始幣別，輸出換算為新台幣、美元、日圓、歐元的金額。', 'correct_answer': '', 'explanation': '用字典儲存匯率，if/elif 判斷輸入幣別後計算換算結果。'},
        {'content': '撰寫程式，輸入一個學生的各科成績，輸出加權平均（各科權重不同）、排名建議（前25%/中間50%/後25%）。', 'correct_answer': '', 'explanation': '定義各科權重，用 sum() 計算加權總分，再除以總權重得平均。'},
        {'content': '撰寫程式，模擬交通號誌系統：輸入目前號誌顏色（紅/黃/綠），輸出行為建議，並計算倒數秒數（紅60秒/綠45秒/黃5秒）。', 'correct_answer': '', 'explanation': '用 if/elif/else 判斷號誌顏色，輸出對應的行為和倒數秒數。'},
        {'content': '撰寫程式，輸入一個日期（年月日），驗證是否為有效日期，並計算是該年的第幾天。', 'correct_answer': '', 'explanation': '驗證月份範圍、各月天數（含閏年）；計算累加前幾個月的天數再加日。'},
        {'content': '撰寫程式，實作成績分流系統：輸入學生國英數三科成績，根據各科組合判斷適合的組別（理工/商科/文科/全面發展）。', 'correct_answer': '', 'explanation': '定義各組的門檻條件，用 if/elif/else 判斷符合哪個組別。'},
        {'content': '撰寫程式，輸入體溫，判斷體溫狀態（低體溫/正常/低燒/中燒/高燒），並輸出建議處置方式。', 'correct_answer': '', 'explanation': '用 if/elif/else 根據不同溫度範圍輸出對應狀態和建議。'},
        {'content': '撰寫程式，模擬停車場計費系統：輸入停車時數（可含小數），計費規則：前1小時30元，之後每小時20元，最高200元。', 'correct_answer': '', 'explanation': '用 if/elif 判斷時數，計算費用後與最高費用比較取較小值。'},
    ],
    # Unit 5: list 串列
    [
        {'content': '撰寫程式，輸入 10 個學生成績，儲存於串列，輸出：最高分、最低分、平均分、及格人數、不及格人數，以及成績由高到低的排序。', 'correct_answer': '', 'explanation': '使用 max(), min(), sum()/len(), 串列推導式篩選及格/不及格，sort() 排序。'},
        {'content': '撰寫程式，產生費波那契數列前 20 項，存入串列，輸出所有偶數費波那契數。', 'correct_answer': '', 'explanation': '迴圈計算費波那契，append() 加入串列，串列推導式篩選偶數。'},
        {'content': '撰寫程式，輸入一個字串，統計每個字母出現的次數（不分大小寫），以次數由多到少輸出。', 'correct_answer': '', 'explanation': '用字典統計，轉換成串列後用 sort(key=) 依次數排序輸出。'},
        {'content': '撰寫程式，實作二元搜尋法：先產生 20 個隨機整數（1-100）並排序，輸入目標值，用二元搜尋找出位置。', 'correct_answer': '', 'explanation': '初始化 low, high 指標，每次取中間值比較，縮小範圍直到找到或確認不存在。'},
        {'content': '撰寫程式，輸入兩個串列的元素，輸出兩個串列的聯集、交集、差集。', 'correct_answer': '', 'explanation': '可使用 set() 轉換後用集合運算（|, &, -），再轉回 sorted list。'},
        {'content': '撰寫程式，實作矩陣轉置：輸入一個 3×4 的矩陣（用巢狀串列），輸出其轉置矩陣（4×3）。', 'correct_answer': '', 'explanation': '轉置矩陣的 [i][j] = 原矩陣的 [j][i]，使用雙層串列推導式。'},
        {'content': '撰寫程式，模擬洗牌：建立 52 張撲克牌串列（4 種花色 × 13 張），使用 random.shuffle() 洗牌，輸出前 5 張。', 'correct_answer': '', 'explanation': '用雙層 for 迴圈或串列推導式建立牌組，random.shuffle() 洗牌。'},
        {'content': '撰寫程式，對一個整數串列實作氣泡排序法（不可使用 sort()），並輸出每一輪排序後的狀態。', 'correct_answer': '', 'explanation': '雙層迴圈比較相鄰元素，若前者較大則交換，每輪後輸出當前串列狀態。'},
        {'content': '撰寫程式，輸入一個字串，判斷是否為回文（正反讀相同），並輸出最長的回文子字串。', 'correct_answer': '', 'explanation': '反轉字串比較判斷回文，找最長回文子字串需兩層迴圈比較所有子字串。'},
        {'content': '撰寫程式，模擬投票系統：有 5 位候選人，輸入 20 張選票（輸入候選人編號），統計各候選人票數，輸出排名和當選者。', 'correct_answer': '', 'explanation': '用串列或字典統計票數，max() 找最高票，sorted() 排序輸出排名。'},
    ],
    # Unit 6: range 數列
    [
        {'content': '撰寫程式，使用 range 產生 1 到 100 的所有整數，找出其中所有的質數，輸出質數串列及質數個數。', 'correct_answer': '', 'explanation': '外層 range(2,101)，內層 range(2,int(n**0.5)+1) 判斷質數。'},
        {'content': '撰寫程式，輸入 n，使用 range 和串列推導式輸出帕斯卡三角形（楊輝三角形）的前 n 行。', 'correct_answer': '', 'explanation': '每行第 k 個元素 = C(n,k)，或用上一行計算：row[i] = prev[i-1] + prev[i]。'},
        {'content': '撰寫程式，使用 range 產生 1 到 1000 的整數，找出所有同時被 3、5、7 整除的數，並計算其總和。', 'correct_answer': '', 'explanation': '用 range(1,1001) 配合 if n%3==0 and n%5==0 and n%7==0 篩選。'},
        {'content': '撰寫程式，使用 range 模擬時鐘：輸出 00:00:00 到 23:59:59 的所有時刻（格式為 HH:MM:SS），只輸出秒數為 0 的時刻（即每分鐘整）。', 'correct_answer': '', 'explanation': '三層 range 迴圈（小時/分鐘/秒），用 f-string 格式化為 HH:MM:SS。'},
        {'content': '撰寫程式，輸入 n，使用 range 計算 π 的近似值（Leibniz 公式）：π/4 = 1 - 1/3 + 1/5 - 1/7 + ...（前 n 項）。', 'correct_answer': '', 'explanation': '用 range(n) 計算 (-1)**i / (2*i+1) 的累加，結果乘以 4。'},
        {'content': '撰寫程式，使用 range 產生一個 5×5 的乘法表格，對角線元素特別標示（加括號）。', 'correct_answer': '', 'explanation': '雙層 range 迴圈，當 i==j 時（對角線）用不同格式輸出。'},
        {'content': '撰寫程式，使用 range 和串列模擬彩券系統：從 1-49 中隨機選 6 個不重複的數字（樂透），輸入玩家選的 6 個號碼，比對中獎情況。', 'correct_answer': '', 'explanation': '用 random.sample(range(1,50),6) 產生彩券號碼，用集合交集計算中獎數量。'},
        {'content': '撰寫程式，使用 range 實作數字金字塔：輸入行數 n，輸出數字從中心向外排列的菱形。', 'correct_answer': '', 'explanation': '上半部 range(1,n+1)，下半部 range(n-1,0,-1)，每行計算空格和數字的對齊。'},
        {'content': '撰寫程式，使用 range 計算調和級數（1 + 1/2 + 1/3 + ... + 1/n），輸入 n，輸出總和及每一步的累積值。', 'correct_answer': '', 'explanation': '用 range(1,n+1) 累加 1/i，每次輸出當前累積總和。'},
        {'content': '撰寫程式，使用 range 模擬等差數列和等比數列：輸入首項、公差/公比和項數，輸出各項及總和。', 'correct_answer': '', 'explanation': '等差：a_n = a_1 + (n-1)*d；等比：a_n = a_1 * r^(n-1)。'},
    ],
    # Unit 7: for 迴圈
    [
        {'content': '撰寫程式，使用 for 迴圈和 enumerate 實作字串加密（凱薩密碼）：輸入字串和位移量，輸出加密後的字串。', 'correct_answer': '', 'explanation': '對每個字元用 ord() 取 ASCII，加上位移後用 chr() 轉回字元，需處理溢出（% 26）。'},
        {'content': '撰寫程式，使用 for 迴圈實作矩陣相乘：輸入兩個 3×3 矩陣，輸出它們的乘積矩陣。', 'correct_answer': '', 'explanation': '三層 for 迴圈：result[i][j] += a[i][k] * b[k][j]。'},
        {'content': '撰寫程式，使用 for 迴圈實作河內塔：輸入盤子數 n，輸出每一步的移動方式。', 'correct_answer': '', 'explanation': '遞迴或迭代實作：將 n-1 個盤子從源柱移到暫存柱，再移最大盤，再將 n-1 個從暫存移到目標。'},
        {'content': '撰寫程式，輸入一段英文文章（字串），統計每個單字出現次數，輸出前 5 個最常見的單字。', 'correct_answer': '', 'explanation': '用 split() 分割單字，字典統計次數，sorted() 依次數排序後取前 5。'},
        {'content': '撰寫程式，使用 for 迴圈實作數字系統轉換：輸入一個十進位整數，輸出其二進位、八進位和十六進位表示。不可使用 bin(), oct(), hex()。', 'correct_answer': '', 'explanation': '反覆對 2/8/16 取餘數，收集商和餘數，組合成對應進位制表示。'},
        {'content': '撰寫程式，使用 for 迴圈模擬蒙地卡羅方法估算圓周率：產生 10000 個隨機點，計算落在單位圓內的比例，輸出 π 的估算值。', 'correct_answer': '', 'explanation': '隨機產生 (x,y) 在 [-1,1] 範圍，若 x²+y²<=1 則在圓內，π ≈ 4 × 圓內點數/總點數。'},
        {'content': '撰寫程式，使用 for 迴圈實作選擇排序：對輸入的 10 個整數進行排序，每輪輸出當前狀態。', 'correct_answer': '', 'explanation': '每輪從未排序部分找最小值，與未排序部分第一個元素交換。'},
        {'content': '撰寫程式，使用 for 迴圈和串列推導式，找出 1000 以內所有的完全數（因數之和等於自身，如 6=1+2+3）。', 'correct_answer': '', 'explanation': '對每個數找其因數串列（不含自身），sum() 判斷是否為完全數。'},
        {'content': '撰寫程式，使用 for 迴圈實作簡單的文字直方圖：輸入 5 個科目的成績，用星號輸出橫向長條圖。', 'correct_answer': '', 'explanation': '對每科輸出：科目名 + " | " + "*" × (分數//10)。'},
        {'content': '撰寫程式，使用 for 迴圈模擬生命遊戲（Conway\'s Game of Life）一步演化：輸入 5×5 格子的初始狀態，輸出演化後的狀態。', 'correct_answer': '', 'explanation': '對每個格子計算 8 個鄰居的活細胞數，套用生存/死亡規則產生下一代。'},
    ],
    # Unit 8: 迴圈應用
    [
        {'content': '撰寫程式，實作完整的學生成績管理系統：可新增學生成績、查詢特定學生、輸出全班統計（平均/最高/最低/及格率），並按成績排序輸出名單。', 'correct_answer': '', 'explanation': '用字典儲存 {姓名: 成績}，實作新增、查詢、統計功能。'},
        {'content': '撰寫程式，模擬銀行複利存款計算機：輸入本金、年利率和存款年數，輸出每年的本利和，並繪製簡單的文字折線圖（用 * 表示金額）。', 'correct_answer': '', 'explanation': '每年計算 A = P*(1+r)^n，累積結果後按比例輸出對應數量的星號。'},
        {'content': '撰寫程式，實作文字版貪吃蛇初始狀態：在 10×10 的格子中，蛇的初始位置為 3 格（從第 5 行開始），食物隨機放置，輸出整個棋盤。', 'correct_answer': '', 'explanation': '用二維串列代表棋盤，蛇的位置標記為 O，頭標記為 @，食物標記為 *。'},
        {'content': '撰寫程式，使用巢狀迴圈實作數獨驗證器：輸入一個 9×9 的數獨解答（二維串列），驗證每行、每列、每個 3×3 宮格是否都包含 1-9 各一次。', 'correct_answer': '', 'explanation': '對每行、每列、每個 3×3 宮格轉成集合，判斷是否等於 {1,...,9}。'},
        {'content': '撰寫程式，實作字串壓縮：對輸入字串進行行程長度編碼（如 "aaabbc" 壓縮為 "a3b2c1"），並實作解壓縮功能。', 'correct_answer': '', 'explanation': '壓縮：計算連續相同字元的數量；解壓縮：讀取字元和數字後重複輸出。'},
        {'content': '撰寫程式，模擬股票技術分析：輸入 20 天的收盤價，計算 5 日和 10 日移動平均線，輸出每天的收盤價及移動平均線，並標記黃金交叉（5日上穿10日）和死亡交叉（5日下穿10日）。', 'correct_answer': '', 'explanation': '移動平均：sum(prices[i-n:i])/n，比較相鄰兩天的 5MA 和 10MA 關係判斷交叉。'},
        {'content': '撰寫程式，實作密碼產生器：根據使用者設定（長度、是否含大寫/小寫/數字/特殊符號），產生符合條件的隨機密碼，並評估密碼強度。', 'correct_answer': '', 'explanation': '用 random.choice() 從符合條件的字元集選取，確保各類型至少一個，評估條件數判斷強度。'},
        {'content': '撰寫程式，模擬圖書館借還書系統：維護書籍串列（書名、庫存量），實作查詢、借書（庫存-1）、還書（庫存+1）功能，並處理庫存不足的情況。', 'correct_answer': '', 'explanation': '用字典 {書名: 庫存} 儲存資料，借書時判斷庫存>0，還書無條件+1。'},
        {'content': '撰寫程式，實作矩陣螺旋輸出：輸入 n×n 的矩陣，按螺旋順序（右→下→左→上）輸出所有元素。', 'correct_answer': '', 'explanation': '維護四個邊界（top, bottom, left, right），每輪縮小邊界並依序輸出對應方向的元素。'},
        {'content': '撰寫程式，綜合應用題：模擬期末成績計算系統，輸入學生的平時成績（30%）、期中成績（30%）、期末成績（40%），計算加權總分，輸出全班的成績分佈直方圖（以 10 分為一組），並標示平均線位置。', 'correct_answer': '', 'explanation': '計算加權分，用串列分組統計（每10分一個區間），輸出每組的學生數量用星號表示。'},
    ],
]

def _handle(self, *args, **options):
    self.stdout.write('開始建立教材資料...')

    # 建立或取得教師帳號
    teacher, created = User.objects.get_or_create(
        username='teacher',
        defaults={
            'email': 'teacher@adaptlearn.tw',
            'role': 'teacher',
            'first_name': '系統',
            'last_name': '教師',
        }
    )
    if created:
        teacher.set_password('teacher1234')
        teacher.save()
        self.stdout.write(f'  建立教師帳號：teacher / teacher1234')

    for course_data in COURSES:
        # 建立課程
        course, c_created = Course.objects.get_or_create(
            title=course_data['title'],
            defaults={
                'description': course_data['description'],
                'teacher': teacher,
                'difficulty': course_data['difficulty'],
                'is_active': True,
            }
        )
        status = '新建' if c_created else '已存在'
        self.stdout.write(f'  [{status}] 課程：{course.title}')

        # 讀取 MD 教材
        md_path = MATERIALS_DIR / course_data['md_file']
        md_content = ''
        if md_path.exists():
            md_content = md_path.read_text(encoding='utf-8')
            self.stdout.write(f'    讀取教材：{md_path.name}')
        else:
            self.stdout.write(self.style.WARNING(f'    找不到教材檔案：{md_path}'))

        unit_sections = split_md_by_units(md_content) if md_content else {}

        for order, unit_title in enumerate(UNIT_TITLES, start=1):
            content = unit_sections.get(order, f'# {unit_title}\n\n（請至教材資料夾查看完整內容）')

            lesson, l_created = Lesson.objects.get_or_create(
                course=course,
                order=order,
                defaults={
                    'title': unit_title,
                    'content': content,
                    'lesson_type': 'text',
                    'duration_minutes': 30,
                }
            )
            if not l_created and lesson.content != content:
                lesson.content = content
                lesson.save()

            l_status = '新建' if l_created else '已存在'
            self.stdout.write(f'    [{l_status}] 單元 {order}：{unit_title}')

            # 建立評量（每個單元一份形成性評量）
            quiz, q_created = Quiz.objects.get_or_create(
                lesson=lesson,
                quiz_type='formative',
                defaults={
                    'title': f'Unit {order} 形成性評量 — {unit_title}',
                    'pass_score': 60.0,
                }
            )

            if q_created and order - 1 < len(QUIZ_QUESTIONS):
                difficulty = course_data['difficulty']
                if difficulty == 'beginner':
                    questions_bank = QUIZ_QUESTIONS[order - 1]
                    q_type = 'multiple_choice'
                elif difficulty == 'intermediate':
                    questions_bank = SHORT_ANSWER_QUESTIONS[order - 1]
                    q_type = 'short_answer'
                else:
                    questions_bank = CODING_QUESTIONS[order - 1]
                    q_type = 'coding'

                for q_idx, q_data in enumerate(questions_bank, start=1):
                    question = Question.objects.create(
                        quiz=quiz,
                        content=q_data['content'],
                        question_type=q_type,
                        correct_answer=q_data.get('correct_answer', ''),
                        points=10.0,
                        order=q_idx,
                        explanation=q_data.get('explanation', ''),
                    )
                    if q_type == 'multiple_choice':
                        for choice_text, is_correct in q_data['choices']:
                            Choice.objects.create(
                                question=question,
                                content=choice_text,
                                is_correct=is_correct,
                            )
                self.stdout.write(f'      建立評量：{quiz.title}（{len(questions_bank)} 題，{q_type}）')

    self.stdout.write(self.style.SUCCESS('\n[OK] 教材資料建立完成！'))
