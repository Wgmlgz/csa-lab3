# CSA-lab3

Мацюк Владимир Николаевич, P3215

```txt
lisp -> asm | acc | neum | hw | instr | struct | stream | port | pstr | prob2 | cache
```

С усложнением

## Язык программирования

### Описание синтаксиса

```bnf
<program> ::= <exp>

<exp> ::= "(" | <exp>*
              | <function>
              | <import-exp>
              | <exp-exp>
              | <let-exp>
              | <def-exp>
              | <set-exp>
              | <literal>
              | <identifier>
              | <function-call>
              | <operator-exp>
              | <if-exp>
              | <while-exp> ")"

<import-exp> ::= "import" <string>
<function> ::= "fn" <identifier> <parameter>* <type>? <exp>
<parameter> ::= "(" <identifier> <type> ")"
<type> ::= "int" | "str" "*"*
<let-exp> ::= "let" <identifier> <exp>
<def-exp> ::= "def" <identifier> <exp>
<set-exp> ::= "set" <identifier> <exp>
<literal> ::= <numeric> | <string>
<function-call> ::= <identifier> <exp>*
<operator-exp> ::= <bin-op> | <un-op>
<bin-op> ::= <bin-operator> <exp> <exp>
<un-op> ::= <operator> <exp>
<operator-exp> ::= <operator> <exp> <exp>
<bin-operator> ::= "+" | "-" | "*" | "/" | "=" | "%"
<un-operator> ::= "*" | "->" | "." | "-" | "+"
<if-exp> ::= "if" <exp> <exp> <exp>
<while-exp> ::= "while" <exp> <exp>

<identifier> ::= "'"? <character> <identifier-char>*
<numeric> ::= <digit>+
<string> ::= "\"" <string-character>* "\""
<identifier-char> ::= <character> | <digit>
<character> ::= "a" | "b" | ... | "z" | "A" | "B" | ... | "Z" | "_"
<digit> ::= "0" | "1" | ... | "9"
<string-character> ::= <character> | <digit> | <escape-sequence> | " "
<escape-sequence> ::= "\n" | "\\"
```

### Описание семантики

Программа организована в виде последовательности выражений, где каждое выражение обладает возвращаемым значением и ассоциированным с ним типом. Типы данных в языке могут быть базовыми (например, `int`, `char`), указателями на другие типы (например, `int*`), составными (например, `str`), или функциональными (например, `(int, str) -> int`). Составные типы представляют собой коллекции других типов и предоставляют доступ к своим элементам через идентификаторы. Например, тип `str` состоит из указателя на символы (`ptr char*`) и длины строки (`len in`t). Специальный тип `void`/`()` указывает на отсутствие возвращаемого значения и имеет размер 0. Все типы, за исключением `()`, имеют фиксированный размер больше нуля.

- Стратегия вычислений: Вычисления в языке следуют стратегии "вызова по значению", где аргументы функций вычисляются перед передачей в функцию. Эта стратегия обеспечивает предсказуемость выполнения кода за счет явного контроля времени и порядка вычислений.

- Области видимости: Язык поддерживает блочную область видимости: переменные, объявленные внутри блока (например, функции или условного выражения), доступны только в пределах этого блока, и его потомках. Области видимости вложенных блоков могут перекрываться, при этом внутренние блоки могут скрывать переменные с тем же именем из внешних блоков.

- Типизация: Язык строго типизирован, что означает необходимость явного указания типов переменных и функций. Система типов включает проверку типов на этапе компиляции, что способствует выявлению ошибок до выполнения программы.

- Виды литералов: Литералы в языке представляют базовые значения, такие как числа (42, 3.14), символы ('a'), строки ("hello"), и булевы значения (true, false). Литералы могут быть непосредственно использованы в выражениях без предварительного объявления.

