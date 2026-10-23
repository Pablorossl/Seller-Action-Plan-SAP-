from django import forms

from action_plans.models import ImprovementPlan, PlanStatus


class ImprovementPlanForm(forms.ModelForm):
    class Meta:
        model = ImprovementPlan
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "status" in self.fields:
            self.fields["status"].choices = [choice for choice in PlanStatus.choices if choice[0] not in (PlanStatus.CLOSED, PlanStatus.CANCELLED)]


class ClosePlanForm(forms.Form):
    status = forms.ChoiceField(label="Finalización", choices=[
        (PlanStatus.CLOSED, "Cerrar"), (PlanStatus.CANCELLED, "Cancelar"),
    ])
    notes = forms.CharField(label="Resultado y razones", widget=forms.Textarea,
        help_text="Explica el resultado, los objetivos pendientes y la decisión de finalizar el plan.")
