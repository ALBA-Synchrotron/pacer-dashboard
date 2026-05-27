from datetime import datetime, timezone
import logging
from logging import Logger
from xml.dom.minidom import Entity

from django.core.management import BaseCommand
from django.conf import settings
from django.db.models import QuerySet, Q

from dashboard.models import InvestigationCheck
from dashboard.utils.icat import ICATClient
from dashboard.utils.panosc import SimplePaNOSCClient
from dashboard.utils.rabbitmq import GenericPublisher

logger: Logger = logging.getLogger(__name__)


def is_valid_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


class Command(BaseCommand):
    help: str = "Check that finished ICAT investigations have a DOI and PaNOSC items created, and if not mint them."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--dry-run", type=bool, default=False, required=False, dest="dry_run",
                            help="Do not actually send mint / PaNOSC item creation operations to the PACER.")
        parser.add_argument("--investigation", type=str, default="", required=False, dest="investigation_name",
                            help="Investigation to run checks for.")
        parser.add_argument("--visit_id", type=str, default="", required=False, dest="visit_id",
                            help="Investigation to run checks for.")

    def handle(self, *args, **options):
        icat_client: ICATClient = ICATClient(settings.ICAT_AUTH.get("url"),
                                             settings.ICAT_AUTH.get("username"),
                                             settings.ICAT_AUTH.get("password"),
                                             settings.ICAT_AUTH.get("auth_plugin"))

        pss_client: SimplePaNOSCClient = SimplePaNOSCClient(settings.PANOSC_AUTH.get("url"),
                                                            settings.PANOSC_AUTH.get("username"),
                                                            settings.PANOSC_AUTH.get("password"))

        icat_search_filters: dict = {"type.name__not_in": ["INDUSTRIAL"]}
        inv_checks_filter: Q = (Q(has_doi=False) | Q(has_panosc_item=False)) & Q(
            check_retries__lt=settings.INVESTIGATION_CHECK_MAX_RETRIES)

        dry_run: bool = options.get("dry_run")
        investigation_name: str = options.get("investigation_name")
        visit_id: str = options.get("visit_id")

        end_date_since: str = datetime.now().strftime("%Y-%m-%d")

        if investigation_name:
            if not visit_id:
                logger.error("Investigation name provided, but no visit ID provided.")
                return

            icat_search_filters["name__eq"] = investigation_name
            inv_checks_filter &= Q(investigation=investigation_name)

            icat_search_filters["visit_id__eq"] = visit_id
            inv_checks_filter &= Q(visit_id=visit_id)

        elif end_date_since:
            if not is_valid_date(end_date_since):
                logger.error("Invalid end date filter format. Format: YYYY-MM-DD")
                return
            icat_search_filters["endDate__lte"] = end_date_since

        investigations_empty_doi_icat: list = icat_client.search("Investigation",
                                                                 conditions={**icat_search_filters, "doi__eq": ""},
                                                                 flatten_single=False)
        investigations_null_doi_icat: list = icat_client.search("Investigation",
                                                                conditions={**icat_search_filters, "doi__eq": None},
                                                                flatten_single=False)

        investigations_no_doi_icat: list = investigations_empty_doi_icat + investigations_null_doi_icat
        if not investigations_no_doi_icat:
            investigations_no_doi_icat = []

        for inv in investigations_no_doi_icat:
            _, __ = InvestigationCheck.objects.get_or_create(investigation=inv.name, visit_id=inv.visitId)

        investigations_check: QuerySet = InvestigationCheck.objects.filter(inv_checks_filter)

        messages_for_pacer: list = []
        for inv_check in investigations_check:
            pacer_ops: list = []

            investigation: Entity = icat_client.search("Investigation",
                                                       conditions={"name__eq": inv_check.investigation,
                                                                   "visitId__eq": inv_check.visit_id}, )
            if not investigation:
                continue

            if investigation.endDate:
                if investigation.endDate > datetime.now(timezone.utc):
                    inv_check.delete()
                    continue

            # No DOI, DOI check pending, then mint the proposal.
            if not investigation.doi and not inv_check.has_doi:
                pacer_ops.append(settings.PACER_INV_OPERATION_MINT)

            # DOI, but check pending, then mark DOI check as complete.
            if investigation.doi and not inv_check.has_doi:
                inv_check.has_doi = True

            pss_id: str = f"{investigation.name}/{investigation.visitId}"

            # No PaNOSC item, PaNOSC item check pending, then create the item.
            if not pss_client.item_exists(pss_id) and not inv_check.has_panosc_item:
                pacer_ops.append(settings.PACER_INV_OPERATION_PANOSC_ITEM)

            # PaNOSC item, but check pending, then mark PaNOSC item check as complete.
            if pss_client.item_exists(pss_id) and not inv_check.has_panosc_item:
                inv_check.has_panosc_item = True

            if not dry_run:
                inv_check.check_retries += 1
                inv_check.save()

            messages_for_pacer.append(
                {"name": str(investigation.name), "visit_id": str(investigation.visitId), "operations": pacer_ops})
        icat_client.logout()

        GenericPublisher.send_messages_to_broker(messages_for_pacer, settings.PACER_INVESTIGATION_OPS_EXCHANGE,
                                                 settings.PACER_INVESTIGATION_OPS_ROUTING_KEY)