- Виды выражений:

  - Пустые `()`: Эти выражения не выполняют никаких действий и возвращают специальное значение (), обозначающее "пустоту" или отсутствие результата. Используются для завершения ветвей выполнения, где результат не требуется.

  - Составные `(() () ... ())`: Составные выражения позволяют группировать несколько выражений в одно, где возвращаемое значение определяется последним выражением в группе. Это позволяет создавать сложные логические и вычислительные конструкции, где каждое действие влияет на конечный результат.

    - Пример:

    ```lisp
    (fn print (s str)
      ((print_str(s))
      (nl)))
    ```

    Здесь `print` вызывает функцию `print_str` для печати строки, за которой следует вызов `nl` для печати новой строки. Возвращаемое значение определяется выражением `(nl)`.

  - Условные `(if cond t f)`: Выбирает между `t` и `f` в зависимости от булева значения `cond`. Это позволяет реализовывать логику ветвления и принятия решений в программе.

    - Пример:

      ```lisp
      (fn factorial (n int) int
        (if (= n 0) 1 (* n (factorial (- n 1)))))
      ```

      Функция factorial использует условное выражение для проверки базового случая рекурсии: если n равно 0, возвращает 1; в противном случае рекурсивно вызывает себя.

  - Циклы `(while cond body)`: Выполняет `body` пока `cond` истинно, возвращая значение последней итерации.

    - Пример:

      ```lisp
      (fn print_n (n int)
        ...
        (while cur (
          (print_byte (+ (% (/ n cur) base) zero))
          (set cur (/ cur base)) ))
        ...)
      ```

  - Определение и присваивание переменных: `(let var val)`: Объявляет новую переменную `var` и инициализирует её значением `val`. Это выражение используется для создания локальных переменных с начальным значением.

    - Пример: `(let x 10)` создаёт переменную `x` с начальным значением `10`.

  - `(set var val)`: Присваивает переменной `var` новое значение `val`. Применяется для изменения значения уже существующих переменных.

    - Пример: `(set x 20)` изменяет значение переменной `x` на `20`.

  - Импорт модулей: `(import "path")`: Подключает модуль или библиотеку, расположенную по указанному пути `"path"`. Это выражение позволяет использовать функции, переменные и типы, определённые в других файлах или библиотеках.

    - Пример: `(import "./math")` импортирует модуль `math` из текущей директории.

  - Оператор доступа к члену структуры: `.` и `->`: Используется для доступа к полям структуры или элементам объекта. Оператор `.` используется для прямого доступа с разыменованием, тогда как `->` возвращает указатель.

    - Пример: `(-> ptr id)` обращается к полю `id` структуры, на которую указывает `ptr`.

  - Операторы: Используются для выполнения арифметических, логических и других операций над данными. Включают в себя стандартные операторы, такие как `+`, `-`, `*`, `/`, `%` для арифметики, и `=`, `!=` для сравнения.

    - Арифметические операторы:

      - `+`: Сложение двух чисел.
      - `-`: Вычитание двух чисел.
      - `*`: Умножение двух чисел.
      - `/`: Деление двух чисел.
      - `%`: Остаток от деления двух чисел.

    - Логические операторы:
      - `=`: Проверка на равенство.
      - `!=`: Проверка на неравенство.

    Примеры:

    - `(+ a b)`: Возвращает сумму `a` и `b`.
    - `(/ a b)`: Возвращает результат деления `a` на `b`.

## Организация памяти

В разработанном эмуляторе процессора внимание уделяется эффективному управлению памятью, с особым акцентом на работу с регистрами и оперативной памятью. В основе эмулятора лежит 64-битная архитектура, что обуславливает использование 64-битных регистров для выполнения операций и хранения данных.

### Регистры процессора

Для управления процессом выполнения программы и обработки данных предусмотрены следующие регистры:

- acc (Accumulator): Регистр аккумулятора, используемый для хранения промежуточных вычислительных результатов.
- ip (Instruction Pointer): Указатель инструкций, хранит адрес текущей выполняемой инструкции в оперативной памяти.
- ptr (Pointer): Универсальный указатель, предназначенный для доступа к оперативной памяти. Значение в ptr определяет, откуда будет загружено или куда будет сохранено значение при доступе к памяти.
- cmd (Command): Регистр команд, содержит текущую исполняемую инструкцию, загруженную из памяти по адресу, указанному в ip.
- stack: Служебный регистр для работы со стековой памятью, хранит адрес вершины стека для текущего контекста выполнения.

### Флаги управления

- run: Логический флаг, управляющий выполнением эмулятора. При установке в true программа продолжает выполнение, в false — останавливается.
  Организация памяти
  Оперативная память эмулятора подразделяется на две основные области:

Глобальная память: Начинается с адреса 0x00 и расширяется вверх. В этой области размещаются исполняемые инструкции программы и константы. Доступ к глобальной памяти осуществляется через установку соответствующего адреса в регистр ptr.

Стековая память: Организована так, что начинается с максимально доступного адреса и расширяется вниз. Стек используется для динамического выделения памяти, в том числе для хранения адресов возврата из функций, локальных переменных и параметров вызова. Для управления стековой памятью служит регистр stack, указывающий на текущую вершину стека.

