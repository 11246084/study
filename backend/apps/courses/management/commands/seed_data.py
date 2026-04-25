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


# ── Level 2 填空題（每單元 10 題，測驗與 Level 1 相同的核心概念）──────────
SHORT_ANSWER_QUESTIONS = [
    # Unit 1: print 輸出
    [
        {'content': '___(\"蘋果\") 讓程式在螢幕上顯示「蘋果」。\n填入函式名稱。', 'correct_answer': 'print', 'explanation': 'print() 是輸出到螢幕的函式。'},
        {'content': 'print(3 ___ 5) 讓輸出為 8。\n填入運算符號。', 'correct_answer': '+', 'explanation': '3 + 5 = 8，+ 是加法運算符號。'},
        {'content': 'print(\"答案是\", ___) 讓輸出為「答案是 15」。\n填入 5×3 的結果。', 'correct_answer': '15', 'explanation': 'print() 逗號分隔的引數中間自動加空格，5 × 3 = 15。'},
        {'content': 'print(10, 20) 的輸出是什麼？', 'correct_answer': '10 20', 'explanation': 'print() 有多個引數時，預設用空格分隔輸出。'},
        {'content': 'print(\"A\")\nprint(\"B\")\n執行後螢幕上共有幾行輸出？', 'correct_answer': '2', 'explanation': '每個 print() 執行後自動換行，兩個 print() 產生兩行輸出。'},
        {'content': 'print(5 ___ 3) 讓輸出為 2。\n填入運算符號。', 'correct_answer': '-', 'explanation': '5 - 3 = 2，- 是減法運算符號。'},
        {'content': 'print(\"結果是\", 5 * 3) 的輸出是什麼？', 'correct_answer': '結果是 15', 'explanation': 'print() 同時顯示文字和數字，逗號處自動加空格，5*3=15。'},
        {'content': 'print() 括號內不放任何引數，輸出是什麼？\n（填「空行」兩字）', 'correct_answer': '空行', 'explanation': 'print() 不帶引數時，只輸出一個換行符，即一個空行。'},
        {'content': 'print(4 ___ 3) 讓輸出為 12。\n填入運算符號。', 'correct_answer': '*', 'explanation': '4 × 3 = 12，* 是乘法運算符號。'},
        {'content': 'print(Python) 這行程式執行會報什麼錯誤？\n（Python 沒有加引號）\n填入錯誤類型名稱。', 'correct_answer': 'NameError', 'explanation': '沒有引號的 Python 被視為變數名稱，找不到會引發 NameError。'},
    ],
    # Unit 2: input 輸入與運算
    [
        {'content': 'x = input()\nprint(type(x).__name__)\n輸入任何內容，輸出的型別名稱一定是什麼？', 'correct_answer': 'str', 'explanation': 'input() 不論輸入什麼，都回傳字串（str）型別。'},
        {'content': 'x = ___(input(\"輸入整數：\"))\n讓使用者輸入的值可以做整數加法。\n填入型別轉換函式名稱。', 'correct_answer': 'int', 'explanation': 'int() 將字串轉為整數，才能進行整數運算。'},
        {'content': 'x = ___(input(\"身高（公尺）：\"))\n讓輸入的身高可以有小數（如 1.75）。\n填入型別轉換函式名稱。', 'correct_answer': 'float', 'explanation': 'float() 將字串轉為浮點數，適合有小數點的輸入。'},
        {'content': 'x = int(input())\nprint(x + 3)\n輸入 5 後，輸出是什麼？', 'correct_answer': '8', 'explanation': 'int() 將 "5" 轉為整數 5，5 + 3 = 8。'},
        {'content': 'x = input()\nprint(x + 10)\n輸入 5 後，會發生什麼錯誤？\n填入錯誤類型名稱。', 'correct_answer': 'TypeError', 'explanation': 'input() 回傳字串，字串不能和整數直接相加，引發 TypeError。'},
        {'content': 'x = input()\nprint(x * 2)\n輸入「3」後輸出是什麼？\n（x 是字串，未做型別轉換）', 'correct_answer': '33', 'explanation': '字串 × 整數 表示重複，"3" * 2 = "33"。'},
        {'content': 'x = int(input())\n輸入「hello」後，會發生什麼錯誤？\n填入錯誤類型名稱。', 'correct_answer': 'ValueError', 'explanation': 'int() 無法將非數字字串轉換，引發 ValueError。'},
        {'content': 'input(\"請輸入年齡：\") 括號裡的「請輸入年齡：」有什麼用途？\n（填入最關鍵的兩個字）', 'correct_answer': '提示文字', 'explanation': '括號內的字串是提示文字，顯示在輸入框前告訴使用者要輸入什麼。'},
        {'content': 'area = 3.14 ___ r ** 2\n計算圓面積，填入運算符號。', 'correct_answer': '*', 'explanation': '圓面積 = π × r²，* 是乘法符號。'},
        {'content': 'x = int(input())\nprint(x ** 2)\n輸入 7 後，輸出是什麼？', 'correct_answer': '49', 'explanation': '7 ** 2 = 7 × 7 = 49，** 是次方運算符號。'},
    ],
    # Unit 3: if 條件判斷
    [
        {'content': 'if x > 0:\n    print(\"正數\")\n___:\n    print(\"非正數\")\n填入讓「其他情況」執行的關鍵字。', 'correct_answer': 'else', 'explanation': 'else 處理所有 if 條件不成立的情況。'},
        {'content': 'if 條件式後面必須加什麼符號才不會出現 SyntaxError？\n填入符號。', 'correct_answer': ':', 'explanation': 'Python 的 if 行尾必須加冒號 :，缺少會引發 SyntaxError。'},
        {'content': 'if score ___ 60:\n    print(\"及格\")\n讓「大於等於 60 分」的條件成立。\n填入比較運算子。', 'correct_answer': '>=', 'explanation': '>= 是「大於等於」，60 >= 60 成立，59 >= 60 不成立。'},
        {'content': 'if x % 2 ___ 0:\n    print(\"偶數\")\n讓「x 是偶數」的條件成立。\n填入「等於」的比較運算子。', 'correct_answer': '==', 'explanation': '== 是比較運算子（判斷相等），= 是賦值，兩者不同。'},
        {'content': 'if True:\nprint(\"Hello\")\n這段程式有什麼錯誤？\n（填入錯誤原因）', 'correct_answer': '缺少縮排', 'explanation': 'if 區塊內的程式碼必須縮排，缺少縮排會引發 IndentationError。'},
        {'content': 'x = 7\nif x > 10:\n    print(\"大\")\nelse:\n    print(\"小\")\n輸出是什麼？', 'correct_answer': '小', 'explanation': '7 不大於 10，條件為 False，執行 else 印出「小」。'},
        {'content': 'score = 60\nif score >= 60:  這個條件是 True 還是 False？', 'correct_answer': 'True', 'explanation': '>= 是大於等於，60 >= 60 成立，結果為 True。'},
        {'content': '比較兩個值是否相等，應該用 = 還是 ==？\n（填入正確的運算子）', 'correct_answer': '==', 'explanation': '= 是賦值運算子，== 才是比較兩值是否相等的運算子。'},
        {'content': 'x = 3\nif x > 5:\n    print(\"A\")\nif x > 1:\n    print(\"B\")\nx = 3 時輸出是什麼？', 'correct_answer': 'B', 'explanation': 'x=3：第一個 if（3>5）為 False；第二個 if（3>1）為 True，印出 B。'},
        {'content': 'ans = \"Y\"\nif ans ___ \"Y\":\n    print(\"繼續\")\n填入字串比較的運算子。', 'correct_answer': '==', 'explanation': '字串比較也使用 ==，判斷兩個字串內容是否完全相同。'},
    ],
    # Unit 4: 多條件 if
    [
        {'content': 'if score >= 90:\n    print(\"A\")\n___ score >= 80:\n    print(\"B\")\n填入「否則如果」的關鍵字。', 'correct_answer': 'elif', 'explanation': 'elif 是 else if 的縮寫，用於串接多個條件分支。'},
        {'content': 'elif 是哪兩個英文關鍵字的縮寫？\n（中間有空格）', 'correct_answer': 'else if', 'explanation': 'elif 是 else if 的縮寫，讓程式碼更簡潔。'},
        {'content': 'else 區塊在什麼條件下執行？\n（填入中文說明）', 'correct_answer': '所有 if 和 elif 條件都不成立時', 'explanation': 'else 是最後的預設分支，只有前面所有條件都不成立時才執行。'},
        {'content': 'score = 72\nif score >= 90:\n    print(\"A\")\nelif score >= 80:\n    print(\"B\")\nelif score >= 70:\n    print(\"C\")\nelse:\n    print(\"F\")\n輸出是什麼？', 'correct_answer': 'C', 'explanation': '72 不符合 >=90、>=80，但符合 >=70，輸出 C。'},
        {'content': 'score = 45\nif score >= 90:\n    print(\"A\")\nelif score >= 60:\n    print(\"B\")\nelse:\n    print(\"F\")\n輸出是什麼？', 'correct_answer': 'F', 'explanation': '45 不符合 >=90 也不符合 >=60，執行 else 印出 F。'},
        {'content': 'a = 5\nb = 5\nif a > b:\n    print(\"a 大\")\nelif a < b:\n    print(\"b 大\")\nelse:\n    print(\"相等\")\n輸出是什麼？', 'correct_answer': '相等', 'explanation': 'a == b，兩個條件都不成立，執行 else 印出「相等」。'},
        {'content': 'if/elif/else 結構中，找到第一個符合的條件後，後面的 elif 還會繼續判斷嗎？\n（填「會」或「不會」）', 'correct_answer': '不會', 'explanation': '程式找到第一個符合的條件就執行，然後跳過整個 if-elif-else 結構。'},
        {'content': '一個 if 語法可以有幾個 elif？\n（填入中文說明）', 'correct_answer': '沒有限制', 'explanation': 'Python 的 elif 數量沒有限制，可根據需求加入多個分支。'},
        {'content': 'bmi = 22.5\nif bmi < 18.5:\n    print(\"過輕\")\nelif bmi < 25:\n    print(\"正常\")\nelif bmi < 30:\n    print(\"過重\")\nelse:\n    print(\"肥胖\")\n輸出是什麼？', 'correct_answer': '正常', 'explanation': '22.5 不小於 18.5，但小於 25，符合第二個 elif，印出「正常」。'},
        {'content': 'score = 95\nif score >= 60:\n    print(\"D\")\nelif score >= 90:\n    print(\"A\")\n輸出是什麼？（注意條件順序！）', 'correct_answer': 'D', 'explanation': '95 >= 60 成立，立刻印出 D，不再檢查後面的 elif。條件順序很重要！'},
    ],
    # Unit 5: list 串列
    [
        {'content': 'nums = [10, 20, 30, 40]\nprint(nums[___])\n讓輸出 20，填入索引值。', 'correct_answer': '1', 'explanation': '串列索引從 0 開始，nums[1] = 20。'},
        {'content': 'Python 串列的索引從哪個數字開始？', 'correct_answer': '0', 'explanation': '所有 Python 序列的索引都從 0 開始，第一個元素是 [0]。'},
        {'content': 'fruits = [\"蘋果\", \"香蕉\", \"西瓜\"]\nprint(fruits[___])\n取最後一個元素「西瓜」，填入負索引。', 'correct_answer': '-1', 'explanation': '負索引 -1 代表最後一個元素。'},
        {'content': 'nums = [1, 2, 3]\nnums.___(4)\nprint(nums)\n在串列末尾加入 4，填入方法名稱。', 'correct_answer': 'append', 'explanation': 'append() 在串列末尾新增一個元素。'},
        {'content': 'print(len([10, 20, 30, 40, 50]))\n輸出是什麼？', 'correct_answer': '5', 'explanation': 'len() 回傳串列的元素個數，這個串列有 5 個元素。'},
        {'content': 'nums = [5, 3, 8, 1]\nnums.___()\nprint(nums)\n讓串列由小到大排序（原地修改），填入方法名稱。', 'correct_answer': 'sort', 'explanation': 'sort() 將串列原地由小到大排序，不回傳新串列。'},
        {'content': 'nums = [10, 20, 30, 40, 50]\nprint(nums[___])\n取第三個元素 30，填入索引。', 'correct_answer': '2', 'explanation': '第三個元素的索引是 2（從 0 開始：0→10, 1→20, 2→30）。'},
        {'content': 'nums = [1, 2, 3]\nnums[1] = 99\nprint(nums)\n輸出是什麼？', 'correct_answer': '[1, 99, 3]', 'explanation': 'nums[1] = 99 將索引 1 的元素從 2 修改為 99。'},
        {'content': 'nums = [10, 20, 30, 40, 50]\nprint(nums[1:4])\n輸出是什麼？（切片取索引 1 到 3）', 'correct_answer': '[20, 30, 40]', 'explanation': '[1:4] 取索引 1、2、3 的元素，即 20、30、40，不包含索引 4。'},
        {'content': 'nums = [3, 1, 4, 1, 5]\nprint(nums.count(1))\n輸出是什麼？count() 計算元素出現次數。', 'correct_answer': '2', 'explanation': '1 在串列中出現兩次（索引 1 和索引 3）。'},
    ],
    # Unit 6: range 數列
    [
        {'content': 'print(list(range(5)))\n輸出是什麼？', 'correct_answer': '[0, 1, 2, 3, 4]', 'explanation': 'range(5) 從 0 開始到 4（不含 5），共 5 個數。'},
        {'content': 'print(list(range(1, 6)))\n輸出是什麼？', 'correct_answer': '[1, 2, 3, 4, 5]', 'explanation': 'range(1, 6) 從 1 開始到 5（不含 6），共 5 個數。'},
        {'content': 'print(list(range(0, 10, 2)))\n輸出是什麼？', 'correct_answer': '[0, 2, 4, 6, 8]', 'explanation': 'range(0, 10, 2) 從 0 開始，步長 2，到 8（不含 10）。'},
        {'content': 'print(list(range(5, 0, -1)))\n輸出是什麼？', 'correct_answer': '[5, 4, 3, 2, 1]', 'explanation': 'step=-1 產生遞減數列，從 5 到 1（不含 0）。'},
        {'content': 'print(len(range(1, 101)))\n輸出是什麼？', 'correct_answer': '100', 'explanation': 'range(1, 101) 包含 1 到 100，共 100 個元素。'},
        {'content': 'print(sum(range(1, 11)))\n1 加到 10 的總和是什麼？', 'correct_answer': '55', 'explanation': '1+2+3+...+10 = 55，sum() 計算 range 中所有元素的總和。'},
        {'content': 'print(50 in range(10))\n輸出是什麼？', 'correct_answer': 'False', 'explanation': 'range(10) 包含 0~9，50 不在其中，in 回傳 False。'},
        {'content': 'print(list(range(2, 11, 2))[-1])\n輸出是什麼？', 'correct_answer': '10', 'explanation': 'range(2, 11, 2) = [2,4,6,8,10]，[-1] 取最後一個元素 10。'},
        {'content': 'range(___, ___) 產生 [3, 4, 5]。\n填入起始值和結束值（用逗號分隔）。', 'correct_answer': '3, 6', 'explanation': 'range(3, 6) 從 3 開始到 5（不含 6），產生 [3, 4, 5]。'},
        {'content': 'print(list(range(10, 0, -3)))\n輸出是什麼？', 'correct_answer': '[10, 7, 4, 1]', 'explanation': '從 10 開始每次 -3：10, 7, 4, 1（下一個 -2 不在範圍內）。'},
    ],
    # Unit 7: for 迴圈
    [
        {'content': 'total = 0\nfor i in range(1, 6):\n    total += i\nprint(total)\n1+2+3+4+5 的總和是什麼？', 'correct_answer': '15', 'explanation': '1+2+3+4+5 = 15，for 迴圈搭配累加器計算總和。'},
        {'content': 'total = 0\nfor i in range(1, 11):\n    total += i\nprint(total)\n1 加到 10 的總和是什麼？', 'correct_answer': '55', 'explanation': '1+2+3+...+10 = 55。'},
        {'content': 'for i in range(3):\n    print(i, end=\" \")\n輸出是什麼？', 'correct_answer': '0 1 2 ', 'explanation': 'range(3) 產生 0, 1, 2，end=" " 讓每個數字後面加空格而不換行。'},
        {'content': 'result = 1\nfor i in range(1, 4):\n    result *= i\nprint(result)\n3 的階乘（1×2×3）是什麼？', 'correct_answer': '6', 'explanation': '1×2×3 = 6，*= 是乘法累積的寫法。'},
        {'content': 'count = 0\nfor x in range(1, 11):\n    if x % 2 == 0:\n        count += 1\nprint(count)\n1 到 10 中有幾個偶數？', 'correct_answer': '5', 'explanation': '2, 4, 6, 8, 10 共 5 個偶數。'},
        {'content': 'for i in range(5):\n    if i == 3:\n        break\n    print(i, end=\" \")\n輸出是什麼？', 'correct_answer': '0 1 2 ', 'explanation': 'i=0,1,2 時印出，i=3 時執行 break 離開迴圈，不再印出 3。'},
        {'content': 'fruits = [\"蘋果\", \"香蕉\", \"西瓜\"]\nfor fruit in fruits:\n    print(fruit)\n迴圈共執行幾次？', 'correct_answer': '3', 'explanation': '串列有 3 個元素，for 迴圈對每個元素執行一次，共 3 次。'},
        {'content': 'total = 0\nfor i in range(1, 6):\n    if i == 3:\n        continue\n    total += i\nprint(total)\n跳過 3，其餘 1+2+4+5 的總和是什麼？', 'correct_answer': '12', 'explanation': 'continue 跳過 i=3 的那次，累加 1+2+4+5 = 12。'},
        {'content': 'nums = [4, 7, 2, 9, 1]\nmax_val = nums[0]\nfor n in nums:\n    if n > max_val:\n        max_val = n\nprint(max_val)\n輸出是什麼？', 'correct_answer': '9', 'explanation': '遍歷串列找最大值，最終 max_val = 9。'},
        {'content': 'for i in range(2, 6):\n    print(i, end=\" \")\n輸出是什麼？', 'correct_answer': '2 3 4 5 ', 'explanation': 'range(2, 6) 產生 2, 3, 4, 5（不含 6），end=" " 讓數字之間有空格。'},
    ],
    # Unit 8: 迴圈應用
    [
        {'content': 'i = 1\ntotal = 0\nwhile i <= 5:\n    total += i\n    i += 1\nprint(total)\n1+2+3+4+5 的總和是什麼？', 'correct_answer': '15', 'explanation': 'while 迴圈從 i=1 到 i=5，累加 1+2+3+4+5 = 15。'},
        {'content': 'while True: 的迴圈靠什麼陳述句跳出？\n填入關鍵字。', 'correct_answer': 'break', 'explanation': 'break 立即終止最內層迴圈，是跳出 while True 的唯一方式。'},
        {'content': 'result = 1\nfor i in range(1, 6):\n    result *= i\nprint(result)\n5 的階乘（1×2×3×4×5）是什麼？', 'correct_answer': '120', 'explanation': '1×2×3×4×5 = 120。'},
        {'content': 'total = 0\nfor i in range(1, 101):\n    if i % 2 == 0:\n        total += i\nprint(total)\n1 到 100 所有偶數的總和是什麼？', 'correct_answer': '2550', 'explanation': '2+4+6+...+100 = 50×51 = 2550。'},
        {'content': 'for i in range(3):\n    for j in range(3):\n        pass\n內層的 pass 共執行幾次？', 'correct_answer': '9', 'explanation': '外層迴圈執行 3 次，每次內層也執行 3 次，共 3×3 = 9 次。'},
        {'content': 'i = 10\nwhile i > 0:\n    print(i, end=\" \")\n    i -= 3\n輸出是什麼？', 'correct_answer': '10 7 4 1 ', 'explanation': 'i 依序為 10, 7, 4, 1（下一次 i=-2，不滿足 i>0，停止）。'},
        {'content': 'total = 0\nfor i in range(1, 6):\n    if i % 2 != 0:\n        total += i\nprint(total)\n1 到 5 所有奇數（1,3,5）的總和是什麼？', 'correct_answer': '9', 'explanation': '1+3+5 = 9，i % 2 != 0 篩選奇數。'},
        {'content': 'n = 5\nfor i in range(1, n+1):\n    print(\"*\" * i)\n最後一行（i=5 時）輸出幾個星號？', 'correct_answer': '5', 'explanation': '"*" * 5 產生 5 個星號 "*****"。'},
        {'content': 'nums = [3, 1, 4, 1, 5, 9, 2, 6]\nprint(sum(nums) / len(nums))\n輸出的平均值是多少？', 'correct_answer': '3.875', 'explanation': '(3+1+4+1+5+9+2+6)/8 = 31/8 = 3.875。'},
        {'content': '依序輸入 5, 3, 8, 0（輸入 0 代表結束），以下程式輸出是什麼？\ntotal = 0\nwhile True:\n    n = int(input())\n    if n == 0:\n        break\n    total += n\nprint(total)', 'correct_answer': '16', 'explanation': '5+3+8=16，輸入 0 時 break 離開迴圈，輸出 16。'},
    ],
]

