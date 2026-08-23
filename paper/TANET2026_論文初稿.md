# 結合形成性評量之程式設計適性學習輔助系統之設計與研究

**A Formative-Assessment-Driven Adaptive Learning Support System for Programming Education: Design and Study**

作者一 1，作者二 2，作者三 3，作者四(通訊作者) 4, *
國立臺北商業大學資訊管理系 1,2,3,4
E-mail 1, E-mail 2, E-mail 3, E-mail 4, *

---

## 摘要

程式設計為資訊領域之基礎能力，然而初學者常因錯誤概念、程式執行流程理解不足與除錯困難而產生挫折與學習焦慮，進而影響學習動機與學習表現。為回應傳統教材固定進度與單一難度難以因應個別差異之問題，本研究以程式設計學習為情境，設計並實作一套以形成性評量為核心之程式設計適性學習輔助系統（AdaptLearn）。系統將課程切分為 8 個單元 × 3 個難易度等級，學生於每一單元完成學習活動後進行單元形成性評量，系統依作答結果即時計算下一單元之教材等級（≥80 分升級、<60 分降級、60–79 分維持），並同步產生單元內的「挑戰進階／補救複習」推薦，形成「學習活動→形成性評量→表現分級→教材調整→循環學習」之調整迴圈；同時納入錯誤可復原、錯誤正常化訊息、學習進度可視化、低風險小任務切割及友善訊息回饋等五項情意支持設計，以降低程式學習焦慮。研究採前測／後測之準實驗設計，以國立臺北商業大學資訊管理系日間部四技一年級學生為對象，分為實驗組（使用本系統）與控制組（固定教材），施測學習成效測驗、情境動機量表（SIMS）、程式設計學習焦慮問卷與系統可用性量表（SUS），並輔以系統所蒐集之學習歷程事件資料進行分析。研究結果顯示【待補】。本研究可驗證形成性評量導向之教材難易度動態調整機制之可行性與效益，並提出兼顧學習成效與情意支持之程式設計教材設計參考。

**關鍵詞**：形成性評量、適性學習、學習成效、學習動機、程式設計

## Abstract

Programming is a fundamental competency in information-related disciplines, yet novices frequently encounter misconceptions, an incomplete mental model of program execution, and debugging difficulties, which lead to frustration and programming anxiety and in turn undermine learning motivation and performance. To address the limitation that conventional materials follow a fixed pace at a single difficulty level, this study designs and implements AdaptLearn, a formative-assessment-driven adaptive learning support system for programming. The curriculum is organized into eight units at three difficulty levels; after each unit quiz the system computes the difficulty level of the next unit (level up when the score is at least 80, level down when below 60, unchanged between 60 and 79) and simultaneously issues a within-unit recommendation for either an advanced challenge or a remedial review, forming a closed adjustment loop of learning activity, formative assessment, performance grading, material adjustment, and iteration. Five affective-support designs — error recoverability, error-normalizing messages, progress visualization, low-stakes task decomposition, and friendly feedback — are embedded to reduce programming anxiety. A quasi-experimental pretest–posttest design was conducted with first-year students of the Department of Information Management, National Taipei University of Business, assigned to an experimental group using the system and a control group using fixed materials. Learning achievement tests, the Situational Motivation Scale, a programming anxiety questionnaire, and the System Usability Scale were administered, complemented by learning-process event logs collected by the system. The results indicate [to be completed]. The study verifies the feasibility of formative-assessment-driven difficulty adjustment and offers design references that balance learning outcomes with affective support.

**Keywords**: formative assessment, adaptive learning, learning achievement, learning motivation, programming education

---

## 1. 前言

隨著資訊科技與網路應用的快速發展，程式設計已成為資訊相關領域中不可或缺的基礎能力。然而，對多數初學者而言，程式設計學習同時涉及英文理解、抽象邏輯推理與語法及語意整合等多重認知歷程，使學習初期容易產生錯誤概念、流程理解不足與除錯困難，進而引發挫折感與學習焦慮，影響其學習動機與學習表現 [14][15]。

