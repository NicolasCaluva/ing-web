import datetime
from haystack import indexes
from .models import School

class SchoolIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    careers = indexes.MultiValueField()
    tag = indexes.CharField(model_attr='tag__name', null=True)
    general_description = indexes.CharField(model_attr='general_description', null=True)
    def get_model(self):
        return School

    def index_queryset(self, using=None):
        """Usado cuando el índice es actualizado."""
        return self.get_model().objects.all()