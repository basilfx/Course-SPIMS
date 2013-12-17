from django import forms

from otp_analyzer.models import Record

import datetime

class UnixDateTimeField(forms.DateTimeField):
    def to_python(self, value):
          try:
               return datetime.datetime.fromtimestamp(int(value))
          except TypeError:
               raise forms.ValidationError(self.error_messages['invalid'], code='invalid')

class RecordImportForm(forms.ModelForm):
     start_time = UnixDateTimeField()
     end_time = UnixDateTimeField()

     class Meta:
          model = Record