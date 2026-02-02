from datetime import date
import shutil
from django.test import Client, TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from bookapp.forms import BookForm
from bookapp.models import Author, Book

# Create your tests here.
class BookModelTest(TestCase):
    def test_correct_book(self):
        book = Book.objects.create(
            title = 'Mi libro',
            pages = 99,
            rating = 4,
            status = 'RE',
            published_date = date(2026, 1, 1)
        )
        book.full_clean()
        self.assertEqual(book.title, 'Mi libro')
        self.assertEqual(book.rating, 4)
        self.assertEqual(book.published_date, date(2026, 1, 1))
    
    def test_wrong_pages(self):
        book = Book.objects.create(
            title = 'Mi libro',
            pages = 0,
            rating = 4,
            status = 'RE',
            published_date = date(2026, 1, 1)
        )
        with self.assertRaises(Exception):
            book.full_clean()
    
    def test_wrong_rating(self):
        book = Book.objects.create(
            title = 'Mi libro',
            pages = 99,
            rating = 6,
            status = 'RE',
            published_date = date(2026, 1, 1)
        )
        with self.assertRaises(Exception):
            book.full_clean()
    
    def test_wrong_read_date(self):
        book = Book.objects.create(
            title = 'Mi libro',
            pages = 99,
            rating = 4,
            status = 'RE',
            published_date = date(2026, 1, 1),
            read_date = date(2025, 12, 1)
        )
        with self.assertRaises(Exception):
            book.full_clean()
    
    def test_with_author(self):
        author = Author.objects.create(
            name = 'Federico',
            last_name = 'García'
        )
        book = Book.objects.create(
            title = 'Mi libro',
            pages = 99,
            rating = 4,
            status = 'RE',
            published_date = date(2026, 1, 1)
        )
        book.authors.add(author)
        book.full_clean()
        self.assertEqual(book.title, 'Mi libro')
        self.assertEqual(book.rating, 4)
        self.assertEqual(book.published_date, date(2026, 1, 1))
        self.assertIn(author, book.authors.all())
    
    def test_with_cover(self):
        cover = SimpleUploadedFile(
            name = 'cover.jpg',
            content = b'My content',
            content_type = 'image/jpeg'
        )
        book = Book(
            title = 'Mi libro',
            pages = 99,
            rating = 4,
            status = 'RE',
            published_date = date(2026, 1, 1),
            cover_image = cover
        )
        book.full_clean()
        self.assertEqual(book.title, 'Mi libro')
        self.assertEqual(book.rating, 4)
        self.assertEqual(book.published_date, date(2026, 1, 1))
        self.assertEqual(book.cover_image.name, 'cover.jpg')

