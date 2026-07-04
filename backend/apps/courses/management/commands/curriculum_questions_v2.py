"""curriculum_questions_v2 — 混合題型題庫（選擇題＋程式填空題）。

設計原則（2026-07 題庫改版）：
- 三個等級都混合「選擇題＋程式填空題」，等級差異來自內容難度而非題型，
  學生無法從題型推斷自己的分級（配合不標籤化設計）。
- 題型比例：L1 = 70 選擇 + 30 填空、L2 = 50 + 50、L3 = 30 選擇 + 70 填空。
- 命題風格對標（皆為原創題，未抄錄原題）：
    L1 → ITS Python：概念辨識、術語、單行程式讀碼
    L2 → TQC+ Python 觀念題：多行程式追蹤、輸出預測、錯誤類型判斷
    L3 → TQC+ 實作題／全國技藝競賽術科（簡化）：情境式程式完成、多空格填空
- 每個題庫 100 題皆為獨立命題，不使用參數模板量產。
- 選擇題正解位置由 seed_data 以內容雜湊做確定性洗牌，避免固定在選項 A。
"""


def mc(content, correct, *distractors, explanation=''):
    """選擇題：第一個參數列表位置放正解，seed 時會洗牌。"""
    return {
        'type': 'multiple_choice',
        'content': content,
        'choices': [(correct, True), *[(d, False) for d in distractors]],
        'explanation': explanation or f'正確答案：{correct}',
    }


def fb(content, *answers, explanation=''):
    """程式填空題：內文以 __1__、__2__ 標記空格；list/tuple 代表同格多解。"""
    lines = []
    for answer in answers:
        if isinstance(answer, (list, tuple)):
            lines.append('|||'.join(answer))
        else:
            lines.append(answer)
    display = '；'.join(f'空格{i}: {line.split("|||")[0]}' for i, line in enumerate(lines, start=1))
    return {
        'type': 'fill_blank',
        'content': content,
        'correct_answer': '\n'.join(lines),
        'explanation': explanation or f'答案 — {display}',
    }


# ═══════════════════════════════════════════════════════════════════
# Unit 1（環境、變數、資料型態與 I/O）
# ═══════════════════════════════════════════════════════════════════

