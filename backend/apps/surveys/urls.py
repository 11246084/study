from django.urls import path
from .views import ScaleListView, ScoreGridView, ScoreBatchView, ScoreImportView

urlpatterns = [
    path('scales/', ScaleListView.as_view(), name='survey-scales'),
    path('scores/', ScoreGridView.as_view(), name='survey-score-grid'),
    path('scores/batch/', ScoreBatchView.as_view(), name='survey-score-batch'),
    path('scores/import/', ScoreImportView.as_view(), name='survey-score-import'),
]