傳統程式設計教材多以靜態文字、範例程式碼或影片說明為主，雖可傳遞基本知識，卻較難即時回應學生在學習歷程中所呈現的個別差異。當教材難易度未能配合學生當下的理解程度時，學生往往難以順利銜接理論與實作，進而降低學習投入與持續學習意願。近年教育科技研究指出，結合互動式數位教材 [18]、形成性評量與即時回饋機制 [12]，有助於降低程式學習初期的理解門檻，並改善學生的學習動機與情意反應；然而多數現行教材仍採固定進度與單一難度設計，缺乏具體且可操作的教材難易度評量與調整機制。

基於上述背景，本研究以程式設計學習為情境，聚焦於形成性評量導向之教材難易度調整機制，設計並實作「程式設計適性學習輔助系統」（AdaptLearn），並以準實驗方式探討其對學生學習成效、學習動機與學習焦慮之影響。具體研究問題如下：

- RQ1：教材難易度調整機制是否能影響學生在程式設計學習中的學習成效？
- RQ2：教材難易度調整機制是否能影響學生在程式設計學習中的學習動機？
- RQ3：教材難易度調整機制是否能影響學生在程式設計學習中的學習焦慮程度？
- RQ4：學生的學習動機與學習焦慮是否與其程式設計學習成效存在顯著關係？

本文其餘章節安排如下：第 2 節回顧程式設計學習困難、教材設計與情意變項之相關研究；第 3 節說明本系統之架構、適性調整機制與情意支持設計；第 4 節說明研究方法；第 5 節呈現研究結果；第 6 節為討論；第 7 節為結論與未來工作。

## 2. 文獻探討

### 2.1 程式設計學習在傳統教學模式下的挑戰

程式設計長期被視為初學者學習歷程中具高度挑戰性的學習領域。Qian 與 Lehman [15] 之系統性文獻回顧指出，初學者普遍存在對變數、控制結構與程式執行流程的錯誤概念，進而影響其對程式行為的理解。即便以語法相對簡潔的 Python 作為入門語言，學生仍可能因無法建立正確的程式執行心智模型，而對程式語意產生錯誤理解 [9]。此外，即使在圖形化或積木式程式設計環境中，初學者對迴圈、變數與邏輯運算等核心概念仍存在顯著誤解，顯示學習困難並非僅源於語言形式，而與概念理解本身密切相關 [4]。

當學生遭遇錯誤時，若缺乏有效判斷錯誤來源與修正策略的能力，問題往往無法即時解決，挫折感隨之累積。相關研究 [11][23] 指出，初學者對程式語言行為的理解偏誤，使除錯成為高度困難的認知任務，即使完成程式任務，亦可能未能真正理解其解題歷程與背後邏輯。上述困境在教材設計未能配合學生理解狀態時往往被進一步放大：教材結構過於複雜或說明不足，將提高學生的認知負荷，阻礙理解與持續投入 [6]；相對地，具備引導機制與適當表徵方式的教材設計，有助於降低學習負擔並協助學生逐步建構概念理解 [8]。此觀點亦呼應自我調整學習研究所強調之學習環境支持角色 [17]。

### 2.2 教材設計對程式設計學習的影響

相較於以靜態文字與單向說明為主的傳統教材，具備互動性與引導結構的教材設計，被認為有助於降低初學者理解程式概念時的認知負荷。Tikva 與 Tambouris [19] 指出，透過鷹架設計將複雜概念拆解為可逐步掌握的學習活動，有助於學生建立較穩定的概念理解基礎並提升學習投入。Shin 等人 [16] 則透過 worked-out example 搭配後設認知鷹架的教材設計，使學生能觀察解題步驟並反思決策過程，進而提升程式問題解決能力。

隨著教育科技發展，具備學習建議與內容調整機制的自適應系統，能依據學生的學習表現動態調整教材內容與難度，使學生在可接受的挑戰範圍內持續學習，進而提升學習成效並降低學習負荷 [10][22]；近年研究亦顯示此類設計在學習理解與學習動機上具正向影響 [3][13]。然而文獻亦指出，教材若僅以固定進度與單一難度呈現，或缺乏結構化引導，將難以回應個別差異，甚至加重認知負荷。是故，自適應教材設計的關鍵不僅在於形式多樣化，更在於是否具備可即時反映學生學習狀態的評量依據，並據此動態調整教材內容與難度——此即本研究以形成性評量作為調整依據之理論基礎。

