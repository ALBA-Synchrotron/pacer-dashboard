import logging
from datetime import datetime
from logging import Logger

import math
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.management import BaseCommand

from dashboard.utils.icat import ICATClient
from dashboard.utils.rabbitmq import GenericPublisher

logger: Logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help: str = "Sends message to the PACER to index all datasets whose embargo has finished in the last 30 days."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--dry-run", type=bool, default=False, required=False, dest="dry_run",
                            help="Do not actually send the dataset index messages to the PACER.")
        parser.add_argument("--all-datasets", type=bool, default=False, required=False, dest="all_datasets",
                            help="Send all public datasets, not just those with just-finished embargoes.")

    def handle(self, *args, **options):
        icat_client: ICATClient = ICATClient(settings.ICAT_AUTH.get("url"),
                                             settings.ICAT_AUTH.get("username"),
                                             settings.ICAT_AUTH.get("password"),
                                             settings.ICAT_AUTH.get("auth_plugin"))

        icat_search_filters: dict = {"type.name__not_in": ["INDUSTRIAL"]}

        dry_run: bool = options.get("dry_run")
        all_datasets: bool = options.get("all_datasets")

        messages_for_pacer: list = []

        today: datetime = datetime.today()
        first_day_current_month: datetime = today.replace(day=1)
        first_day_last_month: datetime = first_day_current_month - relativedelta(months=1)
        last_day_last_month: datetime = first_day_current_month - relativedelta(days=1)

        if not all_datasets:
            icat_search_filters["releaseDate__gte"] = first_day_last_month.strftime("%Y-%m-%d")
            icat_search_filters["releaseDate__lte"] = last_day_last_month.strftime("%Y-%m-%d")

        investigations = icat_client.search("Investigation", conditions=icat_search_filters,
                                            flatten_single=False) or []

        logger.info(f"Found {len(investigations)} PUBLIC investigations to index.")

        for investigation in investigations:
            last_dataset_id = 0
            total_datasets = icat_client.search("Dataset", conditions={"investigation.id__eq": investigation.id},
                                                aggregate="COUNT")

            logger.info(f"Found {total_datasets} datasets for investigation {investigation.id}")

            for batch in range(math.ceil(total_datasets / settings.ICAT_BATCH_SIZE)):
                datasets = icat_client.search("Dataset", conditions={"id__gte": last_dataset_id,
                                                                     "investigation.id__eq": investigation.id},
                                              limit=(0, settings.ICAT_BATCH_SIZE),
                                              order=[("id", "DESC")], flatten_single=False)
                last_dataset_id = datasets[-1].id
                for dataset in datasets:
                    messages_for_pacer.append(
                        {"dataset_id": dataset.id, "index_name": settings.ES_PUBLIC_DATASET_INDEX})

        if not dry_run:
            GenericPublisher.send_messages_to_broker(messages_for_pacer, settings.PACER_INTERNAL_DATASET_EXCHANGE,
                                                     settings.PACER_DATASET_INDEXING_ROUTING_KEY)
