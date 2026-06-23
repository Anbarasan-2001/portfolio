"""Public-facing forms."""

from django import forms

from .models import ContactMessage

# Tailwind classes shared by all text inputs in the contact form.
INPUT_CLASSES = (
    "w-full rounded-xl border border-slate-200 dark:border-white/10 "
    "bg-white dark:bg-white/5 px-4 py-3 text-slate-800 dark:text-slate-100 "
    "placeholder-slate-400 focus:border-accent focus:ring-2 focus:ring-accent/30 "
    "outline-none transition"
)


class ContactForm(forms.ModelForm):
    """Contact form backing the public ContactMessage model."""

    # Honeypot: bots fill this hidden field; humans never see it.
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": INPUT_CLASSES, "placeholder": "Your name", "required": True}
            ),
            "email": forms.EmailInput(
                attrs={"class": INPUT_CLASSES, "placeholder": "you@example.com", "required": True}
            ),
            "subject": forms.TextInput(
                attrs={"class": INPUT_CLASSES, "placeholder": "Subject"}
            ),
            "message": forms.Textarea(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "Tell me about your project...",
                    "rows": 5,
                    "required": True,
                }
            ),
        }

    def clean_website(self):
        """Reject submissions that fill the honeypot field."""
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Spam detected.")
        return ""