### 2.3 學習動機與學習焦慮對程式設計學習的影響

除教材設計外，學習動機與學習焦慮亦為影響學習成效的重要情意因素。近年研究顯示，學習動機與程式學習成效呈正向關係，而程式學習焦慮則與學習成效呈負向關聯 [2]。依據自我決定理論，當學習者能感受到興趣、自主性與學習價值時，較能維持學習投入並面對學習挑戰 [5]；應用於程式設計情境，教材若能降低理解門檻、提升操作可行性並提供清楚引導，有助於促進學習動機。科技學習相關研究亦指出，教材的知覺易用性與學習流暢度能降低負向情緒反應並提升學習投入 [20][21]。

相較之下，程式學習焦慮常源於學生對錯誤的恐懼、對自身能力的不確定感及對程式結果不可預測性的擔憂 [14]；透過具備引導與低門檻特性的教材設計，有助於降低初學者的學習焦慮 [7]。綜合而言，教材設計可透過提升學習動機並降低學習焦慮，進而促進整體程式設計學習成效。

### 2.4 小結

綜合文獻可知，初學者的學習困難不僅源於語法學習，亦涉及錯誤概念形成、程式語意理解不足、心智模型建構困難與錯誤修正策略不足；在固定進度與單一難度的教材模式下，這些困境難以獲得即時回應。既有適性學習研究多聚焦於模型或演算法層面，對於「可落地於實際課堂之調整機制」與「情意因素變化」之實證資料仍相對不足。本研究因此在既有基礎上，以形成性評量作為難易度調整的判準，於實際課堂情境中驗證其可行性與初步成效。

## 3. 系統設計與實作

### 3.1 系統架構

本研究所提出之程式設計適性學習輔助系統採前後端同源之網頁架構實作：後端以 Python Django 5.2 與 Django REST Framework 建置 RESTful API，身分驗證採 JSON Web Token，資料儲存採用 MySQL；前端以 HTML／CSS／JavaScript 撰寫，由 Django 直接提供靜態頁面，學生僅需瀏覽器即可使用，無須安裝額外環境。

系統由四個核心模組組成（如圖 1）：

1. **學習活動模組**：提供依難易度分級之教材內容與教學資源，包含程式概念說明與範例程式，作為學生進行程式學習之主要介面。
2. **評量與回饋模組**：於單元教材後提供單元測驗作為形成性評量工具，即時批改並回饋作答結果，評量構面涵蓋程式語意與執行流程理解、程式結構與邏輯應用，以及錯誤辨識與除錯理解能力。
3. **學習歷程資料庫**：儲存學習紀錄、作答結果與教材等級變化，並以事件層級記錄學生於系統中的細部操作。
4. **資料回饋分析模組**：彙整與分析學習歷程資料，產出教師端儀表板與分析結果，並回饋至教材調整機制，使難易度調整能兼顧系統自動化與教師教學彈性。

> 【圖 1 位置】系統架構圖（沿用計畫書「圖一、系統架構圖」，請置於單欄或跨欄置中，圖說置於圖下方）

### 3.2 課程結構與分級教材

課程內容依教學進度切分為 8 個單元，涵蓋基礎語法與輸入輸出、條件判斷、迴圈與演算法、迴圈實作練習、串列與字串、串列與字串實作練習、函式，以及遞迴與字典。每一單元皆備有 Level 1（基礎）、Level 2（標準）、Level 3（進階）三種難易度版本之教材與對應測驗，三個等級之學習目標一致，差異在於概念說明的鋪陳密度、範例程式的複雜度與練習任務的認知層次。

單元之開放與否由授課教師透過管理介面手動控制，教師於每日課程結束後開放當日單元，以確保系統學習進度與實際課堂教學同步；已作答之單元則持續開放供學生複習。

### 3.3 形成性評量與適性調整機制

每一單元測驗自該單元該等級之題庫中由伺服器端隨機抽取 10 題，題庫規模為每單元每等級 100 題，抽取結果寫入作答紀錄，後續作答與查詢 API 皆以該題組為界，避免題目外洩並降低不同學生間互相參照的可能。題型以選擇題與程式填空題混合設計，並依等級調整比重：Level 1 以選擇題為主（約 7:3）、Level 2 選擇與填空各半、Level 3 以程式填空為主（約 3:7），使三個等級的差異同時反映在內容難度與作答形式的認知需求上。

