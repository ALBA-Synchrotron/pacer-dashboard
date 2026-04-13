from django.views.generic import TemplateView

from dashboard.models import GroupProfile


class DashboardView(TemplateView):
    template_name: str = "main.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super(DashboardView, self).get_context_data(**kwargs)
        context["message_types"] = GroupProfile.get_allowed_message_types(self.request.user)
        return context
