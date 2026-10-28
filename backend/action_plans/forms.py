from django import forms

from action_plans.models import ImprovementPlan, PlanStatus


class RevisionForm(forms.ModelForm):
    expected_revision = forms.IntegerField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["expected_revision"].initial = self.instance.revision

    def clean(self):
        data = super().clean()
        if self.instance.pk and data.get("expected_revision") is not None:
            from action_plans.concurrency import check_revision
            check_revision(self.instance, data["expected_revision"])
        return data


class ImprovementPlanForm(RevisionForm):
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