學生交卷後，系統立即計分並執行適性調整邏輯，此邏輯包含兩條並行路徑：

**（1）垂直路徑——學習進程調整。** 依本次測驗分數決定下一單元之教材等級 Lnext，如式 (1) 所示：

%%EQ%%Lnext = min(Lcur + 1, 3)，若 S ≥ 80
%%EQ%%Lnext = Lcur，若 60 ≤ S < 80
%%EQ%%Lnext = max(Lcur − 1, 1)，若 S < 60	(1)

其中 S 為本次單元測驗百分制分數，Lcur 為學生於本單元之教材等級，Lnext 為系統指派之下一單元教材等級。調整結果寫入學生之適性學習路徑紀錄，作為下一單元教材呈現之依據。

**（2）水平路徑——單元內推薦。** 系統同時針對本單元產生一則推薦卡片：分數 ≥ 80 且尚未達 Level 3 者，推薦同一單元的更高等級教材（「挑戰進階」）；分數 < 60 且尚未降至 Level 1 者，推薦同一單元的較低等級教材（「補救複習」）；60–79 分或已達等級上下限者，則推薦前往下一單元。當學生完成全部 8 個單元後，系統改以「等級最低、分數最低」為排序準則，挑選 3 個最弱單元產生複習推薦。

需說明的是，等級的自動調整僅決定「系統建議」的教材版本；學生於學習主頁的每一單元卡片上，仍可透過等級切換列自由存取該單元的三個等級，以兼顧適性引導與學習自主性。

### 3.4 情意支持設計

針對程式設計初學者常見之學習焦慮與挫折感，本系統於學習流程與介面設計中融入五項情意支持機制：

1. **錯誤可復原**：允許學生於作答錯誤後重試與修正，單元測驗可重複作答，不以單次表現定論。
2. **錯誤正常化訊息**：回饋訊息強調錯誤為學習歷程中之正常現象，並以中性描述取代負向評價用語，降低學生對錯誤之威脅感。
3. **學習進度可視化**：以單元卡片與狀態標示呈現各單元之完成情形與目前等級，協助學生掌握自身學習狀態。
4. **低風險小任務切割**：教材內容採低風險、小任務方式切割，單元測驗每次僅抽取 10 題，降低單次評量之心理負擔。
5. **友善訊息回饋**：以引導式語句說明後續建議行動（挑戰進階／補救複習／前往下一單元），使學生在每次評量後皆有明確且可執行的下一步。

### 3.5 學習歷程資料蒐集

為支援後續學習歷程分析，系統除彙總層（學生×單元之作答次數、最近分數、最佳分數、教材停留時間、目前等級）外，另設置唯讀之研究原始資料層，以事件為單位記錄學生操作，包含頁面瀏覽與關閉、教材開啟與關閉、測驗開啟、題目瀏覽、答案變更、交卷、中途放棄、推薦卡片點擊等事件類型。每筆事件記錄用戶端發生時間、所屬使用時段、分頁識別碼與作答內容全文，並以事件唯一識別碼於伺服器端去重；前端以佇列方式批次上傳，上傳失敗時保留於本機並於下次開啟頁面時補送，以降低資料遺漏。使用時段以 30 分鐘無活動為切分門檻，可用於計算學生之使用次數、使用時長與單次使用長度。上述資料作為解釋量化結果與後續系統優化之依據。

## 4. 研究方法

### 4.1 研究設計

本研究採前測／後測之準實驗研究設計，以程式設計適性學習輔助系統作為主要教學介入工具。於教學介入前，對實驗組與控制組學生實施前測，以了解學生在學習成效、學習動機與學習焦慮等面向之初始狀態；教學介入期間，實驗組學生於程式設計課程中使用本系統，系統依其形成性評量表現動態調整教材難易度，控制組學生則採用固定進度與單一難度之教材進行學習；教學介入結束後，對兩組學生實施後測，並透過組內前後測與組間差異之比較，分析系統在提升學習成效、促進學習動機及降低學習焦慮方面之成效。

