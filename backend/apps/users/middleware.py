"""
StripEmbeddedParamMiddleware
============================
讓 Django admin 不要把 ?embedded=1 當成欄位過濾條件。

問題：admin-shell 用 iframe 載入 /admin/?embedded=1，前端 JS 用這個 query param
判斷是否進入 embedded 模式（隱藏 header、樣式縮排等）。但 Django admin 的 ChangeList
會把所有不認識的 query param 當成欄位過濾器，於是 QuizAttempt 因為沒有 `embedded`
欄位，被當成 IncorrectLookupParameters 拋錯，跳到「資料庫錯誤」頁。

解法：在 admin 路徑下，從 request.GET 拿掉 `embedded`，URL 上保留以便前端 JS 讀取。
"""


class StripEmbeddedParamMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 只對 admin 路徑生效
        if request.path.startswith('/admin/') and 'embedded' in request.GET:
            get = request.GET.copy()  # QueryDict 是不可變，需要 copy 才能改
            get.pop('embedded', None)
            request.GET = get
        return self.get_response(request)