### Работа с памятью

Для выполнения операций с памятью необходимо установить адрес в регистре ptr. После этого, при любом обращении к памяти, будет происходить загрузка или запись данных по указанному адресу. Таким образом, взаимодействие с памятью реализуется через комбинацию регистра ptr и операций чтения/записи.

### Стековая память

В процессе работы программы особое внимание уделяется управлению стековой памятью. Стековая память организована таким образом, что в начале выделяется место для хранения возвращаемого значения блока. После этого аллоцируется пространство для локальных переменных функции. Затем, в соответствии с вложенностью выражений и блоков кода, выделяются дополнительные сегменты памяти.

Когда выполнение программы доходит до вложенного выражения или блока кода, память для него выделяется поверх уже существующей стековой памяти. Если вложенных блоков несколько и они выполняются последовательно, то после завершения каждого из них занимаемая им память может быть переиспользована для следующего блока.

### Пример организации стековой памяти блоков

Предположим, у нас есть стек с адресом начала 0x0000000000010000. Рассмотрим, как будет выглядеть распределение памяти при выполнении определённого блока кода:

| Address  | User          | Owner  |
| -------- | ------------- | ------ |
| `0xffc0` | `child_var_n` | child  |
| `0xffc8` | `child_var_2` | child  |
| `0xffd0` | `child_var_1` | child  |
| `0xffd8` | `child_ret`   | child  |
| `0xffe0` | `var_n`       | scope  |
| `0xffe8` | `var_2`       | scope  |
| `0xfff0` | `var_1`       | scope  |
| `0xfff8` | `ret`         | return |

При вызове блока, если его используется в другом выражении память будет переиспользована.

| Address  | User               | Owner  |
| -------- | ------------------ | ------ |
| `0xffc0` |                    | child  |
| `0xffc8` | `child_var_n`      | child  |
| `0xffd0` | `child_var_2`      | child  |
| `0xffd8` | `child_var_1`      | child  |
| `0xffe0` | `var_n`            | scope  |
| `0xffe8` | `var2`             | scope  |
| `0xfff0` | `var1`             | scope  |
| `0xfff8` | `ret`, `child_ret` | return |

### Вложенный вызов функций

При выполнении вложенных функции система выделяет место для возвращаемого значения, адреса возврата и аргументов. Затем, аргументы вычисляются в выделенное место, после чего происходит смещение указателя стека и переход (jmp) к адресу функции.

| Address               | User         | Owner            |
| --------------------- | ------------ | ---------------- |
| `0xffc0`              | ...          | callee           |
| `0xffc8`              | `body_block` | callee           |
| `0xffd0`              | `arg_2`      | caller           |
| `0xffd8`              | `arg_1`      | caller           |
| `0xffe0`              | `re_addr`    | caller           |
| `0xffe8` <- new_stack | `ret`        | callee -> caller |
| `0xfff0`              |              | caller           |
| `0xfff8` <- old_stack |              | caller           |

## Система команд

### Особенности процессора

- Типы данных и машинные слова: В эмуляторе используются 64-битные машинные слова. Поддерживаются операции с целочисленными значениями, с возможностью работы с различными размерами данных (1, 2, 4, 8 байт).
- Устройство памяти и регистров, адресации: Память подразделяется на глобальную и стековую. Регистры включают аккумулятор (`acc`), указатель команд (`cmd`), указатель стека (`stack`), указатель инструкций (`ip`), и универсальный указатель (`ptr`). Адресация выполняется путём установки необходимого значения в регистр `ptr`.
- Устройство ввода-вывода: Ввод-вывод осуществляется через специализированные команды, позволяющие читать из потока ввода и записывать в поток вывода, используя управляемые дескрипторы устройств.
- Поток управления и системы прерываний: Управление потоком выполнения инструкций происходит через команды перехода, условные переходы.

### Способ кодирования инструкций

Инструкции кодируются в виде бинарных кодов, где первые 4 байта обычно служат тегом инструкции, а последующие 4 байта — аргументом команды. Это позволяет организовать инструкции в удобном для исполнения и анализа формате. Для работы с инструкциями используются современные структуры данных, обеспечивающие высокую скорость обработки и гибкость в добавлении новых команд.

### Набор инструкций