### 4.2 研究對象

研究對象為國立臺北商業大學資訊管理系日間部四技一年級學生，該年級課程規劃中包含程式設計相關課程，學生具備一致的學習背景與學習需求。實驗組學生使用本系統進行課程學習；控制組學生則採用課本與簡報等傳統教材，以相同課程內容與學習任務進行學習。實際參與人數與分組情形為：實驗組 【N＝＿＿】 人、控制組 【N＝＿＿】 人，共 【N＝＿＿】 人。

### 4.3 研究工具

**（1）程式設計適性學習輔助系統**：如第 3 節所述。

**（2）學習成效評量**：由授課教師依課程內容與學習目標設計，涵蓋程式語意與執行流程理解、基本程式結構與邏輯應用，以及錯誤辨識與除錯相關概念；題型包含選擇題、概念理解題與簡易程式題。前後測依相同課程目標設計，採相同或等值題型以確保比較基礎，並輔以系統中之形成性評量成績作為過程性指標。

**（3）學習動機問卷**：採用 Guay 等人 [5] 之情境動機量表（SIMS），共 16 題，涵蓋內在動機、辨識調節、外在調節與無動機四個構面，採李克特五點量表計分。

**（4）學習焦慮問卷**：參考程式設計學習焦慮相關文獻與既有量表設計概念 [20][21] 編製，共 8 題，採李克特五點量表計分，其中反向題於計分時反向處理。

**（5）系統可行性量表**：採用 Brooke [1] 之系統可用性量表（SUS），共 10 題，採李克特五點量表計分，僅對實驗組於後測時施測，換算為 0–100 之 SUS 分數。

### 4.4 研究流程

研究流程涵蓋四個階段（如圖 2）：

- **前測**：於課程開始前對兩組學生實施學習成效前測、學習動機問卷與學習焦慮問卷。
- **教學介入**：以程式設計課程為教學情境，涵蓋前述 8 個單元之教材與形成性評量。實驗組使用本系統學習，系統依各單元形成性評量表現動態調整後續教材等級；控制組採一般課堂教學，教材為單一難度版本，教學過程中不依學習表現調整難易度。〔實際教學介入之期程與時數：【＿＿週，每週＿＿小時】〕
- **後測**：教學介入結束後實施學習成效後測、學習動機問卷、學習焦慮問卷，以及僅對實驗組施測之系統可用性問卷。
- **資料分析**：彙整前後測資料與系統學習歷程資料進行量化分析。

> 【圖 2 位置】研究流程圖（沿用計畫書「圖二、研究流程圖」，圖說置於圖下方）

### 4.5 資料分析方法

本研究以 【統計軟體：＿＿】 進行資料處理，顯著水準訂為 α = .05，分析方法如下：

1. **信度分析**：以 Cronbach's α 檢驗學習動機問卷、學習焦慮問卷與系統可用性量表之內部一致性。
2. **同質性檢驗**：以獨立樣本 t 檢定比較兩組前測之學習成效、學習動機與學習焦慮，確認教學介入前之起始狀態無顯著差異。
3. **學習成效分析**：以成對樣本 t 檢定檢驗各組前後測差異；以獨立樣本 t 檢定比較兩組後測差異；若前測存在顯著差異，改以前測分數為共變數進行單因子共變數分析（ANCOVA），並報告效果量（Cohen's d／偏 η²）。
4. **學習動機與學習焦慮分析**：依上述相同程序，分別就 SIMS 四個構面與焦慮量表總分進行分析。
5. **關聯分析**：以 Pearson 積差相關檢驗學習動機、學習焦慮與學習成效（後測分數與進步分數）之關聯，並視結果以多元迴歸進一步檢驗預測關係。
6. **系統體驗與可用性分析**：計算實驗組之 SUS 分數與各題平均，並輔以描述統計說明。
7. **學習歷程分析**：彙整實驗組於系統中之教材等級變化軌跡、單元作答次數、教材停留時間與使用時段分布，描述學生在不同教材等級下的學習表現變化與學習節點。

## 5. 研究結果

> **【本節待研究資料蒐集完成後填寫】** 以下小節與表格為預留骨架，請依實際統計結果補齊數值與文字說明；表格編號請與內文引用一致。

