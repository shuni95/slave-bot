from models import User
from test_base import OratorTestCase

class TestUserModel(OratorTestCase):

    def test_create_user(self):
        user = User.create(name='name', telegram_chat_id=123123124, username='')

        assert user.name == 'name'

    def test_edit_user(self):
        user = User.create(name='name', telegram_chat_id=123123124, username='')

        user.name = 'new_name'
        user.username = 'testing_username'
        user.save()

        user_searched = User.where('telegram_chat_id', 123123124).first()

        assert user_searched.name == 'new_name'
        assert user_searched.username == 'testing_username'