| Инструкция     | Описание                                                                  |
| -------------- | ------------------------------------------------------------------------- |
| nop            | Не выполняет никаких действий.                                            |
| halt           | Останавливает выполнение программы.                                       |
| deref          | Загружает значение из памяти, на которое указывает acc, в acc.            |
| deref_4        | То же, что и deref, но загружает только 4 байта.                          |
| deref_2        | То же, что и deref, но загружает только 2 байта.                          |
| deref_1        | То же, что и deref, но загружает только 1 байт.                           |
| load           | Копирует аргумент команды в аккумулятор.                                  |
| ptr_acc        | Устанавливает ptr равным значению acc.                                    |
| ptr_ip         | Устанавливает ptr равным сумме acc и ip.                                  |
| acc->ptr       | Копирует значение из аккумулятора в ptr.                                  |
| acc->stack     | Копирует значение из аккумулятора в стек.                                 |
| stack->acc     | Копирует значение из стека в аккумулятор.                                 |
| stack_offset   | Складывает значение вершины стека с аргументом команды и сохраняет в acc. |
| stack\_-offset | Вычитает аргумент команды из вершины стека и сохраняет результат в acc.   |
| shift_stack    | Сдвигает стек на значение аргумента команды.                              |
| unshift_stack  | Сдвигает стек на обратное значение аргумента команды.                     |
| local_ptr      | Вычисляет локальный указатель памяти на основе вершины стека и аргумента. |
| local_set      | Устанавливает значение в локальной памяти равное acc.                     |
| local_get      | Загружает значение из локальной памяти в acc.                             |
| local_set_4    | То же, что и local_set, но для 4 байт.                                    |
| local_get_4    | То же, что и local_get, но для 4 байт.                                    |
| local_set_2    | То же, что и local_set, но для 2 байт.                                    |
| local_get_2    | То же, что и local_get, но для 2 байт.                                    |
| local_set_1    | То же, что и local_set, но для 1 байта.                                   |
| local_get_1    | То же, что и local_get, но для 1 байта.                                   |
| global_set     | Устанавливает глобальное значение в памяти равное acc.                    |
| global_get     | Загружает глобальное значение из памяти в acc.                            |
| inc            | Увеличивает значение acc на 1.                                            |
| inc8           | Увеличивает значение acc на 8.                                            |
| dec            | Уменьшает значение acc на 1.                                              |
| dec8           | Уменьшает значение acc на 8.                                              |
| load_cmd       | Загружает команду в cmd по адресу указанному в ip.                        |
| jmp_acc        | Переход к адресу в acc.                                                   |
| jmp            | Переход к адресу, указанному аргументом команды.                          |
| jmp_if         | Условный переход, если значение в acc истинно.                            |
| jmp_if_false   | Условный переход, если значение в acc ложно.                              |
| out            | Выводит значение acc в устройство вывода.                                 |
| add_cmd        | Складывает аргумент команды с acc.                                        |
| add_local      | Складывает локальное значение с acc.                                      |
| sub_local      | Вычитает локальное значение из acc.                                       |
| mul_local      | Умножает acc на локальное значение.                                       |
| div_local      | Делит acc на локальное значение.                                          |
| rem_local      | Остаток от деления acc на локальное значение.                             |
| invert_bool    | Инвертирует булево значение в acc.                                        |

<!-- Раздел должен включать:

Особенности процессора (всё необходимое для понимания системы команд):

типы данных и машинных слов;
устройство памяти и регистров, адресации;
устройство ввода-вывода;
поток управления и системы прерываний;
и т.п.

Набор инструкций.
Способ кодирования инструкций:

по умолчанию можно использовать современные структуры данных;
требование бинарного кодирования -- особенность конкретного варианта.

Описания системы команд должно быть достаточно для её классификации (CISC, RISC, Acc, Stack). -->

## Транслятор

### Интерфейс командной строки

Командная утилита для преобразования исходного кода в исполняемый файл. Принимает на вход исходный файл и опционально целевой файл, поддерживает флаг -d/--debug для активации режима отладки.

```
Usage: python translator.py <input_file> [target_file] [-d/--debug]
  Flags:
    -d/--debug enables debug output
```

### Принципы работы

Реализовано в папке `src/lang`

- Компиляция:

  - Токенизация текста: Преобразование исходного кода в последовательность токенов, представляющих синтаксические единицы, такие как идентификаторы, числа.
  - Построение S-выражений: Организация токенов в структурированное представление, облегчающее анализ и понимание взаимосвязей между элементами кода.
  - Компиляция в объектный код: Преобразование структурированного представления в промежуточный код, готовый к последующей линковке.