### 5.1 樣本描述與信度分析

【待補：說明有效樣本人數、性別／背景分布、無效問卷剔除標準，以及各量表之 Cronbach's α 值。】

**表 1 各量表信度分析**

| 量表 | 題數 | 前測 α | 後測 α |
|---|---|---|---|
| 學習動機（SIMS）－內在動機 | 4 | | |
| 學習動機（SIMS）－辨識調節 | 4 | | |
| 學習動機（SIMS）－外在調節 | 4 | | |
| 學習動機（SIMS）－無動機 | 4 | | |
| 程式設計學習焦慮 | 8 | | |
| 系統可用性量表（SUS） | 10 | － | |

### 5.2 前測同質性檢驗

【待補：說明兩組於前測之學習成效、學習動機與學習焦慮是否具同質性，並據以決定後續採 t 檢定或 ANCOVA。】

**表 2 兩組前測同質性檢驗**

| 變項 | 實驗組 M(SD) | 控制組 M(SD) | t | p |
|---|---|---|---|---|
| 學習成效 | | | | |
| 學習動機（總分） | | | | |
| 學習焦慮（總分） | | | | |

### 5.3 學習成效分析（對應 RQ1）

【待補：先報告各組前後測成對樣本 t 檢定結果，再報告組間比較（t 檢定或 ANCOVA）結果與效果量，並以文字說明實驗組是否顯著優於控制組。】

**表 3 學習成效前後測分析**

| 組別 | 前測 M(SD) | 後測 M(SD) | t | p | Cohen's d |
|---|---|---|---|---|---|
| 實驗組 | | | | | |
| 控制組 | | | | | |

**表 4 學習成效後測組間比較**

| 變項 | 實驗組 M(SD) | 控制組 M(SD) | t／F | p | 效果量 |
|---|---|---|---|---|---|
| 學習成效後測 | | | | | |

### 5.4 學習動機分析（對應 RQ2）

【待補：依 SIMS 四構面分別報告前後測變化與組間差異，特別說明內在動機與辨識調節是否提升、無動機是否降低。】

**表 5 學習動機各構面前後測分析**

| 構面 | 組別 | 前測 M(SD) | 後測 M(SD) | t | p |
|---|---|---|---|---|---|
| 內在動機 | 實驗組 | | | | |
| | 控制組 | | | | |
| 辨識調節 | 實驗組 | | | | |
| | 控制組 | | | | |
| 外在調節 | 實驗組 | | | | |
| | 控制組 | | | | |
| 無動機 | 實驗組 | | | | |
| | 控制組 | | | | |

### 5.5 學習焦慮分析（對應 RQ3）

【待補：報告兩組學習焦慮之前後測變化與組間差異，並連結至第 3.4 節之五項情意支持設計進行說明。】

**表 6 學習焦慮前後測分析**

| 組別 | 前測 M(SD) | 後測 M(SD) | t | p | Cohen's d |
|---|---|---|---|---|---|
| 實驗組 | | | | | |
| 控制組 | | | | | |

### 5.6 學習動機、學習焦慮與學習成效之關聯（對應 RQ4）

【待補：報告相關係數矩陣，說明學習動機與學習成效之正向關聯、學習焦慮與學習成效之負向關聯是否成立；如有進行迴歸分析，補充說明預測力。】

**表 7 各變項之相關係數矩陣（N＝＿＿）**

| 變項 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| 1. 學習成效（後測） | － | | | |
| 2. 學習動機 | | － | | |
| 3. 學習焦慮 | | | － | |
| 4. 形成性評量平均 | | | | － |

### 5.7 系統可用性分析

【待補：報告 SUS 總分與等第判讀，並摘述得分較高與較低之題項所反映的使用經驗。】

**表 8 系統可用性量表（SUS）結果**

| 項目 | M(SD) |
|---|---|
| SUS 總分（0–100） | |
| 得分最高之三題 | |
| 得分最低之三題 | |

### 5.8 學習歷程分析

【待補：依系統紀錄描述實驗組學生之教材等級變化軌跡（升級／降級／維持之人次與比例）、各單元平均作答次數與教材停留時間、推薦卡片點擊率，並指出出現較多降級或重複作答之單元（學習節點）。】

