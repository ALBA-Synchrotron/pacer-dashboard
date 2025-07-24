from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response


class StatusView(GenericAPIView):

    def get(self, request) -> Response:
        return Response({"status": "ok"}, status=status.HTTP_200_OK)