# ── U1 Level 1：70 選擇 + 30 填空（ITS 風格：概念辨識、單行讀碼）──
U1_L1 = [
    # print 與輸出（8）
    mc('print("Hi") 執行後螢幕顯示什麼？', 'Hi', '"Hi"', 'print(Hi)', '不會顯示任何東西'),
    mc('print(7 + 2) 的輸出是？', '9', '7 + 2', '72', '發生錯誤',
       explanation='括號內是數字運算式，print 會先算出結果 9 再輸出。'),
    mc('print("7 + 2") 的輸出是？', '7 + 2', '9', '72', '發生錯誤',
       explanation='加了引號就是字串，內容原樣輸出，不會計算。'),
    mc('print("A", "B") 的輸出是？', 'A B', 'AB', 'A,B', '"A" "B"',
       explanation='print 的多個引數預設以一個空格分隔。'),
    mc('下列哪一個是 Python 3 正確的輸出寫法？', 'print("OK")', 'print "OK"', 'Print("OK")', 'echo "OK"',
       explanation='Python 3 的 print 是函式，必須加括號；函式名稱區分大小寫。'),
    mc('print() 括號內不放任何東西，執行結果是？', '輸出一個空行', '發生錯誤', '輸出 None', '程式停止',
       explanation='不帶引數的 print() 只輸出換行符，畫面上是一個空行。'),
    mc('關於字串的引號，下列敘述何者正確？', "單引號 'Hi' 與雙引號 \"Hi\" 都可以",
       '只能用雙引號', '只能用單引號', '中文字串必須用單引號'),
    mc('print(10, 20, sep=",") 的輸出是？', '10,20', '10 , 20', '10 20', '1020',
       explanation='sep 參數指定多個值之間的分隔字串。'),

    # 變數與命名（8）
    mc('下列哪一個是合法的變數名稱？', 'total_1', '1total', 'my-score', 'for',
       explanation='變數不能以數字開頭、不能含連字號、不能用保留字 for。'),
    mc('為什麼 class = 3 會發生錯誤？', 'class 是 Python 保留字，不能當變數名稱',
       '變數不能等於數字', '缺少引號', '等號方向寫反了'),
    mc('x = 5 中「=」的意思是？', '把右邊的值指定給左邊的名稱', '判斷 x 是否等於 5',
       '宣告 x 的型態是整數', '輸出 5'),
    mc('score 與 Score 是同一個變數嗎？', '不是，Python 變數名稱區分大小寫',
       '是，大小寫視為相同', '只有第一個字母不分大小寫', '只有英文變數區分大小寫'),
    mc('執行 x = 3 之後再執行 x = 8，此時 x 的值是？', '8', '3', '11', '38',
       explanation='變數重新指定後，新值會覆蓋舊值。'),
    mc('使用尚未指定值的變數會發生什麼？', '引發 NameError', '自動當成 0',
       '自動當成空字串', '程式跳過該行'),
    mc('x, y = 1, 2 執行後，y 的值是？', '2', '1', '(1, 2)', '發生錯誤',
       explanation='多重指定會依序把 1 給 x、2 給 y。'),
    mc('依照 Python 命名慣例，一般變數名稱建議使用哪種寫法？', '全小寫，多個單字用底線連接（如 total_price）',
       '全大寫（如 TOTALPRICE）', '每個單字字首大寫（如 TotalPrice）', '任意混用大小寫'),

    # 資料型態（10）
    mc('type(5) 的結果是？', "<class 'int'>", "<class 'float'>", "<class 'str'>", "<class 'bool'>"),
    mc('type(3.0) 的結果是？', "<class 'float'>", "<class 'int'>", "<class 'str'>", "<class 'complex'>",
       explanation='有小數點就是浮點數，即使小數部分是 0。'),
    mc('type("5") 的結果是？', "<class 'str'>", "<class 'int'>", "<class 'float'>", "<class 'char'>",
       explanation='加了引號的 5 是字串，不是數字。'),
    mc('type(True) 的結果是？', "<class 'bool'>", "<class 'int'>", "<class 'str'>", "<class 'True'>"),
    mc('下列哪一個值的型態是 float？', '3.14', '314', '"3.14"', 'True'),
    mc('"True" 與 True 的差別是？', '"True" 是字串，True 是布林值', '兩者完全相同',
       '"True" 是布林值，True 是字串', '兩者都是字串'),
    mc('int("42") 的結果是？', '整數 42', '字串 "42"', '浮點數 42.0', '發生錯誤'),
    mc('float("3.5") 的結果是？', '3.5', '3', '"3.5"', '4',
       explanation='float() 把字串轉成浮點數。'),
    mc('str(99) 的結果是？', '字串 "99"', '整數 99', '浮點數 99.0', '發生錯誤'),
    mc('布林（bool）型態總共有幾種值？', '2 種：True 與 False', '1 種', '3 種：True、False、None', '不限數量'),

    # 運算子（10）
    mc('7 // 2 的結果是？', '3', '3.5', '4', '1',
       explanation='// 是整除，只取商的整數部分。'),
    mc('7 % 2 的結果是？', '1', '3', '3.5', '0',
       explanation='% 取除法的餘數，7 = 2×3 餘 1。'),
    mc('2 ** 3 的結果是？', '8', '6', '9', '5',
       explanation='** 是次方運算，2 的 3 次方 = 8。'),
    mc('7 / 2 的結果是？', '3.5', '3', '4', '3.0',
       explanation='/ 是一般除法，結果一定是浮點數。'),
    mc('想知道 17 除以 5 的餘數，應使用哪個運算子？', '%', '/', '//', '**'),
    mc('哪一個是 Python 的次方運算子？', '**', '^', 'pow', '××'),
    mc('10 - 4 * 2 的結果是？', '2', '12', '18', '-2',
       explanation='先乘除後加減：4×2=8，10-8=2。'),
    mc('(10 - 4) * 2 的結果是？', '12', '2', '18', '16',
       explanation='括號優先計算：10-4=6，6×2=12。'),
    mc('"a" + "b" 的結果是？', '"ab"', '"a b"', '發生錯誤', '"a+b"',
       explanation='+ 用在兩個字串時是串接。'),
    mc('"ab" * 3 的結果是？', '"ababab"', '"ab3"', '"aaabbb"', '發生錯誤',
       explanation='字串乘以整數 n 表示重複 n 次。'),

    # input 與轉型（8）
    mc('input() 回傳值的型態一定是？', 'str', 'int', 'float', '依輸入內容而定',
       explanation='不論輸入什麼，input() 一律回傳字串。'),
    mc('執行 x = input() 輸入 5，再執行 print(x + "0")，輸出是？', '50', '5', '5.0', '發生錯誤',
       explanation='x 是字串 "5"，和 "0" 串接成 "50"。'),
    mc('要把使用者輸入的整數拿來做加法，正確寫法是？', 'n = int(input())', 'n = input(int)',
       'n = input()', 'n = str(input())'),
    mc('int("abc") 會發生什麼？', '引發 ValueError', '得到 0', '得到 "abc"', '引發 TypeError',
       explanation='int() 無法轉換非數字內容的字串。'),
    mc('input("請輸入姓名：") 括號內的字串有什麼作用？', '顯示提示文字給使用者看',
       '設定輸入的預設值', '限制只能輸入文字', '設定變數名稱'),
    mc('要讀入含小數的身高（如 158.5），應使用？', 'float(input())', 'int(input())',
       'str(input())', 'input(float)'),
    mc('x = input() 輸入 3 之後，print(x * 2) 的輸出是？', '33', '6', '3 3', '發生錯誤',
       explanation='x 是字串 "3"，乘以 2 表示重複兩次。'),
    mc('n = int(input()) 輸入 7 之後，print(n + 3) 的輸出是？', '10', '73', '7 + 3', '發生錯誤'),

    # f-string 與格式化（8）
    mc('f-string 是在字串的引號前面加上哪個字母？', 'f', 's', 'p', 'x'),
    mc('print(f"{1 + 1}") 的輸出是？', '2', '{1 + 1}', '1 + 1', '發生錯誤',
       explanation='f-string 的大括號內會計算運算式並帶入結果。'),
    mc('name = "Al" 時，print(f"Hi {name}") 的輸出是？', 'Hi Al', 'Hi {name}', 'Hi name', 'f"Hi Al"'),
    mc('f-string 中的大括號 { } 用途是？', '帶入變數或運算式的值', '建立字典',
       '標示註解', '表示換行'),
    mc('print(f"{10 / 4}") 的輸出是？', '2.5', '2', '10 / 4', '2.50'),
    mc('忘了加 f 的 print("Hi {name}") 會輸出什麼？', 'Hi {name}', 'Hi Al', '發生錯誤', 'Hi',
       explanation='沒有 f 前綴就是普通字串，大括號原樣輸出。'),
    mc('age = 15 時，哪個寫法可以輸出「我 15 歲」？', 'print(f"我 {age} 歲")', 'print("我 age 歲")',
       'print(f"我 age 歲")', 'print("我 {age} 歲")'),
    mc('print("分數", 90) 與 print(f"分數 {90}") 的輸出？', '兩者都是「分數 90」', '前者多一個逗號',
       '後者多一組大括號', '兩者都發生錯誤'),

    # 錯誤與註解（8）
    mc('print(hello) 中 hello 沒加引號也沒定義過，會引發？', 'NameError', 'SyntaxError',
       'ValueError', 'TypeError'),
    mc('print("hi" 少了右括號，會引發？', 'SyntaxError', 'NameError', 'ValueError', 'IndentationError'),
    mc('"5" + 3 會引發哪種錯誤？', 'TypeError', 'ValueError', 'NameError', 'SyntaxError',
       explanation='字串不能與整數直接相加，型態錯誤。'),
    mc('int("5.5") 會發生什麼？', '引發 ValueError', '得到 5', '得到 5.5', '得到 6',
       explanation='int() 不能直接轉換帶小數點的「字串」，須先 float() 再 int()。'),
    mc('print(10 / 0) 會引發？', 'ZeroDivisionError', 'ValueError', 'NameError', '輸出無限大'),
    mc('已經指定 score = 90，執行 print(Score) 會發生什麼？', '引發 NameError，大小寫不同是不同名稱',
       '正常輸出 90', '自動轉成小寫後輸出', '引發 SyntaxError',
       explanation='Python 變數名稱區分大小寫，Score 從未被定義。'),
    mc('Python 單行註解使用哪個符號開頭？', '#', '//', '<!--', '--'),
    mc('註解在程式執行時會發生什麼事？', '被直譯器完全忽略', '輸出到螢幕',
       '造成語法錯誤', '轉成字串'),

    # 綜合讀碼（10）
    mc('以下程式的輸出是？\n\n```python\nx = 2\ny = x + 3\nprint(y)\n```', '5', '23', 'x + 3', '2'),
    mc('以下程式的輸出是？\n\n```python\na = 1\na = a + 1\nprint(a)\n```', '2', '1', '11', 'a + 1'),
    mc('以下程式的輸出是？\n\n```python\nn = "9"\nprint(n + n)\n```', '99', '18', '9 9', '發生錯誤',
       explanation='n 是字串，+ 是串接。'),
    mc('以下程式的輸出是？\n\n```python\nprice = 50\nqty = 3\nprint(price * qty)\n```', '150', '503', '53', '50 * 3'),
    mc('print(int(7.9)) 的輸出是？', '7', '8', '7.9', '發生錯誤',
       explanation='int() 轉換浮點數時直接捨去小數，不是四捨五入。'),
    mc('print(round(3.7)) 的輸出是？', '4', '3', '3.7', '3.5'),
    mc('print(len("Python")) 的輸出是？', '6', '5', '7', 'Python'),
    mc('以下程式的輸出是？\n\n```python\nx = 10\nprint("x")\n```', 'x', '10', 'x = 10', '發生錯誤',
       explanation='加了引號就是字串 "x"，不是變數。'),
    mc('以下程式的輸出是？\n\n```python\ntotal = 3 + 4\nprint("total =", total)\n```',
       'total = 7', 'total = 3 + 4', '7', 'total=7',
       explanation='逗號分隔的引數之間自動加一個空格。'),
    mc('以下程式的輸出是？\n\n```python\na = 5\nb = 2\nprint(a // b, a % b)\n```', '2 1', '2.5 1', '2 0', '3 1'),

    # ── U1 L1 填空 30（單一空格、1–3 行）──
    fb('輸出文字 Hello。\n\n```python\n__1__("Hello")\n```', 'print'),
    fb('讀入使用者輸入的文字並存入 name。\n\n```python\nname = __1__("請輸入姓名：")\n```', 'input'),
    fb('把輸入轉成整數。\n\n```python\nn = __1__(input("請輸入整數："))\n```', 'int'),
    fb('把輸入轉成浮點數（含小數）。\n\n```python\nprice = __1__(input("請輸入金額："))\n```', 'float'),
    fb('輸出 9 除以 4 的整數商（結果 2）。\n\n```python\nprint(9 __1__ 4)\n```', '//'),
    fb('輸出 9 除以 4 的餘數（結果 1）。\n\n```python\nprint(9 __1__ 4)\n```', '%'),
    fb('輸出 3 的 2 次方（結果 9）。\n\n```python\nprint(3 __1__ 2)\n```', '**'),
    fb('輸出 2 乘以 5 的結果（10）。\n\n```python\nprint(2 __1__ 5)\n```', '*'),
    fb('輸出 7 加 3 的結果（10）。\n\n```python\nprint(7 __1__ 3)\n```', '+'),
    fb('輸出 10 減 6 的結果（4）。\n\n```python\nprint(10 __1__ 6)\n```', '-'),
    fb('用 f-string 輸出「我 15 歲」。\n\n```python\nage = 15\nprint(__1__"我 {age} 歲")\n```', 'f'),
    fb('在這一行加上單行註解符號。\n\n```python\n__1__ 這行是說明文字，不會執行\nprint("開始")\n```', '#'),
    fb('把字串 "Amy" 指定給變數 name。\n\n```python\nname __1__ "Amy"\n```', '='),
    fb('輸出「99分」（字串串接）。\n\n```python\nprint(str(99) __1__ "分")\n```', '+'),
    fb('用 f-string 輸出「x = 8」。\n\n```python\nx = 8\nprint(f"x = {__1__}")\n```', 'x'),
    fb('輸出字串 "Hello" 的長度（結果 5）。\n\n```python\nprint(__1__("Hello"))\n```', 'len'),
    fb('把 3.14159 四捨五入到小數第 2 位後輸出（結果 3.14）。\n\n```python\nprint(__1__(3.14159, 2))\n```', 'round'),
    fb('把整數 123 轉成字串。\n\n```python\ns = __1__(123)\n```', 'str'),
    fb('讓輸出變成「A-B」。\n\n```python\nprint("A", "B", sep=__1__)\n```', ['"-"', "'-'"]),
    fb('讓 print 結尾不換行（end 設為空字串）。\n\n```python\nprint("加油", end=__1__)\nprint("！")\n```',
       ['""', "''"]),
    fb('讓 y 增加 2（複合指定運算子）。\n\n```python\ny = 5\ny __1__ 2\nprint(y)   # 7\n```', '+='),
    fb('輸出 11 整除某數的結果為 5。\n\n```python\nprint(11 // __1__)\n```', '2'),
    fb('讓輸出結果為 False（填入一個整數）。\n\n```python\nprint(bool(__1__))\n```', '0',
       explanation='整數 0 轉成布林值是 False，其他整數都是 True。'),
    fb('攝氏轉華氏：F = C × 9 ÷ 5 再加上多少？\n\n```python\nc = 20\nf = c * 9 / 5 + __1__\nprint(f)   # 68.0\n```', '32'),
    fb('把 185 秒換算成整數分鐘（結果 3）。\n\n```python\nsecs = 185\nprint(secs __1__ 60)\n```', '//'),
    fb('計算半徑 r 的圓面積（圓周率 3.14）。\n\n```python\nr = 5\narea = 3.14 * r __1__ 2\nprint(area)\n```', '**'),
    fb('讓 total 從 0 變成 5。\n\n```python\ntotal = 0\ntotal = total __1__ 5\nprint(total)\n```', '+'),
    fb('用 f-string 帶入變數 age。\n\n```python\nname = "小明"\nage = 16\nprint(f"{name}今年{__1__}歲")\n```', 'age'),
    fb('輸出 222（字串重複）。\n\n```python\nprint("2" __1__ 3)\n```', '*'),
    fb('輸出「Hi!」（字串串接）。\n\n```python\nmsg = "Hi"\nprint(msg __1__ "!")\n```', '+'),
]