@override_settings(MEDIA_ROOT='testfiles')
class BookFormTest(TestCase):
    def test_correct_book(self):
        form = BookForm(
            {
                "title": "Legado maldito",
                "pages": 100,
                "rating": 5,
                "status": "RE",
                "published_date": date(2015, 1, 1)
            }
        )
        self.assertTrue(form.is_valid())
        book = form.save()
        self.assertEqual(book.title, "Legado maldito")
        self.assertEqual(book.rating, 5)
        self.assertEqual(book.published_date, date(2015, 1, 1))
    
    def test_more_than_50(self):
        form = BookForm(
            {
                "title": "Pepito" * 50,
                "pages": 100,
                "rating": 5,
                "status": "RE",
                "published_date": date(2015, 1, 1)
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('The title must be less than 50 characters long', form.errors['title'])
    
    def test_empty_title(self):
        form = BookForm(
            {
                "title": "",
                "pages": 100,
                "rating": 5,
                "status": "RE",
                "published_date": date(2015, 1, 1)
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('The title is mandatory', form.errors['title'])
    
    def test_incorrect_pages(self):
        form = BookForm(
            {
                "title": "Legado maldito",
                "pages": 0,
                "rating": 5,
                "status": "RE",
                "published_date": date(2015, 1, 1)
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('pages', form.errors)
    
    def test_incorrect_rating(self):
        form = BookForm(
            {
                "title": "Legado maldito",
                "pages": 100,
                "rating": 100,
                "status": "RE",
                "published_date": date(2015, 1, 1)
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)
    
    def test_incorrect_dates(self):
        form = BookForm(
            {
                "title": "Legado maldito",
                "pages": 0,
                "rating": 5,
                "status": "RE",
                "published_date": date(2015, 1, 1),
                "read_date": date(2014, 1, 1)
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('read_date', form.errors)
        self.assertIn('The read date must be after the published date', form.errors['read_date'])
    
    def test_author(self):
        author = Author.objects.create(
            name="JK Rowling",
            last_name="Tiffany"
        )
        form = BookForm(
            {
                "title": "Legado maldito",
                "pages": 100,
                "rating": 5,
                "status": "RE",
                "published_date": date(2015, 1, 1),
                "authors": [author.id]
            }
        )
        self.assertTrue(form.is_valid())
        book = form.save()
        self.assertEqual(book.title, "Legado maldito")
        self.assertEqual(book.rating, 5)
        self.assertEqual(book.published_date, date(2015, 1, 1))
        self.assertIn(author, book.authors.all())
    
    def test_cover(self):
        fake_file = SimpleUploadedFile(
            name="cover.jpg",
            content=b"Algo",
            content_type="image/jpeg"
        )
        form = BookForm(
            {
                "title": "Legado maldito",
                "pages": 100,
                "rating": 5,
                "status": "RE",
                "published_date": date(2015, 1, 1)
            },
            {
                "cover_image": fake_file
            }
        )
        self.assertTrue(form.is_valid())
        book = form.save()
        self.assertEqual(book.title, "Legado maldito")
        self.assertEqual(book.rating, 5)
        self.assertEqual(book.published_date, date(2015, 1, 1))
        self.assertEqual(book.cover_image.name, "covers/cover.jpg")
        shutil.rmtree('testfiles')

class BookViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_admin = User.objects.create_user(username="admin", password="admin")
        self.user_other = User.objects.create_user(username="other", password="other")
        self.admin_group = Group.objects.create(name="Admin")
        content_type = ContentType.objects.get_for_model(Book)
        add_perm = Permission.objects.get(codename="add_book", content_type=content_type)
        change_perm = Permission.objects.get(codename="change_book", content_type=content_type)
        view_perm = Permission.objects.get(codename="view_book", content_type=content_type)
        delete_perm = Permission.objects.get(codename="delete_book", content_type=content_type)
        self.admin_group.permissions.add(add_perm, change_perm, view_perm, delete_perm)
        self.user_admin.groups.add(self.admin_group)
        self.book = Book.objects.create(
            title="Piranesi",
            pages=300,
            rating=5,
            status="RE",
            published_date=date(2020, 6, 6)
        )
    
    def test_form_admin(self):
        self.client.login(username="admin", password="admin")
        url = reverse("form")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_form_other(self):
        self.client.login(username="other", password="other")
        url = reverse("form")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
    
    def test_list_admin(self):
        self.client.login(username="admin", password="admin")
        url = reverse("book_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_list_other(self):
        self.client.login(username="other", password="other")
        url = reverse("book_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_edit_admin(self):
        self.client.login(username="admin", password="admin")
        url = reverse("book_edit", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_edit_other(self):
        self.client.login(username="other", password="other")
        url = reverse("book_edit", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
    
    def test_delete_admin(self):
        self.client.login(username="admin", password="admin")
        url = reverse("book_delete", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_delete_other(self):
        self.client.login(username="other", password="other")
        url = reverse("book_delete", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
    
    def test_detail_admin(self):
        self.client.login(username="admin", password="admin")
        url = reverse("book_detail", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_detail_other(self):
        self.client.login(username="other", password="other")
        url = reverse("book_detail", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)