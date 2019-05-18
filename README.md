Этот проект представляет собой PTZ - контроллер в качестве android-приложения для ONVIF-камер, подключенных в одну сеть с сервером-обработчиком. Не требует предустановки на устройстве специальных OVPN приложений. Не получает видео с камер, а только управляет ими (Continuous move и Preset move). Для отслеживания перемещения использует snapshot-ы. 

Для использования:

    1. Скопируйте на сервер, включенный в одну OVPN или локальную сеть с камерами, файл Controller_backend.py
    2. Установите на своё Android устройство .apk-файл, который находится по ссылке:
        https://drive.google.com/file/d/11pqG0hbc3aJovCUvVH354Pt0PYq8JZoo/view?usp=sharing
    3. Внутри приложения введите IP-адрес вашего сервера и порт, на котором запускается py-файл (по умолчанию 8081).
    
Готово!


Server based PTZ controller for ONVIF cameras. Works from WAN on Android devices, does not consume video stream. Only moves camera head and calls / creates presets directly (one button call).

Let's start:

    1. Copy Controller_backend.py to your server (placed in OVPN or local network with ONVIF-cameras)
    2. Install on your Android-device .apk file. Link here>>
            https://drive.google.com/file/d/11pqG0hbc3aJovCUvVH354Pt0PYq8JZoo/view?usp=sharing
    3. Enter your server IP and port.
    
    
