# Practical Assignment 4. Point Cloud Vectorization. Part 2

## Необходимо

### 1. Настроить окружение

- Скачать и установить [Blender](https://www.blender.org/download/) (можно использовать портативную версию)
- Получить доступ к папке [3D Assets](https://disk.yandex.ru/d/KdaNdKgaHsZ3JA)

### 2. Создать цифровую модель рельефа (ЦМР)

- Открыть результат второй практической работы, сохранить точки земли в формате `pcd`.
- Создать новый проект CloudCompare и загрузить в него точки земли.
- Выполнить следующие действия в CloudCompare:
	- Посчитать нормали к точкам.
	- Ориентировать нормалию
	- Построить триангуляционную поверхность.
	- Отфильтровать полигоны по плотности.
	- Удалить лишние полигоны на границах участка.
	- Экспортировать результат в формате `obj`.
	- Сохранить проект CC в формате `bin`.

### 3. Создать модель колеи в Blender

- Ознакомиться с соответствующим [разделом документации из описания алгоритма](https://github.com/lytkinsa96/101_Digital_Modeling/blob/develop/Practical_Assignment_4/scripts/README.md#curve-and-polyline-consistency)
- Создать полилинию, описывающую один из рельсов колеи участка, используя любое удобное ПО.
	- Полилиния должна быть привязана к точкам облака.
	- Полилиния должна состоять только из прямолинейных сегментов (исключая дуги).
- Скопировать полученную полилинию для создания второй, соответствующей другому рельсу.
	- Обе полилинии должны содержать одинаковое количество вершин.
	- Обе полилинии должны располагаться согласованно относительно поверхности головки рельса: 
		- Если первая полилиния находится ближе к внутренней стороне колеи, то и вторая должна быть расположена ближе к внутренней стороне, и аналогично для внешней стороны. 
		- Это согласование необходимо для более точного определения оси пути алгоритмом.
- Сохранить обе полилинии в формате `obj`.
- Скачать профиль рельса и модель шпалы из папки [3D Assets](https://disk.yandex.ru/d/KdaNdKgaHsZ3JA).
- Открыть Blender и перейти во вкладку `Scripting`.
- Создать новый скрипт и скопировать в него содержимое [track_modeling.py](https://github.com/lytkinsa96/101_Digital_Modeling/blob/develop/Practical_Assignment_4/scripts/track_modeling.py)
- Изменить пути до необходимых файлов в скрипте и запустить его.
- Экспортировать результаты в формате `obj` с ориентацией `YZ`:
	- Ось колеи.
	- Рельсы. 
	- Шпалы.

### 4. Собрать сцену

- Собрать модель сцены в любом удобном ПО, опираясь на облако точек и используя модели из папки [3D Assets](https://disk.yandex.ru/d/KdaNdKgaHsZ3JA).
- Экспортировать отдельные "слои" сцены:
	- Все вертикальные столбы (кроме знаков и светофоров). 
	- Все знаки (временные и постоянные).
	- Все светофоры.
	- Все ограждения.
	- Все платформы.
	- Все прочие объекты.
- Разбить каждый "слой" (кроме последнего) на "экземпляры", экспортируя каждый объект в отдельный файл `obj`.
- С помощью CloudCompare определить положение и размеры ограничивающей рамки (bounding box) для каждого "экземпляра".
	- Занести полученную информацию в соответствующие файлы `json`, добавив следующие поля.

```json 
{
	"Position": { 
		"X": , 
		"Y": , 
		"Z": 
	},
	"Bbox": { 
		"Center": { 
			"X": , 
			"Y": , 
			"Z": 
		}, 
		"Dimensions": { 
			"X": , 
			"Y": , 
			"Z": 
		} 
	} 
} 
```

## Результат

Выполненный проект должен содержать следующие файлы, загруженные в ваш личный каталог на Яндекс.Диске (`/3_Output_data/Assignment_4/`):
- Проект CC, `./CloudCompare.bin`
- Облако точек земли, `./Ground.pcd`
- ЦМР, `./DTM.obj`
- Две полилинии, `./<Left,Right>_Rail_Curve.obj`
- Ось колеи, `./Track_Axis.obj`
- Модель рельс, `./Rails.obj`
- Модель шпал, `./Sleepers.obj`
- Модели "слоев", `./<Pole,Sign,Lights,Fence,Platform,Other>.obj`
- Модели "экземпляров", `./<Class_label>/<Class_label>_<№>.obj`
- Соответствующие файлы с метаданными,`./<Class_label>/<Class_label>_<№>.json`

## Материалы 

- [Туториал по созданию ЦМР](https://disk.yandex.ru/i/RdywuLMSGlDWMw)
- [Туториал по моделированию колеи](https://disk.yandex.ru/i/k-1J1KA9H8QeDQ)
- [Туториал по определению метаданных объектов](https://disk.yandex.ru/i/2xFvOoCrUxmfHw)

