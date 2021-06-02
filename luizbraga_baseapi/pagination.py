from rest_framework import pagination
from rest_framework.response import Response


class ApiPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'pages': self.page.paginator.num_pages,
            'previous': self.get_previous_link(),
            'next': self.get_next_link(),
            'results': data
        })
