import os
import numpy as np
from PIL import Image
import keras
from keras.layers import Input
from keras.models import Model
from keras.applications.resnet_v2 import ResNet50V2, preprocess_input, decode_predictions
from tensorflow.compat.v1 import ConfigProto, InteractiveSession

# Конфигурация GPU (для CPU эти строки можно закомментировать или оставить без вреда)
config = ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.7
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)

height, width = 224, 224
ncol = 3

# Загружаем предобученную сеть ResNet50V2
visible2 = Input(shape=(height, width, ncol), name='imginp')
resnet = ResNet50V2(
    include_top=True,
    weights='imagenet',
    input_tensor=visible2,
    input_shape=None,
    pooling=None,
    classes=1000
)


def read_image_files(files_max_count, dir_name):
    """Читает до files_max_count изображений из папки dir_name.
    Возвращает (количество реально загруженных файлов, список объектов PIL.Image).
    """
    # Получаем список файлов, отфильтровывая только изображения
    valid_ext = ('.jpg', '.jpeg', '.png')
    all_files = [f for f in os.listdir(dir_name) if f.lower().endswith(valid_ext)]
    files_count = min(files_max_count, len(all_files))

    image_box = []
    for i in range(files_count):
        img_path = os.path.join(dir_name, all_files[i])
        img = Image.open(img_path)
        image_box.append(img)
    return files_count, image_box


def getresult(image_box):
    """Принимает список PIL.Image, возвращает декодированные предсказания для каждого.
    Формат возврата: список из списков, каждый внутренний список содержит top-1 предсказание,
    пригодный для использования в шаблоне как нейросетевой словарь.
    """
    if not image_box:
        return []

    # Подготовка массива изображений
    images_resized = []
    for img in image_box:
        img_resized = img.resize((height, width))
        img_array = np.array(img_resized) / 255.0
        # Приводим к нужной форме (224,224,3)
        if img_array.shape[-1] == 4:  # PNG с альфа-каналом
            img_array = img_array[:, :, :3]
        images_resized.append(img_array)

    images_np = np.array(images_resized)
    # Предобработка для ResNet (нормализация по стандарту ImageNet)
    images_preprocessed = preprocess_input(images_np)

    # Предсказание
    predictions = resnet.predict(images_preprocessed)
    # Декодируем top-1
    decoded = decode_predictions(predictions, top=1)

    # Преобразуем в удобный для шаблона словарь: {имя класса: вероятность}
    result = []
    for pred in decoded:
        # pred = [(class_id, class_name, probability)]
        result.append([{'class': pred[0][1], 'prob': float(pred[0][2])}])
    return result