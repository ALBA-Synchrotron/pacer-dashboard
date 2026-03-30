from django.views.generic import TemplateView


class DashboardView(TemplateView):
    template_name: str = "main.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super(DashboardView, self).get_context_data(**kwargs)

        return context