**表 9 各單元教材等級調整結果與學習歷程指標**

| 單元 | 升級人次 | 維持人次 | 降級人次 | 平均分數 | 平均作答次數 | 平均教材停留時間 |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |
| 6 | | | | | | |
| 7 | | | | | | |
| 8 | | | | | | |

## 6. 討論

> **【本節待研究結果確定後撰寫】** 建議依下列脈絡展開：

- **6.1 教材難易度動態調整對學習成效之意涵**：【待補：連結第 5.3 節結果與文獻 [3][10][13] 之發現，說明本研究之一致或相異之處及可能原因。】
- **6.2 適性機制與情意支持對動機與焦慮之作用**：【待補：連結第 5.4、5.5 節結果與自我決定理論 [5] 及焦慮相關研究 [7][14]。】
- **6.3 情意變項與學習成效之關係**：【待補：連結第 5.6 節結果與 Chang 等人 [2] 之發現，討論「教材調整→改善情意狀態→提升學習成效」之可能路徑。】
- **6.4 學習歷程資料所揭示的教學意涵**：【待補：由第 5.8 節指出之學習節點，提出單元教材與題庫之修正建議。】
- **6.5 研究限制**：【待補：例如樣本為單一校系之便利取樣、教學介入期程有限、未採隨機分派、學習成效測驗之等值性等。】

## 7. 結論與未來工作

本研究設計並實作一套以形成性評量為核心之程式設計適性學習輔助系統，將課程切分為 8 個單元 × 3 個難易度等級，並以單元測驗成績同時驅動「下一單元教材等級」與「單元內挑戰／補救推薦」兩條調整路徑，形成可於實際課堂運作之教材調整迴圈；同時將五項情意支持設計融入學習流程，以回應程式設計初學者的焦慮與挫折經驗。系統並以事件層級記錄學習歷程，使教材調整之成效可被量化檢視。

在實證方面，本研究以準實驗設計比較實驗組與控制組於學習成效、學習動機與學習焦慮之差異，研究結果顯示【待補：以三至五句摘述主要發現，並回應 RQ1–RQ4】。

本研究之貢獻包括：（1）提出一套可在程式設計課程中實施的流程化設計（學習活動→形成性評量→表現分級→教材調整→版本更新→循環學習），作為未來教材與課程設計之參考架構；（2）提出可移植之「降低程式學習焦慮」系統化設計策略；（3）累積適性學習介入於程式設計教育之實證資料，補足現有研究中對於可落地之調整機制與情意因素變化之實證缺口。

未來工作方向包括：擴大樣本與跨校系驗證、延長教學介入期程以觀察長期效果、引入更細緻的能力診斷模型（如知識追蹤）以取代單一分數門檻、以及依學習歷程分析結果持續優化分級教材與題庫。

## 誌謝

【待補：如有計畫補助或單位協助，請於此致謝。】

## 參考文獻

[1] J. Brooke, "SUS-A quick and dirty usability scale," *Usability Evaluation in Industry*, vol. 189, no. 194, pp. 4–7, 1996.

[2] L. C. Chang, H. R. Lin, and J. W. Lin, "Learning motivation, outcomes, and anxiety in programming courses—A computational thinking–centered method," *Education and Information Technologies*, vol. 29, no. 1, pp. 545–569, 2024.

[3] K. Chrysafiadi, M. Virvou, G. A. Tsihrintzis, and I. Hatzilygeroudis, "Evaluating the user's experience, adaptivity and learning outcomes of a fuzzy-based intelligent tutoring system for computer programming for academic students in Greece," *Education and Information Technologies*, vol. 28, no. 6, pp. 6453–6483, 2023.

[4] S. Grover and S. Basu, "Measuring student learning in introductory block-based programming: Examining misconceptions of loops, variables, and boolean logic," in *Proceedings of the 2017 ACM SIGCSE Technical Symposium on Computer Science Education*, 2017, pp. 267–272.

[5] F. Guay, R. J. Vallerand, and C. Blanchard, "On the assessment of situational intrinsic and extrinsic motivation: The Situational Motivation Scale (SIMS)," *Motivation and Emotion*, vol. 24, pp. 175–213, 2000.

