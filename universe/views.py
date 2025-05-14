# views.py
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Lecture, Quiz, Question, Choice, QuizSubmission, Answer, Timetable
from .serializers import (
    LectureSerializer, QuizSerializer, QuestionSerializer, ChoiceSerializer,
    QuizSubmissionSerializer, AnswerSerializer, TimetableSerializer
)

class LectureViewSet(viewsets.ModelViewSet):
    queryset = Lecture.objects.all()
    serializer_class = LectureSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class QuizSubmissionViewSet(viewsets.ModelViewSet):
    queryset = QuizSubmission.objects.all()
    serializer_class = QuizSubmissionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        submission_id = response.data.get("id")
        submission = QuizSubmission.objects.get(id=submission_id)
        answers = submission.answers.all()
        total_questions = answers.count()
        correct_answers = sum(1 for answer in answers if answer.selected_choice and answer.selected_choice.is_correct)

        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        submission.score = score
        submission.save()

        response.data["score"] = score
        response.data["correct_answers"] = correct_answers
        response.data["total_questions"] = total_questions
        return response


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticated]


class TimetableViewSet(viewsets.ModelViewSet):
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