# ── U1 Level 2：50 選擇 + 50 填空（TQC+ 觀念題風格：程式追蹤）──
U1_L2 = [
    # 選擇：程式追蹤與輸出預測（50）
    mc('以下程式的輸出是？\n\n```python\nx = 5\ny = x\nx = 9\nprint(y)\n```', '5', '9', '14', '發生錯誤',
       explanation='y 複製的是當時 x 的值 5，之後 x 改變不影響 y。'),
    mc('以下程式的輸出是？\n\n```python\na, b = 3, 8\na, b = b, a\nprint(a - b)\n```', '5', '-5', '3', '8',
       explanation='交換後 a=8、b=3，8-3=5。'),
    mc('以下程式的輸出是？\n\n```python\nn = 7\nn += 3\nn *= 2\nprint(n)\n```', '20', '13', '17', '10',
       explanation='7+3=10，再乘 2 得 20。'),
    mc('print(15 % 4 + 15 // 4) 的輸出是？', '6', '7', '3.75', '3',
       explanation='15%4=3、15//4=3，相加為 6。'),
    mc('print(2 * 3 ** 2) 的輸出是？', '18', '36', '12', '64',
       explanation='次方優先：3**2=9，再乘 2。'),
    mc('以下程式的輸出是？\n\n```python\nx = "10"\ny = 5\nprint(x + str(y))\n```', '105', '15', '10 5', '發生錯誤'),
    mc('print(int(9 / 2)) 的輸出是？', '4', '4.5', '5', '4.0',
       explanation='9/2=4.5，int() 捨去小數得 4。'),
    mc('print(10 / 5) 的輸出是？', '2.0', '2', '2.5', '0',
       explanation='/ 的結果一定是 float，即使整除。'),
    mc('以下程式的輸出是？\n\n```python\na = 7\nb = 2\nprint(f"{a}/{b}={a / b}")\n```',
       '7/2=3.5', '7/2=3', 'a/b=3.5', '{a}/{b}=3.5'),
    mc('以下程式的輸出是？\n\n```python\nscore = int("80")\nprint(score + 20)\n```', '100', '8020', '80 + 20', '發生錯誤'),
    mc('以下程式的輸出是？\n\n```python\nx = 4\nx = x * x\nprint(x)\n```', '16', '8', '4', '44'),
    mc('print("3" + "4") 與 print(3 + 4) 的輸出分別是？', '34 與 7', '7 與 7', '34 與 34', '7 與 34',
       explanation='字串相加是串接、數字相加是運算。'),
    mc('n = int(input()) 輸入 12，print(n % 10) 的輸出是？', '2', '1', '12', '1.2',
       explanation='% 10 可取出整數的個位數。'),
    mc('n = int(input()) 輸入 12，print(n // 10) 的輸出是？', '1', '2', '12', '1.2',
       explanation='// 10 可去掉整數的個位數。'),
    mc('a = input() 輸入 7 之後，print(a * 3) 的輸出是？', '777', '21', '7 7 7', '發生錯誤'),
    mc('以下程式的輸出是？\n\n```python\nprice = 100\nprice = price - price * 0.2\nprint(price)\n```',
       '80.0', '80', '99.8', '20.0',
       explanation='price*0.2=20.0，100-20.0=80.0（浮點運算結果帶小數）。'),
    mc('print(7 // 2, 7 / 2) 的輸出是？', '3 3.5', '3.5 3', '3 3', '3.5 3.5'),
    mc('以下程式的輸出是？\n\n```python\nx = 3.99\nprint(int(x))\n```', '3', '4', '3.99', '3.9',
       explanation='int() 直接捨去小數，不做四捨五入。'),
    mc('print(round(8.6)) 的輸出是？', '9', '8', '8.6', '8.5'),
    mc('下列哪一行會引發 TypeError？', 'print("a" + 1)', 'print("a" + "1")', 'print(1 + 1.0)', 'print("a" * 2)'),
    mc('以下程式的輸出是？\n\n```python\nx = 1\nx = 2\nx = 3\nprint(x)\n```', '3', '1', '6', '123',
       explanation='變數保留最後一次指定的值。'),
    mc('以下程式的輸出是？\n\n```python\ntotal = 0\ntotal += 3\ntotal += 4\nprint(total)\n```', '7', '34', '12', '0'),
    mc('print("Py" + "thon") 的輸出是？', 'Python', 'Py thon', 'Py+thon', 'Pythonthon'),
    mc('以下程式輸入 130，輸出是？\n\n```python\nm = int(input())\nprint(m // 60, m % 60)\n```',
       '2 10', '2 1', '2.17 10', '130 60',
       explanation='130 分鐘 = 2 小時餘 10 分鐘。'),
    mc('以下程式的輸出是？\n\n```python\nx = 6\ny = 4\navg = (x + y) / 2\nprint(avg)\n```', '5.0', '5', '10', '8.0'),
    mc('以下程式會引發哪種錯誤？\n\n```python\ny = x + 1\nprint(y)\n```', 'NameError', 'TypeError',
       'ValueError', 'SyntaxError', explanation='x 從未被指定值。'),
    mc('print(int("3.5")) 會引發哪種錯誤？', 'ValueError', 'TypeError', 'SyntaxError', '不會錯誤，輸出 3'),
    mc('下列哪一行「不會」發生錯誤？', 'print(int(3.5))', 'print(int("3.5"))', 'print("5" / 5)', 'print(x)',
       explanation='int(3.5) 是浮點數轉整數（得 3）；其餘分別是 ValueError、TypeError、NameError。'),
    mc('以下程式的輸出是？\n\n```python\na = "3"\nb = "5"\nprint(int(a) + int(b))\n```', '8', '35', '"8"', '發生錯誤'),
    mc('以下程式的輸出是？\n\n```python\nc = int("7") + float("2.5")\nprint(c)\n```', '9.5', '9', '72.5', '發生錯誤',
       explanation='int + float 的結果是 float。'),
    mc('print(str(1) + str(2)) 的輸出是？', '12', '3', '1 2', '發生錯誤'),
    mc('print(25 % 7) 的輸出是？', '4', '3', '3.57', '18'),
    mc('print(25 // 7) 的輸出是？', '3', '4', '3.57', '18'),
    mc('以下程式的輸出是？\n\n```python\nk = 2\nk **= 3\nprint(k)\n```', '8', '6', '5', '9',
       explanation='k **= 3 等同 k = k ** 3。'),
    mc('以下程式的輸出是？\n\n```python\nr = 10\nr //= 3\nprint(r)\n```', '3', '3.33', '4', '1'),
    mc('以下程式的輸出是？\n\n```python\np = 9\np %= 4\nprint(p)\n```', '1', '2', '2.25', '36'),
    mc('以下程式的輸出是？\n\n```python\nbmi = 70 / 1.75 ** 2\nprint(round(bmi, 1))\n```',
       '22.9', '22.86', '40.0', '22',
       explanation='先算 1.75**2=3.0625，70/3.0625≈22.857，取一位小數為 22.9。'),
    mc('f-string 的大括號內可以放什麼？', '變數或任何運算式', '只能放變數名稱',
       '只能放數字', '只能放字串'),
    mc('以下程式的輸出是？\n\n```python\ntw = 31.5\nprint(int(tw * 2))\n```', '63', '62', '63.0', '64'),
    mc('print("結果:", 3 * 4, sep="") 的輸出是？', '結果:12', '結果: 12', '結果:3*4', '結果 12',
       explanation='sep="" 讓兩個引數之間沒有分隔。'),
    mc('以下程式的輸出是？\n\n```python\nprint("A", end="")\nprint("B")\n```', 'AB', 'A B', 'A\\nB（兩行）', 'BA',
       explanation='end="" 讓第一個 print 結尾不換行。'),
    mc('以下程式的輸出是？\n\n```python\nx = 5\nprint(x == 5)\n```', 'True', 'False', '5', 'x == 5'),
    mc('以下程式的輸出是？\n\n```python\ntotal = int("100") - 30\nprint(total)\n```', '70', '10030', '100 - 30', '發生錯誤'),
    mc('x = int(input()) 若輸入「abc」會發生什麼？', '引發 ValueError', '得到 0',
       'x 變成 "abc"', '引發 TypeError'),
    mc('以下程式的輸出是？\n\n```python\nday = 100\nprint(day // 7, "週餘", day % 7, "天")\n```',
       '14 週餘 2 天', '14 週餘 3 天', '14.3 週餘 2 天', '2 週餘 14 天'),
    mc('以下程式的輸出是？\n\n```python\nmoney = 1000\nmoney -= 250\nmoney -= 250\nprint(money)\n```',
       '500', '750', '1000', '250'),
    mc('print(float(5)) 的輸出是？', '5.0', '5', '"5.0"', '發生錯誤'),
    mc('print(int(True)) 的輸出是？', '1', 'True', '0', '發生錯誤',
       explanation='布林值 True 轉整數是 1、False 是 0。'),
    mc('以下程式的輸出是？\n\n```python\nx = 7\ny = 2\nprint(x - y * 2)\n```', '3', '10', '5', '-3',
       explanation='先乘後減：7-4=3。'),
    mc('print((3 + 5) * 2 / 4) 的輸出是？', '4.0', '4', '5.5', '6.5',
       explanation='(3+5)=8，8×2=16，16/4=4.0。'),

    # 填空：完成 2–5 行小程式（50）
    fb('讀入兩個整數並輸出平均值。\n\n```python\na = int(input())\nb = int(input())\nprint((a + b) / __1__)\n```', '2'),
    fb('攝氏溫度轉華氏（F = C × 9/5 + 32）。\n\n```python\nc = float(input())\nf = c __1__ 9 / 5 + 32\nprint(f)\n```', '*'),
    fb('用 f-string 輸出「NT$ 350」。\n\n```python\nprice = 350\nprint(f"NT$ {__1__}")\n```', 'price'),
    fb('把 t 秒換算成「幾小時幾分」：先算小時，再算剩餘分鐘。\n\n```python\nt = 7380\nh = t __1__ 3600\nm = t % 3600 __2__ 60\nprint(h, "小時", m, "分")\n```',
       '//', '//', explanation='7380 秒 = 2 小時 3 分。'),
    fb('交換 a、b 兩個變數的值。\n\n```python\na = 3\nb = 8\na, b = __1__, a\nprint(a, b)   # 8 3\n```', 'b'),
    fb('輸出三位數 n 的個位數字。\n\n```python\nn = 528\nprint(n __1__ 10)   # 8\n```', '%'),
    fb('去掉 n 的個位數字後輸出。\n\n```python\nn = 528\nprint(n __1__ 10)   # 52\n```', '//'),
    fb('讀入單價與數量，輸出總價。\n\n```python\nprice = __1__(input())\nqty = int(input())\nprint(price __2__ qty)\n```',
       'int', '*'),
    fb('讓兩個 print 的輸出接在同一行。\n\n```python\nprint("學號:", end=__1__)\nprint("A123")\n```', ['""', "''"]),
    fb('讓 x 的型態變成 float。\n\n```python\nx = __1__("3.3")\nprint(type(x))   # <class \'float\'>\n```', 'float'),
    fb('計算長方形面積。\n\n```python\nw = int(input())\nh = int(input())\narea = w __1__ h\nprint(area)\n```', '*'),
    fb('把餘額扣掉 120 元（複合指定）。\n\n```python\nbalance = 500\nbalance __1__ 120\nprint(balance)   # 380\n```', '-='),
    fb('把分數乘以 1.5 倍（複合指定）。\n\n```python\nscore = 60\nscore __1__ 1.5\nprint(score)   # 90.0\n```', '*='),
    fb('輸出 2 的 10 次方。\n\n```python\nprint(2 __1__ 10)   # 1024\n```', '**'),
    fb('讀入體重(kg)與身高(m)，計算 BMI = 體重 ÷ 身高平方。\n\n```python\nw = float(input())\nh = float(input())\nbmi = w / h __1__ 2\nprint(bmi)\n```', '**'),
    fb('把輸入的西元年轉成民國年（減 1911）。\n\n```python\nyear = int(input())\nprint(year __1__ 1911)\n```', '-'),
    fb('輸出「85 分」— 數字與文字之間用 f-string 完成。\n\n```python\nscore = 85\nprint(__1__"{score} 分")\n```', 'f'),
    fb('讀入攝氏溫度並「原樣」輸出提示與數值。\n\n```python\nt = float(__1__("請輸入溫度："))\nprint("溫度是", t)\n```', 'input'),
    fb('把 456 拆出百位數。\n\n```python\nn = 456\nprint(n __1__ 100)   # 4\n```', '//'),
    fb('把 456 拆出十位數（先除後取餘）。\n\n```python\nn = 456\nprint(n // 10 __1__ 10)   # 5\n```', '%'),
    fb('計算五科總分後輸出平均（浮點數）。\n\n```python\ntotal = 60 + 70 + 80 + 90 + 100\nprint(total __1__ 5)   # 80.0\n```', '/'),
    fb('把字串數字轉成整數後比較大小輸出 True。\n\n```python\na = __1__("15")\nprint(a > 10)   # True\n```', 'int'),
    fb('輸出圓周長（2 × 3.14 × r）。\n\n```python\nr = 4\nprint(__1__ * 3.14 * r)   # 25.12\n```', '2'),
    fb('把 total 初始化為 0，再加上 99。\n\n```python\ntotal = __1__\ntotal += 99\nprint(total)   # 99\n```', '0'),
    fb('輸出兩數相除的整數商與餘數。\n\n```python\na = 47\nb = 6\nprint(a // b, a __1__ b)   # 7 5\n```', '%'),
    fb('用 round 把 7.456 取到小數第 1 位。\n\n```python\nprint(round(7.456, __1__))   # 7.5\n```', '1'),
    fb('讓輸出型態顯示 <class \'str\'>。\n\n```python\nx = __1__(99)\nprint(type(x))\n```', 'str'),
    fb('計算打八折後的價格。\n\n```python\nprice = 250\nsale = price * __1__\nprint(sale)   # 200.0\n```', '0.8'),
    fb('輸出 1 千萬（用次方表示 10 的 7 次方）。\n\n```python\nprint(10 ** __1__)   # 10000000\n```', '7'),
    fb('讀入分鐘數，輸出等於幾小時（含小數）。\n\n```python\nm = int(input())\nprint(m __1__ 60)\n```', '/'),
    fb('把 flag 設成布林值 True。\n\n```python\nflag = __1__\nprint(type(flag))   # <class \'bool\'>\n```', 'True'),
    fb('輸出「姓名:王小明」，中間不能有空格。\n\n```python\nname = "王小明"\nprint("姓名:", name, sep=__1__)\n```',
       ['""', "''"]),
    fb('把身高 158.7 公分無條件捨去成整數。\n\n```python\nh = 158.7\nprint(__1__(h))   # 158\n```', 'int'),
    fb('數字每三位加逗號之前，先把總金額算出來：單價 1200、數量 3。\n\n```python\ntotal = 1200 __1__ 3\nprint(total)   # 3600\n```', '*'),
    fb('把輸入的元轉換成「幾張百元鈔」。\n\n```python\nmoney = int(input())\nprint(money __1__ 100)\n```', '//'),
    fb('把輸入的元轉換成「不足百元的零頭」。\n\n```python\nmoney = int(input())\nprint(money __1__ 100)\n```', '%'),
    fb('讀入國文、英文成績並用 f-string 輸出總分。\n\n```python\nch = int(input())\nen = int(input())\nprint(f"總分 {ch __1__ en}")\n```', '+'),
    fb('讓 count 每執行一次就加 1。\n\n```python\ncount = 0\ncount __1__ 1\nprint(count)   # 1\n```', '+='),
    fb('輸出變數 x 與它的平方，中間用「的平方是」串起來。\n\n```python\nx = 6\nprint(f"{x} 的平方是 {x ** __1__}")\n```', '2'),
    fb('把梯形面積算出來：(上底 + 下底) × 高 ÷ 2。\n\n```python\na = 3\nb = 7\nh = 4\narea = (a + b) * h / __1__\nprint(area)   # 20.0\n```', '2'),
    fb('讀入三個整數並輸出總和。\n\n```python\na = int(input())\nb = int(input())\nc = int(input())\nprint(a + b __1__ c)\n```', '+'),
    fb('把「分」換算成「元」（100 分 = 1 元，取小數）。\n\n```python\ncents = 1550\nprint(cents / __1__)   # 15.5\n```', '100'),
    fb('輸出 f-string 計算結果「3 + 4 = 7」。\n\n```python\nprint(f"3 + 4 = {3 __1__ 4}")\n```', '+'),
    fb('宣告一個空字串給 message。\n\n```python\nmessage = __1__\nprint(len(message))   # 0\n```', ['""', "''"]),
    fb('把及格分數線 60 存進常數風格的變數。\n\n```python\nPASS_LINE __1__ 60\nprint(PASS_LINE)\n```', '='),
    fb('輸出兩個變數的值，中間以「/」分隔。\n\n```python\na = 5\nb = 9\nprint(a, b, sep=__1__)   # 5/9\n```',
       ['"/"', "'/'"]),
    fb('計算立方體體積（邊長的 3 次方）。\n\n```python\nside = 4\nprint(side ** __1__)   # 64\n```', '3'),
    fb('讀入的字串重複輸出 5 次（不換行、直接相連）。\n\n```python\ntext = input()\nprint(text __1__ 5)\n```', '*'),
    fb('把浮點成績 89.6 四捨五入成整數。\n\n```python\nscore = 89.6\nprint(__1__(score))   # 90\n```', 'round'),
    fb('計算時薪 183 元工作 7.5 小時的薪資。\n\n```python\nwage = 183 __1__ 7.5\nprint(wage)   # 1372.5\n```', '*'),
]

