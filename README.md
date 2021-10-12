Github analyzer!

To use:

set your Github token in main.py

Run for help:

python main.py -h

Example:

python main.py -o juliangarnier -r anime -ds 2018-01-01 -de 2021-10-01 -b master

To work with big repositories add -t "your_token" to get higher rate limit



Техническое задание:

Необходимо сделать python-скрипт, анализирующий репозиторий на GitHub. 
Скрипт принимает следующие аргументы вызова (в командной строке):
- Адрес (URL) репозитория
- Дата начала анализа (по умолчанию: неограниченно давно)
- Дата конца анализа (по умолчанию: настоящий момент времени, дата+время вызова скрипта)
- Ветка репозитория, которая будет анализироваться (по умолчанию master)

Детали задачи:
Анализ репозитория должен производится с помощью REST API GitHub-а (https://docs.github.com/en/rest).
Результат работы скрипта выводится в stdout. Результат включает в себя:
- Активные участники. Таблица с двумя колонками: login автора, количество коммитов. Содержит топ-30 самых активных участников, отсортированных по количеству коммитов (по убыванию). Коммиты считаются в диапазоне дат, заданном при вызове и на ветке заданной при вызове.
- Количество открытых и закрытых PR. Считаться должны те PR, которые были закрыты и открыты в указанный период времени и для которых базовой является ветка, указанная в параметре скрипта.
- Количество "устаревших" PR. "Устаревшим" стоит считать PR, который был открыт более 30 дней назад и остаётся таким по текущий момент. Анализировать стоит только те PR, для которых базовой является ветка, указанная в параметре скрипта.
- Количество открытых и закрытых issues в указанном периоде времени и ветке.
- Количество "устаревших" issues в указанной ветке. "Устаревшим" следует считать issue, открытый более 14 дней назад и остающийся открытым по текущий момент.

Итоговый скрипт нужно постараться сделать чистым, с соблюдением рабочего этикета и общепринятых в python-community норм оформления программ. Скрипт должен быть отказоустойчивым, с учётом возможных ограничений (например: ограничение API на количество вызовов).

Мы не ограничиваем кандидата в сроках исполнения задания. Однако отметим, что в среднем на его выполнение уходит около 1-й недели.  Отдельно просим в пояснении к выполненному заданию указать количество времени, которое у вас ушло на его выполнение.
