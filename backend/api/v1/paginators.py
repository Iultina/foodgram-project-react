from rest_framework.pagination import PageNumberPagination

PAGE_NUMBERS = 6


class CustomPagination(PageNumberPagination):
    page_size = PAGE_NUMBERS
