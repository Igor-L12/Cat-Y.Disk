import requests
import magic
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render


def check_disk(public_key):
    """Получение списка файлов и папок из публичной ссылки."""
    url = "https://cloud-api.yandex.net/v1/disk/public/resources"
    params = {
        "public_key": public_key
        }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return {"error": response.json().get("message", "Ошибка при доступе к Яндекс.Диску")}


def get_download_url(public_key, path=None):
    """Получение ссылки для скачивания файла."""
    url = "https://cloud-api.yandex.net/v1/disk/public/resources/download"
    params = {"public_key": public_key}
    if path:
        params["path"] = path
    response = requests.get(url, params=params)
    return response.json().get("href")


def index(request):
    """Отображение списка файлов."""
    if request.method == "POST":
        public_key = request.POST.get("public_key")
        files = check_disk(public_key)

        if "error" in files:
            messages.error(request, "Некорректная ссылка")
            return render(request, "disk/index.html", {"error": files["error"]})

        items = files.get("_embedded", {}).get("items", [])
        context = {
            "items": items, 
            "public_key": public_key
            }
        return render(request, "disk/public_disk.html", context)

    return render(request, "disk/index.html")


def download(request):
    """Скачивание файла."""
    public_key = request.GET.get("public_key")
    path = request.GET.get("path")

    download_url = get_download_url(public_key, path)
    response = requests.get(download_url)
    filename = path.split("/")[-1]

    magic_instance = magic.Magic(mime=True)
    mime_type = magic_instance.from_buffer(response.content)

    file_response = HttpResponse(response.content, content_type=mime_type)
    file_response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return file_response