# ── Level 3 程式設計題（每單元 10 題，應用與 Level 1/2 相同的核心概念）────
CODING_QUESTIONS = [
    # Unit 1: print 輸出
    [
        {'content': '撰寫程式，分別用兩個 print() 顯示你的名字和就讀學校，各自一行。', 'correct_answer': '', 'explanation': '每個 print() 執行後自動換行，兩個 print() 產生兩行輸出。'},
        {'content': '撰寫程式，計算並顯示 123 + 456 的結果。\n輸出格式：「123 + 456 = 579」', 'correct_answer': '', 'explanation': 'print("123 + 456 =", 123 + 456) 可同時顯示文字和計算結果。'},
        {'content': '撰寫程式，用一個 print() 同時顯示長、寬和面積。\n長=8、寬=5，輸出格式：「長=8 寬=5 面積=40」', 'correct_answer': '', 'explanation': 'print("長=8", "寬=5", "面積=", 8*5) 或類似方式。'},
        {'content': '撰寫程式，用 print() 輸出以下星號圖案（星號數量由上到下遞增）：\n*\n**\n***\n****\n*****', 'correct_answer': '', 'explanation': '用 5 個 print() 分別輸出 "*", "**", "***", "****", "*****"。'},
        {'content': '撰寫程式，計算並顯示 5 的平方和 5 的立方。\n輸出格式：「5 的平方 = 25，5 的立方 = 125」', 'correct_answer': '', 'explanation': '5 ** 2 = 25，5 ** 3 = 125，用 print() 顯示結果。'},
        {'content': '撰寫程式，顯示 1 × 1 到 1 × 5 的乘法算式，每行一個。\n格式：「1 × 1 = 1」、「1 × 2 = 2」⋯', 'correct_answer': '', 'explanation': '用 5 個 print() 分別輸出每個算式。'},
        {'content': '撰寫程式，計算並顯示 100 ÷ 7 的商和餘數。\n格式：「100 ÷ 7 的商 = 14，餘數 = 2」', 'correct_answer': '', 'explanation': '// 是整除運算符，% 是取餘數運算符。'},
        {'content': '撰寫程式，用 print() 輸出以下名片格式：\n====================\n姓名：王小明\n學號：B12345678\n====================', 'correct_answer': '', 'explanation': '用多個 print() 分別輸出每行，"=" * 20 可產生分隔線。'},
        {'content': '撰寫程式，分別計算並顯示邊長 6 的正方形周長和面積。\n格式：「周長 = 24，面積 = 36」', 'correct_answer': '', 'explanation': '周長 = 4 × 邊長，面積 = 邊長²，用 print() 顯示。'},
        {'content': '撰寫程式，顯示以下三行，每行用 print() 輸出：\n「Python 很有趣」\n「程式設計不難」\n「多練習就會了」', 'correct_answer': '', 'explanation': '三個 print() 分別輸出三行文字。'},
    ],
    # Unit 2: input 輸入與運算
    [
        {'content': '撰寫程式，讓使用者輸入兩個整數，計算並顯示它們的和。\n格式：「X + Y = Z」', 'correct_answer': '', 'explanation': '用 int(input()) 取得整數，print(a, "+", b, "=", a+b) 輸出。'},
        {'content': '撰寫程式，讓使用者輸入名字，顯示「您好，XXX！」\n（XXX 替換成使用者輸入的名字）', 'correct_answer': '', 'explanation': 'name = input("請輸入名字：")；print("您好，" + name + "！")'},
        {'content': '撰寫程式，讓使用者輸入圓的半徑，計算並顯示圓的面積。\nπ 使用 3.14159，面積 = π × r²', 'correct_answer': '', 'explanation': 'r = float(input())；area = 3.14159 * r ** 2；print(area)'},
        {'content': '撰寫程式，讓使用者輸入攝氏溫度，換算並顯示對應的華氏溫度。\n公式：F = C × 9/5 + 32', 'correct_answer': '', 'explanation': 'c = float(input())；f = c * 9/5 + 32；print(f)'},
        {'content': '撰寫程式，讓使用者輸入一個整數，顯示它的平方和立方。\n格式：「N 的平方 = A，立方 = B」', 'correct_answer': '', 'explanation': 'n = int(input())；print(n, "的平方 =", n**2, "，立方 =", n**3)'},
        {'content': '撰寫程式，讓使用者輸入秒數，換算並顯示「X 分 Y 秒」格式。\n例如輸入 125，顯示「2 分 5 秒」', 'correct_answer': '', 'explanation': 'sec = int(input())；m = sec // 60；s = sec % 60；print(m, "分", s, "秒")'},
        {'content': '撰寫程式，讓使用者輸入三角形的底和高，計算並顯示面積。\n面積 = 底 × 高 ÷ 2', 'correct_answer': '', 'explanation': 'base = float(input())；height = float(input())；area = base * height / 2；print(area)'},
        {'content': '撰寫程式，讓使用者輸入一個整數，計算並顯示它除以 7 的商和餘數。\n格式：「商 = X，餘數 = Y」', 'correct_answer': '', 'explanation': 'n = int(input())；print("商 =", n//7, "，餘數 =", n%7)'},
        {'content': '撰寫程式，讓使用者輸入身高（公分）和體重（公斤），計算並顯示 BMI 值。\nBMI = 體重 / (身高/100)²', 'correct_answer': '', 'explanation': 'h = float(input())/100；w = float(input())；bmi = w / h**2；print(bmi)'},
        {'content': '撰寫程式，讓使用者輸入兩個整數，分別顯示它們的和、差、積、商（整除）。', 'correct_answer': '', 'explanation': 'a = int(input())；b = int(input())；分別 print 加減乘整除的結果。'},
    ],
    # Unit 3: if 條件判斷
    [
        {'content': '撰寫程式，讓使用者輸入一個整數，判斷並顯示它是「正數」、「負數」還是「零」。', 'correct_answer': '', 'explanation': '用 if x > 0 / elif x < 0 / else 三個分支判斷。'},
        {'content': '撰寫程式，讓使用者輸入成績（0-100），判斷並顯示是否及格。\n60 分以上顯示「及格」，否則顯示「不及格」', 'correct_answer': '', 'explanation': 'score = int(input())；if score >= 60: print("及格") else: print("不及格")'},
        {'content': '撰寫程式，讓使用者輸入一個整數，判斷並顯示是「奇數」還是「偶數」。', 'correct_answer': '', 'explanation': 'if n % 2 == 0: print("偶數") else: print("奇數")'},
        {'content': '撰寫程式，讓使用者輸入兩個整數，判斷並顯示哪個比較大（或顯示「兩數相等」）。', 'correct_answer': '', 'explanation': 'if a > b / elif a < b / else 三個分支。'},
        {'content': '撰寫程式，讓使用者輸入年份，判斷並顯示是否為閏年。\n閏年條件：能被 4 整除且不被 100 整除，或能被 400 整除。', 'correct_answer': '', 'explanation': 'if (year%4==0 and year%100!=0) or year%400==0: print("閏年") else: print("非閏年")'},
        {'content': '撰寫程式，讓使用者輸入三個整數，找出並顯示最大值。', 'correct_answer': '', 'explanation': '用 if/elif/else 比較三個數，找出最大值。'},
        {'content': '撰寫程式，讓使用者輸入體溫（攝氏），判斷並顯示狀態：\n低於 36 → 「低體溫」\n36 到 37.5 → 「正常」\n高於 37.5 → 「發燒」', 'correct_answer': '', 'explanation': 'temp = float(input())；if temp < 36 / elif temp <= 37.5 / else 三個分支。'},
        {'content': '撰寫程式，讓使用者輸入一個整數，判斷是否在 1 到 100 之間（含）。\n顯示「在範圍內」或「超出範圍」', 'correct_answer': '', 'explanation': 'if 1 <= n <= 100: print("在範圍內") else: print("超出範圍")'},
        {'content': '撰寫程式，讓使用者輸入月份（1-12），判斷並顯示是哪個季節。\n3-5 月→春，6-8 月→夏，9-11 月→秋，12,1,2 月→冬', 'correct_answer': '', 'explanation': '用 if/elif/else 判斷月份範圍，或用 in [3,4,5] 判斷。'},
        {'content': '撰寫程式，讓使用者輸入一個正整數，判斷能否被 2 整除，並顯示結果。\n能整除顯示「X 能被 2 整除」，否則顯示「X 不能被 2 整除」', 'correct_answer': '', 'explanation': 'if n % 2 == 0: print(n, "能被 2 整除") else: print(n, "不能被 2 整除")'},
    ],
    # Unit 4: 多條件 if
    [
        {'content': '撰寫程式，讓使用者輸入成績（0-100），用 if/elif/else 顯示等第：\n90 以上→A，80-89→B，70-79→C，60-69→D，60 以下→F', 'correct_answer': '', 'explanation': '依序用 if >= 90 / elif >= 80 / elif >= 70 / elif >= 60 / else 判斷。'},
        {'content': '撰寫程式，讓使用者輸入 BMI 值，判斷並顯示體重狀態：\nBMI < 18.5→過輕，18.5-24→正常，24-27→過重，27 以上→肥胖', 'correct_answer': '', 'explanation': '用 if/elif/else 依序判斷各 BMI 範圍。'},
        {'content': '撰寫程式，讓使用者輸入月份（1-12），顯示該月有幾天。\n（2 月固定 28 天，不考慮閏年）', 'correct_answer': '', 'explanation': '31 天：1,3,5,7,8,10,12；30 天：4,6,9,11；28 天：2。'},
        {'content': '撰寫程式，讓使用者輸入 1-7 的數字，顯示對應的星期名稱。\n1=星期一，2=星期二，⋯，7=星期日', 'correct_answer': '', 'explanation': '用 if/elif 依序判斷 1 到 7，else 顯示「輸入錯誤」。'},
        {'content': '撰寫程式，讓使用者輸入年齡，判斷並顯示身份：\n0-12→兒童，13-17→青少年，18-64→成人，65 以上→長者', 'correct_answer': '', 'explanation': 'if age <= 12 / elif age <= 17 / elif age <= 64 / else 四個分支。'},
        {'content': '撰寫程式，讓使用者輸入一個整數，判斷是哪個範圍：\n個位數（1-9）、二位數（10-99）、三位數（100-999）、更大的數', 'correct_answer': '', 'explanation': 'if 1 <= n <= 9 / elif n <= 99 / elif n <= 999 / else 判斷各範圍。'},
        {'content': '撰寫程式，讓使用者輸入三科成績，計算平均，並根據平均顯示等第（同第一題的標準）。', 'correct_answer': '', 'explanation': '用 int(input()) 取得三科，計算 (a+b+c)/3，再用 if/elif/else 判斷。'},
        {'content': '撰寫程式，讓使用者輸入時速（公里/小時），顯示超速等級：\n60 以下→正常，60-80→注意，80-100→超速，100 以上→嚴重超速', 'correct_answer': '', 'explanation': 'speed = int(input())；if speed < 60 / elif speed <= 80 / elif speed <= 100 / else'},
        {'content': '撰寫程式，讓使用者輸入一個正整數，判斷是否為 2 的倍數、3 的倍數、兩者都是，或兩者都不是。', 'correct_answer': '', 'explanation': 'if n%2==0 and n%3==0 / elif n%2==0 / elif n%3==0 / else 四個分支。'},
        {'content': '撰寫程式，讓使用者輸入兩個整數 a 和 b，用 if/elif/else 判斷並顯示大小關係：\n「a 大於 b」、「a 小於 b」或「a 等於 b」', 'correct_answer': '', 'explanation': 'if a > b / elif a < b / else 三個分支。'},
    ],
    # Unit 5: list 串列
    [
        {'content': '撰寫程式，建立串列 [10, 5, 8, 3, 7]，輸出最大值、最小值和所有元素的總和。', 'correct_answer': '', 'explanation': '使用 max()、min()、sum() 函式直接計算。'},
        {'content': '撰寫程式，建立一個空串列，使用 append() 依序加入 1 到 5，最後輸出整個串列。', 'correct_answer': '', 'explanation': '先建立 nums = []，再用 append() 或迴圈加入元素。'},
        {'content': '撰寫程式，建立串列 [88, 45, 72, 95, 60, 55]，篩選出及格（≥60）的成績並輸出。', 'correct_answer': '', 'explanation': '用 for 迴圈逐一比較，及格的加入新串列後輸出。'},
        {'content': '撰寫程式，建立串列 [5, 3, 8, 1, 9, 2]，使用 sort() 排序後輸出。', 'correct_answer': '', 'explanation': 'nums.sort() 原地排序，然後 print(nums)。'},
        {'content': '撰寫程式，建立串列 [1, 2, 3, 4, 5]，輸出：索引 1 的元素、最後一個元素（用負索引）、切片 [1:4]。', 'correct_answer': '', 'explanation': 'nums[1]、nums[-1]、nums[1:4] 分別輸出。'},
        {'content': '撰寫程式，建立兩個串列 [1, 2, 3] 和 [4, 5, 6]，用 + 合併成新串列並輸出。', 'correct_answer': '', 'explanation': 'combined = [1,2,3] + [4,5,6]；print(combined)'},
        {'content': '撰寫程式，建立串列 [4, 7, 2, 9, 1, 5]，用 for 迴圈找出最大值（不可使用 max()）。', 'correct_answer': '', 'explanation': '初始化 max_val = nums[0]，迴圈比較每個元素，更新 max_val。'},
        {'content': '撰寫程式，建立串列 [10, 20, 30, 40, 50]，修改索引 2 的元素為 99，再輸出整個串列。', 'correct_answer': '', 'explanation': 'nums[2] = 99 修改第三個元素，然後 print(nums)。'},
        {'content': '撰寫程式，建立串列 [3, 1, 4, 1, 5, 9, 2, 6, 5]，計算元素 5 出現幾次，並輸出結果。', 'correct_answer': '', 'explanation': 'nums.count(5) 或用 for 迴圈計數。'},
        {'content': '撰寫程式，建立串列 [1, 2, 3, 4, 5]，計算並輸出所有元素的平均值。', 'correct_answer': '', 'explanation': 'average = sum(nums) / len(nums)；print(average)'},
    ],
    # Unit 6: range 數列
    [
        {'content': '撰寫程式，使用 range() 輸出 1 到 10 的所有整數，每個數字用空格分隔在同一行。', 'correct_answer': '', 'explanation': 'for i in range(1, 11): print(i, end=" ")'},
        {'content': '撰寫程式，使用 sum(range()) 計算 1 加到 100 的總和，並顯示結果。', 'correct_answer': '', 'explanation': 'print(sum(range(1, 101)))  結果為 5050。'},
        {'content': '撰寫程式，使用 range(0, 10, 2) 搭配迴圈輸出 0 到 8 的所有偶數，每個用空格分隔。', 'correct_answer': '', 'explanation': 'for i in range(0, 10, 2): print(i, end=" ")'},
        {'content': '撰寫程式，使用 range(10, 0, -1) 搭配迴圈輸出 10 到 1 的倒數，每個用空格分隔。', 'correct_answer': '', 'explanation': 'for i in range(10, 0, -1): print(i, end=" ")'},
        {'content': '撰寫程式，使用 range() 輸出 1 到 30 中所有 3 的倍數，每個用空格分隔。', 'correct_answer': '', 'explanation': 'for i in range(3, 31, 3): print(i, end=" ")'},
        {'content': '撰寫程式，使用 list(range()) 建立串列 [1, 3, 5, 7, 9]（1 到 9 的奇數），並輸出。', 'correct_answer': '', 'explanation': 'print(list(range(1, 10, 2)))'},
        {'content': '撰寫程式，讓使用者輸入 n，使用 sum(range()) 計算 1 到 n 的總和並顯示。', 'correct_answer': '', 'explanation': 'n = int(input())；print(sum(range(1, n+1)))'},
        {'content': '撰寫程式，使用 range() 計算 1 到 10 中所有奇數的總和並顯示。', 'correct_answer': '', 'explanation': 'print(sum(range(1, 11, 2)))  結果為 25（1+3+5+7+9）。'},
        {'content': '撰寫程式，使用 range(5, 0, -1) 搭配迴圈，輸出以下倒三角形圖案：\n*****\n****\n***\n**\n*', 'correct_answer': '', 'explanation': 'for i in range(5, 0, -1): print("*" * i)'},
        {'content': '撰寫程式，使用 range() 計算 1 到 100 中所有 5 的倍數的個數，並顯示結果。', 'correct_answer': '', 'explanation': 'count = 0；for i in range(1, 101): if i % 5 == 0: count += 1；print(count)'},
    ],
    # Unit 7: for 迴圈
    [
        {'content': '撰寫程式，使用 for 迴圈輸出串列 [10, 20, 30, 40, 50] 中的每個元素，每個一行。', 'correct_answer': '', 'explanation': 'for x in [10,20,30,40,50]: print(x)'},
        {'content': '撰寫程式，使用 for 迴圈計算 1 到 5 的乘積（1×2×3×4×5）並顯示結果。', 'correct_answer': '', 'explanation': 'result = 1；for i in range(1, 6): result *= i；print(result)  結果 120。'},
        {'content': '撰寫程式，使用 for 迴圈輸出 1 到 10，但跳過 5（使用 continue）。', 'correct_answer': '', 'explanation': 'for i in range(1, 11): if i == 5: continue；print(i)'},
        {'content': '撰寫程式，使用 for 迴圈計算串列 [3, 1, 4, 1, 5, 9, 2, 6] 中所有元素的總和。', 'correct_answer': '', 'explanation': 'total = 0；for n in nums: total += n；print(total)  結果 31。'},
        {'content': '撰寫程式，使用 for 迴圈計算並顯示 1! 到 5! （1 到 5 的階乘）。\n格式：「1! = 1」、「2! = 2」⋯', 'correct_answer': '', 'explanation': '外層迴圈 n=1~5，內層迴圈計算 n! = 1×2×⋯×n。'},
        {'content': '撰寫程式，使用 for 迴圈找出 1 到 50 中第一個能被 7 整除且大於 20 的數，顯示後停止（使用 break）。', 'correct_answer': '', 'explanation': 'for i in range(1, 51): if i % 7 == 0 and i > 20: print(i); break  答案 21。'},
        {'content': '撰寫程式，使用 for 迴圈輸出字串 "Python" 中每個字元，每個一行。', 'correct_answer': '', 'explanation': 'for ch in "Python": print(ch)'},
        {'content': '撰寫程式，使用 for 迴圈找出串列 [4, 7, 2, 9, 1, 5] 的最大值，不可使用 max()。', 'correct_answer': '', 'explanation': 'max_val = nums[0]；for n in nums: if n > max_val: max_val = n；print(max_val)'},
        {'content': '撰寫程式，使用 for 迴圈輸出 3 × 1 到 3 × 5 的乘法算式。\n格式：「3 × 1 = 3」、「3 × 2 = 6」⋯', 'correct_answer': '', 'explanation': 'for i in range(1, 6): print("3 ×", i, "=", 3*i)'},
        {'content': '撰寫程式，使用 for 迴圈計算 1 到 10 中所有偶數的總和，並顯示結果。', 'correct_answer': '', 'explanation': 'total = 0；for i in range(1, 11): if i % 2 == 0: total += i；print(total)  結果 30。'},
    ],
    # Unit 8: 迴圈應用
    [
        {'content': '撰寫程式，使用 while 迴圈讓使用者持續輸入數字，輸入 0 時停止，最後顯示所有數字的總和。', 'correct_answer': '', 'explanation': 'total=0；while True: n=int(input())；if n==0: break；total+=n；print(total)'},
        {'content': '撰寫程式，使用 while 迴圈顯示 1 到 10，每個數字一行。', 'correct_answer': '', 'explanation': 'i=1；while i<=10: print(i)；i+=1'},
        {'content': '撰寫程式，使用巢狀 for 迴圈輸出 1 到 3 的乘法表（1×1=1 到 3×3=9），每行一個算式。', 'correct_answer': '', 'explanation': 'for i in range(1,4): for j in range(1,4): print(f"{i}×{j}={i*j}")'},
        {'content': '撰寫程式，讓使用者猜一個數字（答案固定為 42），顯示「太大」、「太小」或「猜對了！」，猜對時顯示共猜了幾次。', 'correct_answer': '', 'explanation': 'count=0；while True: guess=int(input())；count+=1；if/elif/else 判斷，猜對時 break 並顯示次數。'},
        {'content': '撰寫程式，使用巢狀迴圈輸出以下圖案：\n* \n* * \n* * * \n* * * * \n* * * * *', 'correct_answer': '', 'explanation': 'for i in range(1,6): for j in range(i): print("*",end=" ")；print()'},
        {'content': '撰寫程式，使用 while 迴圈計算 1 到 100 中所有偶數的總和，並顯示結果。', 'correct_answer': '', 'explanation': 'i=1；total=0；while i<=100: if i%2==0: total+=i；i+=1；print(total)  結果 2550。'},
        {'content': '撰寫程式，讓使用者輸入 n，使用 for 迴圈輸出費波那契數列的前 n 項（0, 1, 1, 2, 3, 5, 8⋯）。', 'correct_answer': '', 'explanation': 'a,b=0,1；for _ in range(n): print(a,end=" ")；a,b=b,a+b'},
        {'content': '撰寫程式，使用巢狀迴圈計算並顯示 1 到 5 的階乘。\n格式：「1!=1」、「2!=2」、「3!=6」、「4!=24」、「5!=120」', 'correct_answer': '', 'explanation': 'for n in range(1,6): result=1；for i in range(1,n+1): result*=i；print(f"{n}!={result}")'},
        {'content': '撰寫程式，讓使用者輸入密碼（正確密碼為 1234），最多可嘗試 3 次，超過次數顯示「帳號鎖定」，正確時顯示「登入成功」。', 'correct_answer': '', 'explanation': 'for attempt in range(3): pwd=input()；if pwd=="1234": print("登入成功")；break；else: print("帳號鎖定")'},
        {'content': '撰寫程式，建立串列 [3, 1, 4, 1, 5, 9, 2, 6]，使用 for 迴圈同時找出最大值和最小值並顯示。', 'correct_answer': '', 'explanation': 'max_v=min_v=nums[0]；for n in nums: if n>max_v: max_v=n；elif n<min_v: min_v=n；print(max_v, min_v)'},
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
