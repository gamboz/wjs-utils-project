"""Import all users from a journal."""

from django.core.management.base import BaseCommand
from django.core.management import call_command
import logging
import warnings
import pymysql
from ._utils import get_connect_string

logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=RuntimeWarning)


class Command(BaseCommand):
    """Management command to import all users froma journal."""

    help = "Import all users from a journal."

    def handle(self, *args, **options):
        """Import all users from a journal."""
        self.journal = options["journal"]
        counter = 0
        for record in self.get_all_usercods():
            usercod = record[0]
            call_command("import_user_from_wjapp", usercod, self.journal)
            counter += 1
        self.stdout.write(f"Imported {counter} users")

    def add_arguments(self, parser):
        """Add arguments to mgmt command."""
        parser.add_argument(
            "journal", type=str, help="The journal from which to import"
        )

    def get_all_usercods(self):
        """Return all usercods of a certain journal."""
        with pymysql.connect(**get_connect_string(self.journal)) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT userCod from User order by userCod""")
                return cursor
