from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ClubForm
from .models import Club


@login_required
def configuracion_club(request):
    # Por ahora usamos el primer club creado.
    # Después lo vamos a vincular al usuario logueado.
    club = get_object_or_404(Club, pk=1)

    if request.method == "POST":
        form = ClubForm(
            request.POST,
            request.FILES,
            instance=club,
        )

        if form.is_valid():
            form.save()
            return redirect("configuracion_club")

    else:
        form = ClubForm(instance=club)

    return render(
        request,
        "clubs/configuracion.html",
        {
            "form": form,
            "club": club,
        },
    )