- Линковка:
  - Расчет сдвигов: Определение смещений для переменных и функций в памяти, что необходимо для корректной адресации во время исполнения.
  - Сборка инструкций в линейный набор: Объединение всех частей кода, включая глобальные и локальные участки, в единый поток инструкций.
  - Обработка меток: Разрешение ссылок на метки, функции и переменные, преобразование символьных имен в конкретные адреса памяти или инструкции, чтобы обеспечить правильную связь и вызовы в исполняемом коде.

## Модель процессора

Раздел подразумевает разработку консольного приложения:

Входные данные:

Имя файла для чтения машинного кода.
Имя файла с данными для имитации ввода в процессор.

Выходные данные:

Вывод данных из процессора.
Журнал состояний процессора, включающий:

состояния регистров процессора;
выполняемые инструкции (возможно, микрокод) и соответствующие им исходные коды;
ввод/вывод из процессора.

Раздел должен включать:

Схемы DataPath и ControlUnit, описание сигналов и флагов:

В случае, если схемы DataPath и ControlUnit совмещены, должна быть убедительная аргументация в тексте отчёта.
Не стоит полностью отрисовывать сигнальные линии от ControlUnit ко всем элементам схемы, это загромождает схему и усложняет её чтение. Обозначьте их как сделано в примере.
Если вы настаиваете на полной отрисовке сигнальных линий, то они должны визуально отличаться от линий передачи данных / адресов.
Схемы должны помещаться на экран.
В случае, если схемы не соответствуют данным требованиям, они могут быть признаны нечитаемыми, следовательно, непроверяемыми. Пример нечитаемой схемы: link

Особенности реализации процесса моделирования.

Обратите внимание, что схемы должны отражать аппаратную структуру процессора и его элементов. Делайте схемы читаемыми. На структурных элементах отображайте порты (если у вас две стрелки в регистр -- это ошибка), не забывайте мультиплексоры.
Рекомендации по реализации:

строгое разделение DataPath и ControlUnit на уровне кода/интерфейсов/схем;
реализация машинной арифметики на уровне схем не требуется, просто складывайте, вычитайте, умножайте и делите так, как будто это поддержано АЛУ за один такт;
при моделировании процессов ориентироваться на схему процессора и её функционирование (а не писать отвлечённый код).

## Тестирование

Раздел должен включать:

Краткое описание разработанных тестов.

Описание работы настроенного CI.

Реализацию следующих алгоритмов (должны проверяться в рамках интеграционных тестов):

hello -- напечатать hello world;

cat -- печатать данные, поданные на вход симулятору через файл ввода (размер ввода потенциально бесконечен);

hello_user_name -- запросить у пользователя его имя, считать его, вывести на экран приветствие (< -- ввод пользователя через файл ввода, > вывод симулятора):

> What is your name?
> < Alice
> Hello, Alice!

алгоритм согласно варианту;

дополнительные алгоритмы, демонстрирующие особенности вашего варианта (синтаксис, работу специфических команд и т.п.).

Необходимо показать работу разработанных алгоритмов.

Для одной из программ сделать подробное описание с комментариями в рамках отчёта, включая: использование разработанных программ, исходный код, машинный код, результат работы и журнал состояний модели процессора.
Для всех алгоритмов необходимо привести ссылки на их golden тесты. Они должны включать: алгоритм, машинный код и данные, ввод/вывод, журнал работы процессора.
Если размер журнала модели процессора слишком большой (сотни килобайт), его полное включение в golden test нецелесообразно. Необходимо адаптировать журнал под каждый алгоритм, добившись достаточной репрезентативности для проверки задания.
Все листинги исходного кода должны быть отформатированы.

Кроме того, в конце отчёта необходимо привести следующий текст для трёх реализованных алгоритмов (необходимо для сбора общей аналитики по проекту):
| ФИО | <алг> | <LoC> | <code байт> | <code инстр.> | <инстр.> | <такт.> | <вариант> |
где:

алг. -- название алгоритма (hello, cat, или как в варианте)
прог. LoC -- кол-во строк кода в реализации алгоритма
code байт -- кол-во байт в машинном коде (если бинарное представление)
code инстр. -- кол-во инструкций в машинном коде
инстр. -- кол-во инструкций, выполненных при работе алгоритма
такт. -- кол-во тактов, которое заняла работа алгоритма
