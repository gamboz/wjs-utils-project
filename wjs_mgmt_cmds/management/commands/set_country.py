"""Set a user's country from her institution."""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from wjs_mgmt_cmds.pytyp.affiliationSplitter import splitCountry
import logging
import warnings

logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=RuntimeWarning)


class Command(BaseCommand):
    """Admin command to set a user's country."""

    help = """Set a users country.

    Cycle through all accounts (ordered by id) and, for each one, if
    the country is not set, then try to extract it from the
    affiliation.
    """

    # Important! This is the entry point.
    def handle(self, *args, **options):
        """Set the country."""
        # import pudb; pudb.set_trace()
        self.options = options
        for account in self.accounts:
            self.set_country(account)

    def add_arguments(self, parser):
        """Add arguments to mgmt command."""
        parser.add_argument(
            "--interactive",
            action="store_true",
            help="Ask for user input in dubious cases.",
        )
        parser.add_argument(
            "--remove-from-organization",
            action="store_true",
            help="If a country is found in the `organization` field,"
            " use it for the field `country`"
            " AND remove it from the `organization` string."
            " Warning: the form of the `organization` migth change sligthly,"
            ' because the string is "normalized" in the process.',
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Set the `country` from the `organization`"
            " even if `country` already has a value.",
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--accountid", type=int, help="Work on this account only."
        )
        group.add_argument(
            "--start-from", type=int, help="Start from this account id."
        )

    def set_country(self, account):
        """Extract the country from the affiliation and set it."""
        if not account.country or self.options["force"]:
            organization = account.organization
            address = splitCountry(organization, self.options)
            if address.country is None:
                logger.warning("Cannot set country for account %s (from %s)",
                               account.id,
                               account.organization)
            else:
                account.country = address.country
                if self.options["remove_from_organization"]:
                    account.organization = address.address
            return address

    @property
    def accounts(self):
        """Make a query set with the accounts to check."""
        Account = get_user_model()
        if self.options["accountid"]:
            return Account.objects.get(id=self.options["accountid"])

        if self.options["start_from"]:
            return Account.objects.filter(
                id__gteq=self.options["start-from"]
            ).order_by("id")

        return Account.objects.all().order_by("id")