# ── U1 Level 3：30 選擇 + 70 填空（TQC+ 實作／技藝競賽風格：情境式）──
U1_L3 = [
    # 選擇：進階追蹤與陷阱（30）
    mc('print(2 + 3 * 4 ** 2) 的輸出是？', '50', '80', '400', '44',
       explanation='次方最優先：4**2=16，3×16=48，最後 2+48=50。'),
    mc('print(17 // 4 // 2) 的輸出是？', '2', '4', '2.125', '8',
       explanation='同級運算由左至右：17//4=4，4//2=2。'),
    mc('print(100 % 30 % 7) 的輸出是？', '3', '10', '4', '0',
       explanation='由左至右：100%30=10，10%7=3。'),
    mc('print(0.1 + 0.2 == 0.3) 的輸出是？', 'False', 'True', '0.3', '發生錯誤',
       explanation='浮點數以二進位近似儲存，0.1+0.2 = 0.30000000000000004。'),
    mc('print(True + True) 的輸出是？', '2', 'TrueTrue', 'True', '發生錯誤',
       explanation='布林值參與算術時 True 視為 1。'),
    mc('以下程式的輸出是？\n\n```python\nx = y = 5\ny += 1\nprint(x, y)\n```', '5 6', '6 6', '5 5', '6 5',
       explanation='連鎖指定後兩者都是 5；整數不可變，y+=1 只改 y。'),
    mc('print(f"{7:03d}") 的輸出是？', '007', '7', '73d', '700',
       explanation='格式規格 03d：整數靠右補零至 3 位。'),
    mc('print(f"{3.14159:.2f}") 的輸出是？', '3.14', '3.1', '3.142', '3.2',
       explanation='.2f 表示固定小數點後 2 位。'),
    mc('print(f"{1234567:,}") 的輸出是？', '1,234,567', '1234567', '1.234.567', '123,4567',
       explanation='格式規格逗號：千分位分隔。'),
    mc('print(10 % 3 * 2 ** 2) 的輸出是？', '4', '16', '2', '1',
       explanation='先 2**2=4，再 10%3=1，最後 1×4=4。'),
    mc('print(f"{42:>5}") 的輸出是？', '42 靠右對齊，前面補 3 個空格', '42 靠左，後面補 3 個空格',
       '00042', '發生錯誤',
       explanation='格式規格 >5 表示總寬度 5、靠右對齊，不足處補空格。'),
    mc('以下程式的輸出是？\n\n```python\na = 5\nb = 2\na, b = a + b, a - b\nprint(a, b)\n```', '7 3', '7 5', '3 7', '5 2',
       explanation='右側先以舊值同時求值：a+b=7、a-b=3。'),
    mc('print(int(9.99), round(9.99)) 的輸出是？', '9 10', '10 10', '9 9', '10 9',
       explanation='int() 直接捨去小數、round() 四捨五入，兩者結果不同。'),
    mc('print(17 // 5 * 5 + 17 % 5) 的輸出是？', '17', '15', '20', '12',
       explanation='商×除數＋餘數必等於原數。'),
    mc('print(len(str(12345))) 的輸出是？', '5', '12345', '1', '發生錯誤',
       explanation='先轉字串 "12345"，長度是 5 — 計算位數的常用技巧。'),
    mc('print("5" * 2 + str(5 * 2)) 的輸出是？', '5510', '2010', '1010', '55 10',
       explanation='"5"*2 是 "55"，str(10) 是 "10"，串接得 "5510"。'),
    mc('print(float("1e3")) 的輸出是？', '1000.0', '1.3', '103.0', '發生錯誤',
       explanation='1e3 是科學記號，表示 1×10³。'),
    mc('print(7 / 2 // 1.5) 的輸出是？', '2.0', '2', '2.33', '3.5',
       explanation='由左到右：7/2=3.5，3.5//1.5=2.0（浮點整除仍為 float）。'),
    mc('divmod(17, 5) 的回傳值是？', '(3, 2)', '(2, 3)', '3.4', '[3, 2]',
       explanation='divmod 一次回傳（商, 餘數）。'),
    mc('print(abs(-3) + abs(3)) 的輸出是？', '6', '0', '-6', '3'),
    mc('以下程式的輸出是？\n\n```python\nx = 10\nx //= 3\nx **= 2\nprint(x)\n```', '9', '100', '11', '10',
       explanation='10//3=3，3**2=9。'),
    mc('int(input()) 讀入 "  42  "（前後有空格）會發生什麼？', '得到整數 42',
       '引發 ValueError', '得到字串 "  42  "', '得到 0',
       explanation='int() 轉字串時會自動忽略前後空白。'),
    mc('print(f"{100 / 3:.1f}") 的輸出是？', '33.3', '33.33', '33', '33.4'),
    mc('print(type(3 / 1) == type(3.0)) 的輸出是？', 'True', 'False', 'float', '發生錯誤',
       explanation='/ 的結果是 float，與 3.0 同型態。'),
    mc('下列哪個運算式的值「不等於」10？', '103 % 100', '3 + 7', '100 // 10', '2 ** 3 + 2',
       explanation='103 % 100 = 3；其餘都是 10（3+7、100//10、8+2）。'),
    mc('print(5 + int(2.9) + round(2.9)) 的輸出是？', '10', '11', '9', '10.8',
       explanation='int(2.9)=2（捨去）、round(2.9)=3（四捨五入），5+2+3=10。'),
    mc('n = "07"; print(int(n) + 1) 的輸出是？', '8', '071', '08', '發生錯誤',
       explanation='int("07") 是 7；字串轉整數允許前導零。'),
    mc('print(f"{3.14159:.3f}") 的輸出是？', '3.142', '3.141', '3.14159', '3.14',
       explanation='.3f 取到小數第 3 位並四捨五入：3.14159 → 3.142。'),
    mc('以下程式的輸出是？\n\n```python\nprint("A", "B", sep="-", end="!")\nprint("C")\n```',
       'A-B!C', 'A-B!\nC', 'A B!C', 'A-B-C!',
       explanation='sep 決定引數間分隔、end 決定結尾字元，兩個 print 接在同一行。'),
    mc('想把 3.999「直接捨去」小數變成 3，哪個寫法正確？', 'int(3.999)', 'round(3.999)',
       'float(3.999)', 'str(3.999)',
       explanation='int() 捨去小數得 3；round(3.999) 會四捨五入成 4。'),

    # 填空：情境式程式完成（70）
    fb('【找零計算】讀入付款金額與商品價格，輸出應找的 500、100 元鈔票數與剩餘零錢。\n\n```python\npay = int(input())\nprice = int(input())\nchange = pay - price\nn500 = change __1__ 500\nrest = change % 500\nn100 = rest __2__ 100\ncoin = rest % 100\nprint(n500, n100, coin)\n```',
       '//', '//', explanation='鈔票張數用整除、剩餘金額用取餘。'),
    fb('【秒數轉時間】把總秒數轉成 時:分:秒。\n\n```python\nt = int(input())\nh = t // 3600\nm = t __1__ 3600 // 60\ns = t __2__ 60\nprint(f"{h}:{m}:{s}")\n```',
       '%', '%'),
    fb('【溫度轉換】華氏轉攝氏：C = (F − 32) × 5 ÷ 9，取小數 1 位。\n\n```python\nf = float(input())\nc = (f - __1__) * 5 / 9\nprint(f"{c:.__2__f}")\n```',
       '32', '1'),
    fb('【BMI 計算】讀入體重(kg)、身高(cm)，先把身高轉公尺再算 BMI，取 2 位小數。\n\n```python\nw = float(input())\nh = float(input()) / __1__\nbmi = w / h ** 2\nprint(f"{bmi:.2__2__}")\n```',
       '100', 'f'),
    fb('【數字反轉】把三位數 n 反轉輸出（如 123 → 321）。\n\n```python\nn = int(input())\na = n // 100\nb = n // 10 __1__ 10\nc = n __2__ 10\nprint(c * 100 + b * 10 + a)\n```',
       '%', '%'),
    fb('【各位數和】計算三位數各位數字的總和。\n\n```python\nn = int(input())\ntotal = n // 100 + n // 10 % 10 + n __1__ 10\nprint(total)\n```', '%'),
    fb('【平均分數】讀入三科成績，平均取到小數第 2 位輸出。\n\n```python\na = int(input())\nb = int(input())\nc = int(input())\navg = (a + b + c) / __1__\nprint(f"{avg:__2__}")\n```',
       '3', '.2f'),
    fb('【匯率換算】台幣換美元（匯率 31.5），輸出取 2 位小數。\n\n```python\ntwd = float(input())\nusd = twd __1__ 31.5\nprint(round(usd, __2__))\n```',
       '/', '2'),
    fb('【購物總價】單價 × 數量再打 9 折。\n\n```python\nprice = int(input())\nqty = int(input())\ntotal = price * qty * __1__\nprint(total)\n```', '0.9'),
    fb('【時間差】電影 138 分鐘，換算成「幾小時幾分」輸出 2 小時 18 分。\n\n```python\nmins = 138\nprint(mins // 60, "小時", mins __1__ 60, "分")\n```', '%'),
    fb('【連鎖指定】讓 a、b、c 同時等於 0。\n\n```python\na = b __1__ c = 0\nprint(a, b, c)\n```', '='),
    fb('【薪資試算】時薪 190，工時超過 8 小時的部分以 1.34 倍計。已知工作 10 小時。\n\n```python\nbase = 190 * 8\novertime = 190 * __1__ * (10 - 8)\nprint(base + overtime)\n```',
       '1.34'),
    fb('【圓面積與周長】讀入半徑，同時輸出面積與周長（圓周率 3.14159）。\n\n```python\nr = float(input())\npi = 3.14159\narea = pi * r __1__ 2\nperi = 2 * pi __2__ r\nprint(area, peri)\n```',
       '**', '*'),
    fb('【等差數列和】首項 a、公差 d、項數 n 的總和 = (2a + (n−1)d) × n ÷ 2。\n\n```python\na = 3\nd = 4\nn = 10\ntotal = (2 * a + (n - 1) * d) * n __1__ 2\nprint(total)   # 210\n```',
       '//', explanation='用 // 保持整數輸出（值必為整數）。'),
    fb('【單位換算】把 x 公里換成公尺再加上 y 公尺。\n\n```python\nx = float(input())\ny = float(input())\nprint(x * __1__ + y)\n```', '1000'),
    fb('【位數擷取】取出四位數的千位與個位相加。\n\n```python\nn = 5273\nprint(n // __1__ + n % __2__)   # 5 + 3 = 8\n```',
       '1000', '10'),
    fb('【科學記號】把 0.00052 用 e 記號輸出。\n\n```python\nx = 0.00052\nprint(f"{x:__1__}")   # 5.2e-04\n```', '.1e'),
    fb('【百分比】答對 17 題、共 20 題，輸出「85.0%」。\n\n```python\nright = 17\ntotal = 20\nrate = right / total * __1__\nprint(f"{rate}__2__")\n```',
       '100', '%'),
    fb('【補零格式】把編號 7 輸出成 0007。\n\n```python\nno = 7\nprint(f"{no:__1__}")\n```', '04d'),
    fb('【千分位】把 9876543 輸出成 9,876,543。\n\n```python\nn = 9876543\nprint(f"{n:__1__}")\n```', ','),
    fb('【交換與運算】不用第三個變數交換 x、y，再輸出差。\n\n```python\nx = 12\ny = 5\nx, y = y, __1__\nprint(x - y)   # -7\n```', 'x'),
    fb('【複利計算】本金 10000、年利率 1.2%、存 3 年（單利）。\n\n```python\np = 10000\nrate = 0.012\ninterest = p * rate * __1__\nprint(p + interest)\n```', '3'),
    fb('【去尾進位】把 47 個蛋裝盒，每盒 6 個：需要幾個「裝滿」的盒子與剩幾顆蛋。\n\n```python\neggs = 47\nbox = eggs __1__ 6\nleft = eggs __2__ 6\nprint(box, left)   # 7 5\n```',
       '//', '%'),
    fb('【平均速度】距離 180 公里、時間 2.5 小時，速度取整數輸出。\n\n```python\nd = 180\nt = 2.5\nprint(__1__(d / t))   # 72\n```', 'int'),
    fb('【運算式重組】輸出 (5 + 3)² = 64。\n\n```python\nprint((5 __1__ 3) ** 2)\n```', '+'),
    fb('【字串重複排版】輸出 30 個等號當分隔線。\n\n```python\nprint("=" __1__ 30)\n```', '*'),
    fb('【變數追蹤】完成程式使輸出為 25。\n\n```python\nx = 2\nx += 3\nx __1__= x\nprint(x)   # 25\n```', '*',
       explanation='x*=x 即 5×5=25。'),
    fb('【階段計費】計程車：起跳 85 元（1.25 公里），之後每 0.2 公里加 5 元。已知里程 3.25 公里。\n\n```python\nkm = 3.25\nextra = (km - 1.25) / __1__\nfare = 85 + extra * 5\nprint(round(fare))   # 135\n```',
       '0.2', explanation='浮點除法可能有微小誤差，最後以 round 取整最保險。'),
    fb('【整數上限】印出 n 位數的最大值（如 3 位數 → 999）。\n\n```python\nn = 3\nprint(10 ** n __1__ 1)\n```', '-'),
    fb('【油耗計算】行駛 412 公里、加油 28.4 公升，輸出每公升跑幾公里（取 1 位小數）。\n\n```python\nkm = 412\nliter = 28.4\nprint(round(km / liter, __1__))\n```', '1'),
    fb('【分帳】聚餐 3480 元由 7 人平分，輸出每人應付（無條件進位到整數需 +6 再整除的技巧）。\n\n```python\ntotal = 3480\nn = 7\nper = (total + n - 1) __1__ n\nprint(per)   # 498\n```',
       '//', explanation='(total+n-1)//n 是不用 math.ceil 的無條件進位技巧。'),
    fb('【判斷位數】用 len 與 str 輸出整數 n 的位數。\n\n```python\nn = 90210\nprint(__1__(str(n)))   # 5\n```', 'len'),
    fb('【百位四捨五入】把 4567 四捨五入到百位（輸出 4600）。\n\n```python\nn = 4567\nprint(round(n, __1__))\n```', '-2',
       explanation='round 的第二參數可為負數：-2 表示取到百位。'),
    fb('【運費規則】滿 490 免運，未滿運費 65。先算含運總價（購物 350 元）。\n\n```python\nprice = 350\nshipping = 65\ntotal = price __1__ shipping\nprint(total)   # 415\n```', '+'),
    fb('【時薪反推】月薪 36000、每月工時 176 小時，輸出時薪（取 2 位小數）。\n\n```python\nsalary = 36000\nhours = 176\nprint(f"{salary / hours:.2__1__}")\n```', 'f'),
    fb('【溫差】今天最高溫 31.5、最低溫 24.2，輸出溫差的絕對值（取 1 位小數）。\n\n```python\nhigh = 31.5\nlow = 24.2\nprint(round(__1__(low - high), 1))   # 7.3\n```', 'abs'),
    fb('【商與餘一次取得】用 divmod 同時取得 100 ÷ 7 的商與餘數。\n\n```python\nq, r = __1__(100, 7)\nprint(q, r)   # 14 2\n```', 'divmod'),
    fb('【票價總計】全票 280、半票 140，讀入兩種張數輸出總金額。\n\n```python\nfull = int(input())\nhalf = int(input())\ntotal = full * 280 + half * __1__\nprint(total)\n```', '140'),
    fb('【濃度計算】糖 30 克加水 270 克，輸出濃度百分比（整數 10）。\n\n```python\nsugar = 30\nwater = 270\nrate = sugar / (sugar + water) * 100\nprint(__1__(rate))\n```', 'int'),
    fb('【里程表】出發 12480.6 公里、抵達 12742.1 公里，輸出行駛里程（取 1 位小數）。\n\n```python\nstart = 12480.6\nend = 12742.1\nprint(round(end __1__ start, 1))\n```', '-'),
    fb('【購買上限】身上 500 元，飲料一瓶 35 元，最多能買幾瓶、剩多少錢。\n\n```python\nmoney = 500\nprice = 35\nprint(money // price, money __1__ price)   # 14 10\n```', '%'),
    fb('【零存整付】每月存 3500 元，輸出兩年總存款。\n\n```python\nmonthly = 3500\nprint(monthly * 12 * __1__)   # 84000\n```', '2'),
    fb('【打折進位】原價 199 打 75 折，輸出去掉小數的售價。\n\n```python\nprice = 199\nsale = price * 0.75\nprint(__1__(sale))   # 149\n```', 'int'),
    fb('【回數票】一本回數票 10 張 950 元，單買一張 105 元，輸出買一本省多少。\n\n```python\nsingle = 105\nbook = 950\nprint(single * __1__ - book)   # 100\n```', '10'),
    fb('【點數兌換】1 點折 0.3 元，讀入點數輸出可折抵金額（去小數）。\n\n```python\npoints = int(input())\nprint(int(points * __1__))\n```', '0.3'),
    fb('【梯形圍籬】上底 5、下底 11、高 4 的梯形面積。\n\n```python\narea = (5 + 11) * 4 __1__ 2\nprint(area)   # 32\n```', '//'),
    fb('【對分猜數】1 到 100 的中點（整數）。\n\n```python\nlow = 1\nhigh = 100\nmid = (low + high) __1__ 2\nprint(mid)   # 50\n```', '//'),
    fb('【組合輸出】用一個 print 輸出兩行：第一行 Hello、第二行 World（用跳脫字元）。\n\n```python\nprint("Hello__1__World")\n```',
       ['\\n', '\\\\n'], explanation=r'\n 是換行的跳脫字元。'),
    fb('【引號中的引號】輸出：He said "Hi"（用跳脫字元保留雙引號）。\n\n```python\nprint("He said __1__Hi__2__")\n```',
       ['\\"', '\\\\"'], ['\\"', '\\\\"']),
    fb('【總秒數】3 小時 25 分 40 秒共有幾秒。\n\n```python\nprint(3 * 3600 + 25 * __1__ + 40)   # 12340\n```', '60'),
    fb('【明年年齡】讀入出生年（民國），輸出明年幾歲（今年民國 115 年）。\n\n```python\nbirth = int(input())\nage = 115 - birth + __1__\nprint(age)\n```', '1'),
    fb('【匯差】用 31.2 買進 500 美元、用 31.8 賣出，輸出價差獲利。\n\n```python\nprofit = (31.8 - 31.2) * __1__\nprint(round(profit, 1))   # 300.0\n```', '500'),
    fb('【階梯電價】前 120 度每度 1.63、超過部分每度 2.38，用量 200 度。\n\n```python\nkwh = 200\nbill = 120 * 1.63 + (kwh - __1__) * 2.38\nprint(round(bill))   # 386\n```', '120'),
    fb('【正方形對角線】邊長 s 的對角線 = s × 2 的 0.5 次方。\n\n```python\ns = 10\nprint(round(s * 2 ** __1__, 2))   # 14.14\n```', '0.5'),
    fb('【集點升級】每消費 50 元集 1 點，讀入消費金額輸出點數。\n\n```python\nspend = int(input())\nprint(spend __1__ 50)\n```', '//'),
    fb('【平均進貨價】兩批貨：40 個單價 12 元、60 個單價 15 元，輸出平均單價。\n\n```python\ncost = 40 * 12 + 60 * 15\navg = cost / (40 + __1__)\nprint(avg)   # 13.8\n```', '60'),
    fb('【溫度顯示】把 36.53 度輸出成「36.5℃」。\n\n```python\nt = 36.53\nprint(f"{t:.1f}__1__")\n```', '℃'),
    fb('【停車費】每 30 分鐘 20 元、不足 30 分鐘以 30 分計。停 100 分鐘。\n\n```python\nmins = 100\nunits = (mins + 29) // __1__\nprint(units * 20)   # 80\n```', '30'),
    fb('【匯總報表】用一個 f-string 輸出「小計 1200 元、稅 60 元、總計 1260 元」。\n\n```python\nsub = 1200\ntax = 60\nprint(f"小計 {sub} 元、稅 {tax} 元、總計 {sub __1__ tax} 元")\n```', '+'),
    fb('【單價比較】A 牌 600g 賣 96 元，輸出每 100g 單價。\n\n```python\nprice = 96\nweight = 600\nprint(price / weight * __1__)   # 16.0\n```', '100'),
    fb('【行程分段】500 公里旅程已完成 37%，輸出剩餘公里數。\n\n```python\ntotal = 500\ndone = 0.37\nprint(total * (1 __1__ done))   # 315.0\n```', '-'),
    fb('【誤差修正】把 0.1 + 0.2 的結果四捨五入到 1 位小數再比較 0.3。\n\n```python\nx = 0.1 + 0.2\nprint(__1__(x, 1) == 0.3)   # True\n```', 'round'),
    fb('【倒數計時】距離比賽還有 40 天，輸出「5 週又 5 天」的兩個數字。\n\n```python\ndays = 40\nprint(days // 7, "週又", days __1__ 7, "天")\n```', '%'),
    fb('【身高單位】把 5 呎 11 吋換算成公分（1 呎 = 12 吋、1 吋 = 2.54 公分）。\n\n```python\ninches = 5 * __1__ + 11\nprint(round(inches * 2.54, 1))   # 180.3\n```', '12'),
    fb('【付款湊整】消費 268 元付 1000 元，輸出找零中 50 元硬幣的個數。\n\n```python\nchange = 1000 - 268\nprint(change % 100 __1__ 50)   # 32 除百餘數再整除 50 → 0\n```',
       '//', explanation='732 % 100 = 32，32 // 50 = 0 個 50 元硬幣。'),
    fb('【成績加權】平時 30%、期中 30%、期末 40%：平時 80、期中 75、期末 90。\n\n```python\nfinal = 80 * 0.3 + 75 * 0.3 + 90 * __1__\nprint(final)   # 82.5\n```', '0.4'),
    fb('【網速換算】100 Mbps 下載 1500 MB 檔案需要幾秒（1 Byte = 8 bits）。\n\n```python\nmb = 1500\nspeed = 100\nprint(mb * __1__ / speed)   # 120.0\n```', '8'),
    fb('【現在幾點】現在 22 點，再過 55 小時是幾點（24 小時制）。\n\n```python\nnow = 22\nprint((now + 55) __1__ 24)   # 5\n```', '%'),
    fb('【折上折】原價 1000 元先打 8 折、再打 95 折，輸出最後售價。\n\n```python\nprice = 1000\nfinal = price * 0.8 * __1__\nprint(final)   # 760.0\n```', '0.95'),
    fb('【耗電計算】60W 燈泡每天開 5 小時，輸出 30 天共耗電幾度（1 度 = 1000 瓦小時）。\n\n```python\nwatt = 60\nhours = 5\ndays = 30\nprint(watt * hours * days / __1__)   # 9.0\n```', '1000'),
]


