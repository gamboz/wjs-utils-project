"""Create a bunch of users, useful for testing."""

from collections import namedtuple
from django.core.management.base import BaseCommand
from journal.models import Journal
from utils.testing import helpers


class Command(BaseCommand):
    """Admin command."""

    help = 'Create some authors, editors, reviewers, etc…'

    def generate_username(account):
        """Generate username from first and last name."""
        username = account.first.lower() + account.last.lower()
        return username

    def handle(self, *args, **options):
        """Handle the command."""
        Account = namedtuple('Account', [
            'first',
            'last',
            'email',
            'roles',
        ])
        accounts_data = [
            Account('Autho', 'Rename', 'au1@localdomain', ['author', ]),
            Account('Refe', 'Ree', 'ref1@localdomain', ['reviewer', ]),
            Account('Edi', 'Tor', 'ed1@localdomain', ['editor', ]),
            ]

        jcom = Journal.objects.get(code='JCOM')
        password = 'pass'
        # country_id for Italy:
        italy = 110
        for account_data in accounts_data:
            username = self.generate_username(account_data)
            helpers.create_users(username,
                                 roles=account_data.roles,
                                 journal=jcom,
                                 password=password,
                                 email=account_data.email,
                                 first_name=account_data.first,
                                 last_name=account_data.last,
                                 is_active=True,
                                 country_id=italy
                                 )
