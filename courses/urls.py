from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # home page
    path('', views.index, name="index"),
    
    # course - category - review
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('category/<int:category_id>/', views.category_courses, name='category_courses'),
    path('review/create', views.create_review, name="create-review"),
    # upload course
    path('upload/', views.upload_course, name='upload_course'),
    path('course/<int:pk>/update/', views.update_course, name='update_course'),
    path('course/<int:pk>/delete/', views.delete_course, name='delete_course'),

    # dashboard - change group permission
    path("dashboard", views.dashboard, name="dashboard"),
    path('become-instructor/', views.become_instructor, name='become_instructor'),
    
    # auth
    path('register', views.RegisterView.as_view(), name="register"),
    path('signout', views.signout, name="signout"),

    # shopping cart
    path('cart/add/<int:id>/', views.cart_add, name='cart_add'),
    path('cart/item_clear/<int:id>/', views.item_clear, name='item_clear'),
    path('cart/cart_clear/', views.cart_clear, name='cart_clear'),
    path('cart/cart-detail/',views.cart_detail,name='cart_detail'),

    # checkout    
    path('checkout', views.checkout, name="checkout"),
]