[6] X. Hao, Z. Xu, M. Guo, Y. Hu, and F. Geng, "The effect of embedded structures on cognitive load for novice learners during block-based code comprehension," *International Journal of STEM Education*, vol. 10, no. 1, p. 42, 2023.

[7] Y. Y. He, C. K. Chang, and B. J. Liu, "Teaching computer programming for freshmen: A study on using scratch as remedial teaching," *International Journal on Digital Learning Technology*, vol. 2, no. 1, pp. 11–32, 2010.

[8] D. Hooshyar, R. B. Ahmad, M. Yousefi, F. D. Yusop, and S. J. Horng, "A flowchart-based intelligent tutoring system for improving problem-solving skills of novice programmers," *Journal of Computer Assisted Learning*, vol. 31, no. 4, pp. 345–361, 2015.

[9] F. Johnson, S. McQuistin, and J. O'Donnell, "Analysis of student misconceptions using Python as an introductory programming language," in *Proceedings of the 4th Conference on Computing Education Practice*, 2020, pp. 1–4.

[10] H. C. Ling and H. S. Chiang, "Learning performance in adaptive learning systems: A case study of web programming learning recommendations," *Frontiers in Psychology*, vol. 13, 770637, 2022.

[11] K. C. Lu and S. Krishnamurthi, "Identifying and correcting programming language behavior misconceptions," *Proceedings of the ACM on Programming Languages*, vol. 8, no. OOPSLA1, pp. 334–361, 2024.

[12] M. Messer, N. C. Brown, M. Kölling, and M. Shi, "Automated grading and feedback tools for programming education: A systematic review," *ACM Transactions on Computing Education*, vol. 24, no. 1, pp. 1–43, 2024.

[13] L. Na Nongkhai, J. Wang, and T. Mendori, "Development and evaluation of adaptive learning support system based on ontology of multiple programming languages," *Education Sciences*, vol. 15, no. 6, p. 724, 2025.

[14] K. Nolan and S. Bergin, "The role of anxiety when learning to program: A systematic review of the literature," in *Proceedings of the 16th Koli Calling International Conference on Computing Education Research*, 2016, pp. 61–70.

[15] Y. Qian and J. Lehman, "Students' misconceptions and other difficulties in introductory programming: A literature review," *ACM Transactions on Computing Education*, vol. 18, no. 1, pp. 1–24, 2017.

[16] Y. Shin, J. Jung, J. Zumbach, and E. Yi, "The effects of worked-out example and metacognitive scaffolding on problem-solving programming," *Journal of Educational Computing Research*, vol. 61, no. 6, pp. 1312–1331, 2023.

[17] L. Silva, A. Mendes, A. Gomes, and G. Fortes, "What learning strategies are used by programming students? A qualitative study grounded on the self-regulation of learning theory," *ACM Transactions on Computing Education*, vol. 24, no. 1, pp. 1–26, 2024.

[18] J. Swacha, R. Queirós, and J. C. Paiva, "Towards a framework for gamified programming education," in *2019 International Symposium on Educational Technology (ISET)*, 2019, pp. 144–149.

[19] C. Tikva and E. Tambouris, "The effect of scaffolding programming games and attitudes towards programming on the development of computational thinking," *Education and Information Technologies*, vol. 28, no. 6, pp. 6845–6867, 2023.

[20] V. Venkatesh, "Determinants of perceived ease of use: Integrating control, intrinsic motivation, and emotion into the technology acceptance model," *Information Systems Research*, vol. 11, no. 4, pp. 342–365, 2000.

[21] L. C. Wang and M. P. Chen, "The effects of game strategy and preference-matching on flow experience and programming performance in game-based learning," *Innovations in Education and Teaching International*, vol. 47, no. 1, pp. 39–52, 2010.

[22] G. Weber and M. Specht, "User modeling and adaptive navigation support in WWW-based tutoring systems," in *User Modeling: Proceedings of the Sixth International Conference UM97*, 1997, pp. 289–300.

[23] K. Woo and G. Falloon, "Problem solved, but how? An exploratory study into students' problem solving processes in creative coding tasks," *Thinking Skills and Creativity*, vol. 46, 101193, 2022.
