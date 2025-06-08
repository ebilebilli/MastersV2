from django_elasticsearch_dsl import Document, fields, Index
from django_elasticsearch_dsl.registries import registry
from elasticsearch import Elasticsearch
from django.conf import settings

from services.models.category_model import Category
from services.models.service_model import Service
from core.models.city_model import City, District
from users.models.master_model import Master

es_client = Elasticsearch(hosts=[settings.ELASTICSEARCH_HOST])
if not es_client.ping():
    raise ValueError("Elasticsearch serverinə qoşulma uğursuz oldu!")

@registry.register_document
class MasterDocument(Document):
    profession_category = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(),
        'display_name': fields.TextField(),
    })

    profession_service = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(),
        'display_name': fields.TextField(),
    })

    cities = fields.NestedField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(),
        'display_name': fields.TextField(),
    })

    districts = fields.NestedField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(),
        'display_name': fields.TextField(),
    })

    average_rating = fields.FloatField()
    review_count = fields.IntegerField()

    class Index:
        name = 'masters'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Master
        fields = [
            'full_name',
            'custom_profession',
            'education_detail',
            'birthday',
            'phone_number',
            'gender',
            'is_active_on_main_page',
            'note',
            'experience',
            'facebook_url',
            'instagram_url',
            'tiktok_url',
            'linkedin_url',
            'youtube_url',
            'created_at',
            'slug',
        ]
        related_models = [Category, Service, City, District]

    def get_instances_from_related(self, related_instance):
        try:
            if isinstance(related_instance, Category):
                return Master.objects.filter(profession_category=related_instance)
            elif isinstance(related_instance, Service):
                return Master.objects.filter(profession_service=related_instance)
            elif isinstance(related_instance, City):
                return Master.objects.filter(cities=related_instance)
            elif isinstance(related_instance, District):
                return Master.objects.filter(districts=related_instance)
            return []
        except Exception:
            return []

    def prepare_average_rating(self, instance):
        return instance.average_rating() or None

    def prepare_review_count(self, instance):
        return instance.review_count or None

    def prepare_profession_category(self, instance):
        if instance.profession_category:
            return {
                'id': instance.profession_category.id,
                'name': instance.profession_category.name,
                'display_name': instance.profession_category.display_name
            }
        return None

    def prepare_profession_service(self, instance):
        if instance.profession_service:
            return {
                'id': instance.profession_service.id,
                'name': instance.profession_service.name,
                'display_name': instance.profession_service.display_name
            }
        return None

    def prepare_custom_profession(self, instance):
        return instance.custom_profession or None

    def prepare_cities(self, instance):
        return [
            {
                'id': city.id,
                'name': city.name,
                'display_name': getattr(city, 'display_name', None)
            }
            for city in instance.cities.all()
        ]

    def prepare_districts(self, instance):
        return [
            {
                'id': district.id,
                'name': district.name,
                'display_name': getattr(district, 'display_name', None)
            }
            for district in instance.districts.all()
        ]