# ═══════════════════════════════════════════════════════════════════
# 填空題 → 選擇題 轉換（2026-07-04 拍板全選擇制）
# 題幹與正解沿用人工命題，誘答選項依答案類型從精選誘答表產生。
# ═══════════════════════════════════════════════════════════════════

_DISTRACTORS = {
    '+': ['-', '*', '//'], '-': ['+', '/', '%'], '*': ['+', '**', '//'],
    '/': ['//', '%', '*'], '//': ['/', '%', '*'], '%': ['//', '/', '**'],
    '**': ['*', '^', '//'], '+=': ['=+', '==', '+'], '-=': ['=-', '==', '-'],
    '*=': ['=*', '==', '*'], '=': ['==', '=>', '::'], '==': ['=', '!=', '≡'],
    '<=': ['<', '>=', '=<'], '>=': ['>', '<=', '=>'],
    'print': ['echo', 'output', 'show'], 'input': ['read', 'scan', 'get'],
    'int': ['str', 'float', 'bool'], 'float': ['int', 'str', 'double'],
    'str': ['int', 'chr', 'text'], 'len': ['count', 'size', 'chars'],
    'round': ['int', 'cut', 'fix'], 'abs': ['pos', 'fabs', 'plus'],
    'divmod': ['moddiv', 'divide', 'math.mod'], 'f': ['s', 'p', 'x'],
    '#': ['//', '<!--', ';'], 'else': ['elif', 'if not', 'other'],
    'elif': ['else if', 'elseif', 'case'], 'True': ['False', '1', '"True"'],
    'age': ['name', 'year', 'n'], 'x': ['y', 'n', 'value'],
    'y': ['x', 'z', 'n'], 'b': ['a', 'c', 'n'], 'price': ['cost', 'money', 'qty'],
    'total': ['sum', 'count', 'result'],
    '"-"': ['","', '"."', '" "'], '""': ['" "', '"0"', 'None'],
    '"/"': ['"-"', '","', '"|"'],
    '\\n': ['\\t', '/n', '\\\\'], '\\"': ["\\'", "''", '"'],
    '℃': ['度C', 'C°', 'oC'], '.2f': ['.2d', '2.f', 'f2'],
    '.1e': ['.e1', '1e', '.1f'], '04d': ['4d', 'd04', '0.4d'],
    ',': ['.', ';', '_'],
}


