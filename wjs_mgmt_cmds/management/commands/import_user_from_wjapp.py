"""Import a single user from a journal."""

# from collections import namedtuple
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import pymysql
import logging
from wjs_mgmt_cmds.pytyp.affiliationSplitter import splitCountry
from wjs.jcom_profile.models import UserCod
from core.models import Country
import warnings
from ._utils import get_connect_string

logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=RuntimeWarning)


class Command(BaseCommand):
    """Admin command to import a user from wjapp."""

    help = "Import user from wjapp. Needs a userCod!"

    # Important! This is the entry point.
    def handle(self, *args, **options):
        """Import the user."""
        # import pudb; pudb.set_trace()
        self.journal = options["journal"]
        self.usercod = options["usercod"]
        wjapp_user = self.read_user()
        self.create_or_update(wjapp_user)

    def add_arguments(self, parser):
        """Add arguments to mgmt command."""
        parser.add_argument(
            "usercod", type=int, help="The userCod of the user to import"
        )
        parser.add_argument("journal", help="The journal from which to import")

    def read_user(self):
        """Read data from wjapp."""
        connect_string = get_connect_string()
        wjapp_user = self.read_data(connect_string)
        return wjapp_user

    def read_data(self, connect_string):
        """Connect to DB and return data structure."""
        with pymysql.connect(
            **connect_string, cursorclass=pymysql.cursors.DictCursor
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                SELECT u.*, o.orcidid
                FROM User u LEFT JOIN OrcidId o ON o.userCod = u.userCod
                WHERE u.usercod = %s
                """,
                    (self.usercod,),
                )
                if cursor.rowcount != 1:
                    logger.error(
                        "Unexpected row count from wjapp: %s instead of 1!",
                        cursor.rowcount,
                    )
                    raise Exception(
                        "Unexpected query result. Maybe too many ORCIDids?"
                    )
                # TODO: might need to mangle more data before returning
                record = cursor.fetchone()
                self.mangle_organization(record)
                return record

    def create_or_update(self, wjapp_user):
        """Create or update Janeway user from wjapp data."""
        # see also https://gitlab.sissamedialab.it/gamboz/wjs-utils-project/-/issues/2
        email_exists = self.does_email_exists(wjapp_user)
        (janeway_account, account_created) = self.get_or_create_account(
            wjapp_user, email_exists
        )
        if account_created:
            if email_exists:
                # difficult case: should merge two users from different journals
                logger.debug(
                    "User %s newly imported from %s, but email (%s) already exists."
                    " Probably previously imported from other journal.",
                    self.usercod,
                    self.journal,
                    wjapp_user["email"],
                )
                self.merge_data(wjapp_user, janeway_account)
                self.save_usercod(janeway_account)
            else:
                # easy case: all new
                self.save_data(wjapp_user, janeway_account)
                self.save_usercod(janeway_account)
        else:
            if email_exists:
                # easy case: already imported from same journal
                # just overwrite data
                self.save_data(wjapp_user, janeway_account)
            else:
                # impossible case
                logger.error("#!💀???❌@§*.")

    def save_data(self, wjapp_user, janeway_account):
        """Save (overwrite) wjapp data over Janeway account."""
        # Mapping between Janeway core_account and wjapp User
        # ===================================================

        # Fields from wjapp User table
        # ----------------------------
        # janeway_account.userCod = ... see below (data is related to
        # Account, so an account must exist before saving)
        janeway_account.username = wjapp_user["userId"]
        # janeway_account.password = wjapp_user['password']
        # janeway_account.passwordResetToken = wjapp_user['passwordResetToken']
        janeway_account.email = wjapp_user["email"]
        janeway_account.first_name = wjapp_user["firstName"]
        janeway_account.middle_name = wjapp_user["middleName"]
        janeway_account.last_name = wjapp_user["lastName"]
        janeway_account.institution = wjapp_user["organization"]
        janeway_account.date_joined = wjapp_user["registrationDate"]
        # janeway_account.phone = wjapp_user['phone']
        # janeway_account.fax = wjapp_user['fax']
        # janeway_account.mobile = wjapp_user['mobile']
        # janeway_account.address = wjapp_user['address']
        # janeway_account.editorWorkload = wjapp_user['editorWorkload']
        # janeway_account.registeredByCod = wjapp_user['registeredByCod']
        # janeway_account.registeredByRealCod = wjapp_user['registeredByRealCod']
        # janeway_account.privacy = wjapp_user['privacy']
        # janeway_account.privacyActionDate = wjapp_user['privacyActionDate']
        # janeway_account.commMail = wjapp_user['commMail']
        # janeway_account.submissionAllowed = wjapp_user['submissionAllowed']
        # janeway_account.lastAccessDate = wjapp_user['lastAccessDate']

        # Fields from Janeway core_account
        # --------------------------------
        # janeway_account.activation_code = wjapp_user['activation_code']
        # janeway_account.salutation = wjapp_user['salutation']

        # No bio related to a single user in wjapp: there is a
        # `authorsBio` field in the Version table. I will use the info
        # from Drupal.
        # janeway_account.biography = wjapp_user['biography']

        janeway_account.orcid = wjapp_user["orcidid"]
        janeway_account.institution = wjapp_user["institution"]
        # janeway_account.department = wjapp_user['department']
        # janeway_account.twitter = wjapp_user["twitter"]
        # janeway_account.facebook = wjapp_user["facebook"]
        # janeway_account.linkedin = wjapp_user["linkedin"]
        # janeway_account.website = wjapp_user["website"]
        # janeway_account.github = wjapp_user["github"]
        # janeway_account.profile_image = wjapp_user["profile_image"]
        # janeway_account.email_sent = wjapp_user["email_sent"]
        # janeway_account.date_confirmed = wjapp_user["date_confirmed"]
        # janeway_account.confirmation_code = wjapp_user["confirmation_code"]
        # janeway_account.signature = wjapp_user["signature"]

        # Is "interest" equivalent to ours "keywords"?
        # janeway_account.interest = wjapp_user["interest"]

        self.set_country(wjapp_user, janeway_account)
        # janeway_account.preferred_timezone = wjapp_user["preferred_timezone"]

        # TODO: verify if these can be evinced from the Feature table
        # janeway_account.is_active = wjapp_user["is_active"]
        # janeway_account.is_staff = wjapp_user["is_staff"]
        # janeway_account.is_admin = wjapp_user["is_admin"]

        # janeway_account.enable_digest = wjapp_user["enable_digest"]
        # janeway_account.enable_public_profile = wjapp_user["enable_public_profile"]
        # janeway_account.date_joined = wjapp_user["date_joined"]
        # janeway_account.uuid = wjapp_user["uuid"]

        janeway_account.save()
        # if created:
        #     logger.debug(
        #         "New user created (%s) for %s",
        #         janeway_account.id,
        #         wjapp_user["email"],
        #     )
        #     # It is necessary to record the usercod only if the user
        #     # has been newly created, because the usercod is used to
        #     # "decide" whether to get an existing user or to creat a
        #     # new one. When we are here (`created == True`), it means
        #     # that no such usercod/journal exited.
        #     try:
        #         UserCod.objects.create(
        #             account=janeway_account,
        #             userCod=self.usercod,
        #             source=source,
        #         )
        #     except Exception as e:
        #         logger.error(
        #             "Error storing userCod %s-%s for %s: %s",
        #             self.usercod,
        #             self.journal,
        #             wjapp_user["email"],
        #             e,
        #         )

    def save_usercod(self, janeway_account):
        """Save the usercod/journal info."""
        source = [s[0] for s in UserCod.sources if s[1] == self.journal][0]
        UserCod.objects.create(
            account=janeway_account,
            userCod=self.usercod,
            source=source,
        )

    def mangle_organization(self, record):
        """Transform wjapp's "organization" into Janeway's "country" and "address"."""
        if record["organization"] is None or record["organization"] == "":
            record["country"] = None
            record["institution"] = None
            return

        # This is the iteresting part ⤵
        dictCountry = splitCountry(record["organization"])

        # I prefer None over an empty string.
        if dictCountry["country"] == "":
            dictCountry["country"] = None
        if dictCountry["address"] == "":
            dictCountry["address"] = None
        if dictCountry["other"] == "":
            dictCountry["other"] = None

        check = record.setdefault("country", dictCountry["country"])
        assert check == dictCountry["country"]
        # institution and address are similar enough for me :)
        check = record.setdefault("institution", dictCountry["address"])
        assert check == dictCountry["address"]

    def get_or_create_account(self, wjapp_user, email_exists):
        """Similar to django's get_or_create.

        I want to retrieve an account that might already exist (based
        on the usercod/journal pair) OR create a new account.
        """
        created = False
        Account = get_user_model()
        source = [s[0] for s in UserCod.sources if s[1] == self.journal][0]
        try:
            account = Account.objects.get(
                usercods__userCod=self.usercod,
                usercods__source=source,
            )
        except Account.DoesNotExist:
            if email_exists:
                created = False
                account = Account.objects.get(email=wjapp_user["email"])
            else:
                created = True
                account = Account(
                    username=wjapp_user["userId"],
                    email=wjapp_user["email"],
                    first_name=wjapp_user["firstName"],  # redundant
                    last_name=wjapp_user["lastName"],  # redundant
                )
            account.save()
        return (account, created)

    def does_email_exists(self, wjapp_user):
        """Test whether the given email already exists."""
        Account = get_user_model()
        return bool(Account.objects.filter(email=wjapp_user["email"]))

    def merge_data(self, wjapp_user, janeway_account):
        """Merge new data with existing data."""
        logger.warning(
            "Must merge data w:%s-%s / j:%s, but does not know how...",
            self.usercod,
            self.journal,
            janeway_account.id,
        )
        self.save_data(wjapp_user, janeway_account)

    def set_country(self, wjapp_user, janeway_account):
        """Map a wjapp country to Janeway's country."""
        if wjapp_user["country"] is None:
            logger.warning(
                "No country for user %s (%s)",
                wjapp_user["userCod"],
                wjapp_user["email"],
            )
        else:
            mymap = dict(
                UK="United Kingdom",
            )
            try:
                country = Country.objects.get(
                    name__contains=mymap.get(
                        wjapp_user["country"], wjapp_user["country"]
                    )
                )
            except Country.DoesNotExist:
                logger.error(
                    "Unknown country %s for user %s",
                    wjapp_user["country"],
                    wjapp_user["email"],
                )
            else:
                janeway_account.country = country

    # def get_unique_email(self, wjapp_user):
    #     """Check that the email we are using is unique.

    #     If it is not, generate a unique one and return it.
    #     I'm assuming that

    #     """
    #     # wjapp allows for non-unique emails[*]. Let's generate a unique
    #     # one if we need it.
    #     # [*] probably only "service" users such as jcom-hidden-user & co.
    #     #
    #     # TODO: merge users with same email?
    #     email = wjapp_user["email"]
    #     Account = get_user_model()
    #     try:
    #         Account.objects.get(email=email)
    #     except Exception:
    #         pass
    #     else:
    #         (name, domain) = email.split("@")
    #         unique_email = f"{name}+{self.usercod}@{domain}"
    #         logger.warning("Account with email %s already exists. Using %s",
    #                        email, unique_email)
    #         email = unique_email

    #     defaults = dict(
    #     )
    #     return defaults
