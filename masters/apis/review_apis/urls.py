from django.urls import path

from apis.review_apis.review_views import *


app_name = 'review_apis'

urlpatterns = [
    path(
        'masters/<int:master_id>/reviews/',
        ReviewsForMasterAPIView.as_view(),
        name="master-reviews-list"
    ),
    
    path(
        'masters/<int:master_id>/reviews/create/',
         CreateReviewAPIView.as_view(),
         name='create-reviews'
    ),

    path(
        'masters/reviews/<int:review_id>/update/',
        UpdateReviewAPIView.as_view(),
        name='udpate-reviews'
    ),

    path(
        'masters/reviews/<int:review_id>/delete/',
        DeleteReviewAPIView.as_view(),
        name='delete-reviews'
    ),

    path(
        'masters/<int:master_id>/reviews/filter/',
        FilterReviewAPIView.as_view(),
        name='filter-reviews'
    )
]
