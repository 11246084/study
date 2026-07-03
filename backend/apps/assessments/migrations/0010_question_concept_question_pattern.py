from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('assessments', '0009_alter_question_correct_answer_and_more')]
    operations = [
        migrations.AddField(model_name='question', name='concept', field=models.CharField(blank=True, db_index=True, max_length=80, verbose_name='概念標籤')),
        migrations.AddField(model_name='question', name='pattern', field=models.CharField(blank=True, db_index=True, max_length=80, verbose_name='題型模式')),
    ]
