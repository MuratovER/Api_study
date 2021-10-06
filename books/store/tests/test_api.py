import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.book_1 = Book.objects.create(name="Test Book 1", price='25',
                                          author_name='Author 1', owner=self.user)
        self.book_2 = Book.objects.create(name="Test Book 2", price='50',
                                          author_name='Author 2')
        self.book_3 = Book.objects.create(name="Test Book 3", price='100',
                                          author_name='Author 3')
        self.book_4 = Book.objects.create(name="Test Book Author 1", price='150',
                                          author_name='Author 4')

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        serializer_data = BookSerializer([self.book_1, self.book_2,
                                          self.book_3, self.book_4], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price': '50'})
        serializer_data = BookSerializer([self.book_2], many=True).data
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author 1'})
        serializer_data = BookSerializer([self.book_1, self.book_4], many=True).data
        self.assertEqual(serializer_data, response.data)

    # def test_get_ordering(self):
    #     url = reverse('book-list')
    #     response = self.client.get(url, data={'ordering':50})
    #     serializer_data = BookSerializer([self.book_1], many=True).data
    #     self.assertEqual(serializer_data, response.data)

    def test_create(self):
        self.assertEqual(4, Book.objects.all().count())
        url = reverse('book-list')
        data = {
            "name": "Programming in Python 3",
            "price": 150,
            "author_name": "Mark Summer",
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data, content_type = 'application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(5, Book.objects.all().count())
        self.assertEqual(self.user,Book.objects.last().owner)


    def test_update(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 50,
            "author_name": self.book_1.author_name,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, content_type = 'application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db() #self.book_1.refresh_from_db() эквивалентны self.book_1 = Book.objects.get(id=self.book_1.id)
        self.assertEqual(50, self.book_1.price)

    def test_update_not_owner(self):
        self.user2 = User.objects.create(username="testuser2")
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 50,
            "author_name": self.book_1.author_name,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, content_type = 'application/json')
        self.assertEqual(response.data, {'detail':
                                            ErrorDetail(string='You do not have permission to perform this action.',
                                            code='permission_denied')})
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.book_1.refresh_from_db() #self.book_1.refresh_from_db() эквивалентны self.book_1 = Book.objects.get(id=self.book_1.id)
        self.assertEqual(25, self.book_1.price)

    def test_delete(self):
        self.assertEqual(4, Book.objects.all().count())
        url = reverse('book-detail', args=(self.book_1.id,))
        self.client.force_login(self.user)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(3, Book.objects.all().count())

    def test_delete_not_owner(self):
        self.user2 = User.objects.create(username="testuser2")
        self.assertEqual(4, Book.objects.all().count())
        url = reverse('book-detail', args=(self.book_1.id,))
        self.client.force_login(self.user2)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(4, Book.objects.all().count())


    def test_update_not_owner_but_staff(self):
        self.user2 = User.objects.create(username="testuser2",
                                         is_staff=True)
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 50,
            "author_name": self.book_1.author_name,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, content_type = 'application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db() #self.book_1.refresh_from_db() эквивалентны self.book_1 = Book.objects.get(id=self.book_1.id)
        self.assertEqual(50, self.book_1.price)


class BookRelationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.user2 = User.objects.create(username="testuser2")
        self.book_1 = Book.objects.create(name="Test Book 1", price='25',
                                          author_name='Author 1', owner=self.user)
        self.book_2 = Book.objects.create(name="Test Book 2", price='50',
                                          author_name='Author 2')

    def test_like(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))

        data = {
            "like": True,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type = 'application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertTrue(relation.like)


    def in_bookmarks(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))

        data = {
            "like": True,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type = 'application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertTrue(relation.like)

    def test_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))

        data = {
            "rate": 3,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type = 'application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertEqual(3, relation.rate)


    def test_rate_wrong(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))

        data = {
            "rate": 9,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type = 'application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)

