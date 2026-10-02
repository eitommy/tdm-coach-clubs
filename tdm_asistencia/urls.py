from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path


handler403 = "tdm_asistencia.error_views.error_403"
handler404 = "tdm_asistencia.error_views.error_404"
handler500 = "tdm_asistencia.error_views.error_500"


urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "accounts/login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
        ),
        name="login",
    ),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    path(
        "accounts/password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="auth/password_reset_form.html",
            email_template_name="auth/password_reset_email.html",
            subject_template_name="auth/password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "accounts/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="auth/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "accounts/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="auth/password_reset_confirm.html",
        ),
        name="password_reset_confirm",
    ),
    path(
        "accounts/reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="auth/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),

    path(
    "accounts/password_change/",
    auth_views.PasswordChangeView.as_view(
        template_name="auth/password_change_form.html",
    ),
    name="password_change",
),
path(
    "accounts/password_change/done/",
    auth_views.PasswordChangeDoneView.as_view(
        template_name="auth/password_change_done.html",
    ),
    name="password_change_done",
),

    path(
        "club/",
        include("clubs.urls"),
    ),

    path(
        "",
        include("asistencia.urls"),
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