def _numeric_distractors(text):
    try:
        value = float(text)
    except ValueError:
        return None
    is_int = '.' not in text
    if is_int:
        n = int(value)
        cands = [n + 1, n - 1, n * 2, n + 2, n * 10]
    else:
        cands = [value * 10, value / 10, value + 1, value * 2]
    out = []
    for c in cands:
        s = str(int(c)) if is_int or float(c).is_integer() and abs(c) >= 1 else f'{c:g}'
        if s != text and s not in out:
            out.append(s)
        if len(out) == 3:
            break
    return out


def _distractors_for(answer, bank_pool, rng):
    """回傳 3 個不等於正解的誘答字串。"""
    if answer in _DISTRACTORS:
        return list(_DISTRACTORS[answer])
    numeric = _numeric_distractors(answer)
    if numeric and len(numeric) == 3:
        return numeric
    pool = [a for a in bank_pool if a != answer]
    rng.shuffle(pool)
    out = []
    for a in pool:
        if a not in out:
            out.append(a)
        if len(out) == 3:
            break
    return out


def fb_to_mc(question, bank_pool):
    """把 fill_blank 題轉成 multiple_choice：正解＋3 誘答。多空格題以「、」串接成組。"""
    import hashlib
    import random
    rng = random.Random(int(hashlib.md5(question['content'].encode('utf-8')).hexdigest(), 16))
    answers = [line.split('|||')[0] for line in question['correct_answer'].split('\n')]

    if len(answers) == 1:
        correct = answers[0]
        wrongs = _distractors_for(correct, bank_pool, rng)
        # 沒有空格標記的題目屬「直接作答」型（如：輸出是多少？）
        prompt = ('\n\n空格 __1__ 應填入下列何者？' if '__1__' in question['content']
                  else '\n\n答案是下列何者？')
    else:
        correct = '、'.join(answers)
        alt_sets = [_distractors_for(a, bank_pool, rng) for a in answers]
        wrongs = []
        # 經典錯位組合：改第一格、改第二格、全改
        combos = [
            [alt_sets[0][0]] + answers[1:],
            answers[:-1] + [alt_sets[-1][0]],
            [alt_sets[i][min(1, len(alt_sets[i]) - 1)] for i in range(len(answers))],
        ]
        for combo in combos:
            text = '、'.join(combo)
            if text != correct and text not in wrongs:
                wrongs.append(text)
        i = 0
        while len(wrongs) < 3:  # 補足（避免湊巧重複）
            filler = '、'.join([alt_sets[0][i % 3]] + [alt_sets[j][(i + 1) % 3] for j in range(1, len(answers))])
            if filler != correct and filler not in wrongs:
                wrongs.append(filler)
            i += 1
        nums = '、'.join(str(i) for i in range(1, len(answers) + 1))
        prompt = f'\n\n空格 {nums} 依序應填入下列何者？'

    return {
        'type': 'multiple_choice',
        'content': question['content'] + prompt,
        'choices': [(correct, True), *[(w, False) for w in wrongs]],
        'explanation': question.get('explanation', ''),
    }


