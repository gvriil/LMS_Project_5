from rest_framework.pagination import PageNumberPagination

class MaterialsPagination(PageNumberPagination):
    page_size = 5  # количество элементов на странице по умолчанию
    page_size_query_param = 'page_size'  # параметр для изменения размера страницы
    max_page_size = 20  # максимальное количество элементов на странице