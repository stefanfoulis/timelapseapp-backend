from django.shortcuts import render


def progress(request):
    return render(request, "progress_experiment/index.html", {})