def _all_mc(bank):
    pool = []
    for q in bank:
        if q['type'] == 'fill_blank':
            pool.extend(line.split('|||')[0] for line in q['correct_answer'].split('\n'))
    return [q if q['type'] == 'multiple_choice' else fb_to_mc(q, pool) for q in bank]


# 部分單元先行改版；未列在此的單元沿用 curriculum_questions.py 舊題庫。
# 全選擇制：填空題於載入時轉為選擇題。
from .curriculum_u2 import U2_L1, U2_L2, U2_L3  # noqa: E402
from .curriculum_u3 import U3_L1, U3_L2, U3_L3  # noqa: E402
from .curriculum_u4 import U4_L1, U4_L2, U4_L3  # noqa: E402
from .curriculum_u5 import U5_L1, U5_L2, U5_L3  # noqa: E402
from .curriculum_u6 import U6_L1, U6_L2, U6_L3  # noqa: E402
from .curriculum_u7 import U7_L1, U7_L2, U7_L3  # noqa: E402

MIXED_BANKS = {
    ('beginner', 1): _all_mc(U1_L1),
    ('intermediate', 1): _all_mc(U1_L2),
    ('advanced', 1): _all_mc(U1_L3),
    ('beginner', 2): _all_mc(U2_L1),
    ('intermediate', 2): _all_mc(U2_L2),
    ('advanced', 2): _all_mc(U2_L3),
    ('beginner', 3): _all_mc(U3_L1),
    ('intermediate', 3): _all_mc(U3_L2),
    ('advanced', 3): _all_mc(U3_L3),
    ('beginner', 4): _all_mc(U4_L1),
    ('intermediate', 4): _all_mc(U4_L2),
    ('advanced', 4): _all_mc(U4_L3),
    ('beginner', 5): _all_mc(U5_L1),
    ('intermediate', 5): _all_mc(U5_L2),
    ('advanced', 5): _all_mc(U5_L3),
    ('beginner', 6): _all_mc(U6_L1),
    ('intermediate', 6): _all_mc(U6_L2),
    ('advanced', 6): _all_mc(U6_L3),
    ('beginner', 7): _all_mc(U7_L1),
    ('intermediate', 7): _all_mc(U7_L2),
    ('advanced', 7): _all_mc(U7_L3),
}
