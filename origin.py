import csv
import re
from datetime import datetime


# ---------- Параметризованный декоратор логгера ----------
def logger(path):
    def __logger(old_function):
        def new_function(*args, **kwargs):
            call_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            func_name = old_function.__name__
            args_repr = ', '.join(map(repr, args))
            kwargs_repr = ', '.join(f"{k}={v!r}" for k, v in kwargs.items())
            all_args = ', '.join(filter(None, [args_repr, kwargs_repr]))

            result = old_function(*args, **kwargs)

            log_entry = f"{call_time} – {func_name}({all_args}) -> {result!r}\n"
            with open(path, 'a', encoding='utf-8') as log_file:
                log_file.write(log_entry)

            return result

        return new_function

    return __logger

# Основной код из старого домашнего задания

@logger('phonebook.log')   # логи будут в файле phonebook.log
def normalize_name(parts):
    """
    parts – список из первых трёх полей (lastname, firstname, surname)
    Возвращает кортеж (lastname, firstname, surname)
    """
    # Склеиваем все три поля через пробел и разбиваем
    full = ' '.join(parts).strip().split()
    lastname = full[0] if len(full) > 0 else ''
    firstname = full[1] if len(full) > 1 else ''
    surname = full[2] if len(full) > 2 else ''
    return lastname, firstname, surname

@logger('phonebook.log')
def normalize_phone(phone):
    if not phone:
        return ''
    phone = phone.strip()
    # Добавочный номер
    ext = ''
    match = re.search(r'(доб\.?\s*)(\d+)', phone, re.IGNORECASE)
    if match:
        ext = ' доб.' + match.group(2)
        phone = re.sub(r'доб\.?\s*\d+', '', phone, flags=re.IGNORECASE)
    # Оставляем только цифры
    digits = re.sub(r'\D', '', phone)
    # Форматируем
    if len(digits) == 11 and digits[0] in ('7', '8'):
        digits = digits[1:]
        number = f'+7({digits[0:3]}){digits[3:6]}-{digits[6:8]}-{digits[8:10]}'
    elif len(digits) == 10:
        number = f'+7({digits[0:3]}){digits[3:6]}-{digits[6:8]}-{digits[8:10]}'
    else:
        number = phone  # нераспознанный формат оставляем как есть
    return number + ext

# Чтение исходного файла
with open('phonebook_raw.csv', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter=',')
    contacts_list = list(reader)

# Отделяем заголовок (если есть)
header = []
if contacts_list and contacts_list[0][0].lower() == 'lastname':
    header = contacts_list[0]
    data = contacts_list[1:]
else:
    data = contacts_list

# Обрабатываем каждую строку
normalized = []
for row in data:
    # Дополняем до 7 полей
    while len(row) < 7:
        row.append('')
    # Пропускаем строки, где все три первых поля пусты
    if all(not cell.strip() for cell in row[:3]):
        continue

    # Нормализуем ФИО
    last, first, sur = normalize_name(row[:3])
    row[0], row[1], row[2] = last, first, sur

    # Нормализуем телефон
    row[5] = normalize_phone(row[5])

    normalized.append(row)

# Объединение дублей по ФАМИЛИИ, ИМЕНИ, ОТЧЕСТВУ (все три)
unique = {}
for row in normalized:
    key = (row[0].lower(), row[1].lower(), row[2].lower())
    if key not in unique:
        unique[key] = row[:]        # сохраняем копию
    else:
        existing = unique[key]
        # Заполняем недостающие данные (индексы 3..6)
        for i in range(3, 7):
            if not existing[i] and row[i]:
                existing[i] = row[i]

# Формируем результат (заголовок + данные)
result = []
if header:
    result.append(header)
result.extend(unique.values())

# Запись в файл (без пустых строк в конце)
with open('phonebook.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerows(result)

print(f'Обработано записей: {len(normalized)}')
print(f'Уникальных контактов: {len(unique)}')