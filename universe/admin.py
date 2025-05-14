from django.contrib import admin
from .models import (
    Lecture,
    Quiz,
    Question,
    Choice,
    QuizSubmission,
    Answer,
    Timetable
)

@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'lecture', 'created_at')
    list_filter = ('lecture',)
    search_fields = ('title',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz')
    list_filter = ('quiz',)
    search_fields = ('text',)


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')
    list_filter = ('is_correct', 'question')
    search_fields = ('text',)


@admin.register(QuizSubmission)
class QuizSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'submitted_at')
    list_filter = ('quiz', 'submitted_at')
    search_fields = ('user__username',)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('submission', 'question', 'selected_choice')
    list_filter = ('question',)
    search_fields = ('submission__user__username',)


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'uploaded_at')
    list_filter = ('type',)
    search_fields = ('title',)
