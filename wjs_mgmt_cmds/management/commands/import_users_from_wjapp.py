"""Create a bunch of users, useful for testing."""

# from collections import namedtuple
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import configparser
import os
import pymysql
import logging
from wjs_mgmt_cmds.pytyp.affiliationSplitter import splitCountry
from wjs.jcom_profile.models import UserCod
from core.models import Country

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Admin command to import a user from wjapp."""

    help = "Import user from wjapp. Needs a userCod!"

    # Important! This is the entry point.
    def handle(self, *args, **options):
        """Import the user."""
        wjapp_user = self.read_user(options["usercod"])
        self.create_or_update(wjapp_user)

    def add_arguments(self, parser):
        """Add arguments to mgmt command."""
        parser.add_argument(
            "usercod", type=int, help="The userCod of the user to import"
        )

    def read_user(self, usercod):
        """Read data from wjapp."""
        self.usercod = usercod
        connect_string = self.get_connect_string()
        wjapp_user = self.read_data(connect_string)
        return wjapp_user

    def get_connect_string(self, journal="jcom") -> dict:
        """Return a connection string suitable for pymysql."""
        self.journal = journal
        config = self.read_config(self.journal)
        return dict(
            database=config.get("db_name"),
            host=config.get("db_host"),
            user=config.get("db_user"),
            password=config.get("db_password"),
        )

    def read_config(self, journal):
        """Read configuration file."""
        # TODO: parametrize
        cred_file = os.path.join("/tmp", ".db.ini")
        config = configparser.ConfigParser()
        config.read(cred_file)
        return config[journal]

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
        Account = get_user_model()
        # I want to retrieve an account that might already exist
        # (based on the usercod/journal pair) OR create a new account.
        defaults = dict(
            username=wjapp_user["userId"],
            email=wjapp_user["email"],
            first_name=wjapp_user["firstName"],  # redundant
            last_name=wjapp_user["lastName"],  # redundant
        )
        # logger.debug("DEFAULTS⩤ %s", defaults)
        source = [s[0] for s in UserCod.sources if s[1] == self.journal][0]
        (new_user, created) = Account.objects.get_or_create(
            defaults=defaults,
            usercods__userCod=self.usercod,
            usercods__source=source,
        )

        # Mapping between Janeway core_account and wjapp User
        # ===================================================

        # Fields from wjapp User table ----------------------------
        # new_user.userCod = ... see below (data is related to
        # Account, so an account must exist before saving)
        new_user.username = wjapp_user["userId"]
        # new_user.password = wjapp_user['password']
        # new_user.passwordResetToken = wjapp_user['passwordResetToken']
        new_user.email = wjapp_user["email"]
        new_user.first_name = wjapp_user["firstName"]
        new_user.middle_name = wjapp_user["middleName"]
        new_user.last_name = wjapp_user["lastName"]
        new_user.institution = wjapp_user["organization"]
        new_user.date_joined = wjapp_user["registrationDate"]
        # new_user.phone = wjapp_user['phone']
        # new_user.fax = wjapp_user['fax']
        # new_user.mobile = wjapp_user['mobile']
        # new_user.address = wjapp_user['address']
        # new_user.editorWorkload = wjapp_user['editorWorkload']
        # new_user.registeredByCod = wjapp_user['registeredByCod']
        # new_user.registeredByRealCod = wjapp_user['registeredByRealCod']
        # new_user.privacy = wjapp_user['privacy']
        # new_user.privacyActionDate = wjapp_user['privacyActionDate']
        # new_user.commMail = wjapp_user['commMail']
        # new_user.submissionAllowed = wjapp_user['submissionAllowed']
        # new_user.lastAccessDate = wjapp_user['lastAccessDate']

        # Fields from Janeway core_account
        # --------------------------------
        # new_user.activation_code = wjapp_user['activation_code']
        # new_user.salutation = wjapp_user['salutation']

        # No bio related to a single user in wjapp: there is a
        # `authorsBio` field in the Version table. I will use the info
        # from Drupal.
        # new_user.biography = wjapp_user['biography']

        new_user.orcid = wjapp_user["orcidid"]
        new_user.institution = wjapp_user["institution"]
        # new_user.department = wjapp_user['department']
        # new_user.twitter = wjapp_user["twitter"]
        # new_user.facebook = wjapp_user["facebook"]
        # new_user.linkedin = wjapp_user["linkedin"]
        # new_user.website = wjapp_user["website"]
        # new_user.github = wjapp_user["github"]
        # new_user.profile_image = wjapp_user["profile_image"]
        # new_user.email_sent = wjapp_user["email_sent"]
        # new_user.date_confirmed = wjapp_user["date_confirmed"]
        # new_user.confirmation_code = wjapp_user["confirmation_code"]
        # new_user.signature = wjapp_user["signature"]

        # Is "interest" equivalent to ours "keywords"?
        # new_user.interest = wjapp_user["interest"]

        if wjapp_user["country"] is None:
            logger.warning("No country for user %s", wjapp_user["email"])
        try:
            country = Country.objects.get(name=wjapp_user["country"])
        except Country.DoesNotExist:
            logger.error(
                "Unknown country %s for user %s",
                wjapp_user["country"],
                wjapp_user["email"],
            )
        else:
            new_user.country = country
        # new_user.preferred_timezone = wjapp_user["preferred_timezone"]

        # TODO: verify if these can be evinced from the Feature table
        # new_user.is_active = wjapp_user["is_active"]
        # new_user.is_staff = wjapp_user["is_staff"]
        # new_user.is_admin = wjapp_user["is_admin"]

        # new_user.enable_digest = wjapp_user["enable_digest"]
        # new_user.enable_public_profile = wjapp_user["enable_public_profile"]
        # new_user.date_joined = wjapp_user["date_joined"]
        # new_user.uuid = wjapp_user["uuid"]

        new_user.save()
        if created:
            logger.debug(
                "New user created (%s) for %s",
                new_user.id,
                wjapp_user["email"],
            )
            # It is necessary to record the usercod only if the user
            # has been newly created, because the usercod is used to
            # "decide" whether to get an existing user or to creat a
            # new one. When we are here (`created == True`), it means
            # that no such usercod/journal exited.
            try:
                UserCod.objects.create(
                    account=new_user, userCod=self.usercod, source=source
                )
            except Exception as e:
                logger.error(
                    "Error storing userCod %s-%s for %s: %s",
                    self.usercod,
                    self.journal,
                    wjapp_user["email"],
                    e,
                )

    def mangle_organization(self, record):
        """Transform wjapp's "organization" into Janeway's "country" and "address"."""
        if record["organization"] is None or record["organization"] == '':
            record["country"] = None
            record["institution"] = None
            return

        # This is the iteresting part ⤵
        dictCountry = splitCountry(record["organization"])

        check = record.setdefault("country", dictCountry["country"])
        assert check == dictCountry["country"]
        # institution and address are similar enough for me :)
        check = record.setdefault("institution", dictCountry["address"])
        assert check == dictCountry["address"]
