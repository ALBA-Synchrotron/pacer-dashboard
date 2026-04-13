from django.db import models

from ..labels.investigation_check import MODEL_LABELS, VERBOSE_NAME, VERBOSE_NAME_PLURAL


class InvestigationCheck(models.Model):
    investigation = models.CharField(max_length=255, verbose_name=MODEL_LABELS.get("investigation"))
    visit_id = models.CharField(max_length=255, default="", verbose_name=MODEL_LABELS.get("visit_id"))
    has_doi = models.BooleanField(default=False, verbose_name=MODEL_LABELS.get("has_doi"))
    has_panosc_item = models.BooleanField(default=False, verbose_name=MODEL_LABELS.get("has_panosc_item"))
    first_check_date = models.DateTimeField(auto_now_add=True, verbose_name=MODEL_LABELS.get("first_check_date"))
    last_check_date = models.DateTimeField(auto_now=True, verbose_name=MODEL_LABELS.get("last_check_date"))
    check_retries = models.IntegerField(default=0, verbose_name=MODEL_LABELS.get("check_attempts"))

    class Meta:
        verbose_name: str = VERBOSE_NAME
        verbose_name_plural: str = VERBOSE_NAME_PLURAL
