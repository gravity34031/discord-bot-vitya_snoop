

























# 1. models.Model создает как бы связь с таблицами баз данных. При создании models.Model создается так же менеджер, который за эту связь и отвечает. По сути нужен для описания таблиц баз данных, полей, связей между таблицами. CharField - создает поле в бд с текстом. ForeignKey - Внешний ключ на другую таблицу.
# 2. миграции позволяют 'синхронизировать' какие либо изменения между models.Model - классом таблицы в python и таблицей непосредственно в базе данных. сначала делаем makemigrations. Эта команда записывает изменения с специальные файлы, так же выполняется и отслеживание версий миграций. Потом migrate для применения миграций
# 3. queryset - структура. которая получается при получении каких-то данных из бд. Отличается тем, что имеет множество других методов, что позволяют дополнительно данные фильтровать, аннотировать и прочее. А ленивый queryset значит, что запрос в бд не выполняется весь целиком сразу, а выполняется каждый раз, постепенно.
# 4. filter - данные фильтрует по какому-то полю. На выходе получаем список. get - получение одного объекта. exclude - обратно filter: исключает что-то из выборки. annotate - как бы добавляет новое поле к объектам, которые основе на счете чего-то(сумма, среднее, минимальное и прочее). aggregate он соберет все какие-то значения и выдаст лишь одно, тоже среднее и прочее
# 5. проблема возникает из-за того, что по стандарту запросы в django выполняются лениво. Поэтому, когда есть связи с другими таблицами, получение данных из этих таблиц выполняется не один раз, а каждый, для каждого объекта. Чтобы это избежать используется select_related и prefetch_related
# 6. select_related - для foreignkey, prefetch_related - для many-to-many. Они служат для сбора данных из связанных таблиц, позволяя делать запрос всего один раз, а не куча, избегая проблемы n+1
# 7. менеджер - это как бы связующее звено между таблицей базы данных и моделью. Менеджер позволяет выполнять запросы к таблице. При создании модели назначается один менеджер, их можно переписывать и добавлять новые. Менеджер по сути и создает, отдает queryset. 
# 8. сериалайзер устроен таким образом, что json данные он переделывает в более сложные(например, модель) и наоборот, чтобы python мог с этим работать. Так же он позволяет параллельно с этим данные валидировать. ModelSerializer, ListSerializer, DictSerializer
# 9. По сути APIView по сравнению с остальными - более базовый класс, остальные от него наследуются. Он не обладает ничем лишним, но позволяет делать view для обработки всех CRUD запросов. GenericAPIView - дженерики уже заготовленные виды view, у которых разные предназначения, и они отвечают за разные CRUD запросы: для чтения, для записи, для удаления, для чтения и записи и прочее. ViewSet же самая большая надстройка, в которой большая часть часто повторяющегося функционала реализована за нас. Так же он является более общим, чем дженерики, потому что в нем можно прописывать все CRUD операции. Так же вместо кучи кода можно просто написать аргументом queryset, permission_classes и прочее
# 10. middleware - функция, которая выполняется до и после выполнения view, между запросами. Позволяет реализовать какое-то дополнительное поведение: например, на определенный ендпоинт запретить доступ определенному пользователю. Подключается в settings.py в разделе middleware. 
# 11. не знаю, расскажи
# 12. первым делом - добавить нужные приложения. Добавить middleware. Там для некоторых дополнительных библиотек определяется настройка. Нужно выключить режим debug. Скрыть secretkey в .env. Прописать подключение к бд, при этом беря логин-пароль из .env. 



# Спроектируй модели для блога: User, Post, Comment, Tag. Укажи поля и типы связей (OneToMany, ManyToMany и т.д.). Коротко объясни, почему так.

# Напиши миграцию (команду и последовательность) — какие команды ты выполните, если только что добавил поле summary = models.TextField(null=True, blank=True) в Post.

# Напиши QuerySet, который получает последние 10 постов с количеством комментариев для каждого поста (в одном запросе, оптимизированно).

# class User(models.Model):
#     name = models.CharField(max_length=255)
#     email = models.EmailField(unique=True)
#     avatar = models.ImageField(null=True, blank=True)
    
# class Post(models.Model):
#     title = models.CharField(max_length=255)
#     text = models.TextField()
#     author = models.ForeignKey(User, on_delete=models.CASCADE)
#     tags = models.ManyToManyField('Tag', blank=True)
# class Comment(models.Model):
#     body = models.TextField()
#     author = models.ForeignKey(User, on_delete=models.CASCADE)
#     post = models.ForeignKey(Post, on_delete=models.CASCADE)
# class Tag(models.Model):
#     name = models.CharField(max_length=255)
#     posts = models.ManyToManyField('Post', blank=True)

# python manage.py migrate
# python manage.py makemigrations

# queryset: Post.objects.annotate(comment_count=Count('comment'))[:10]


# У тебя есть модели:

# class Author(models.Model):
#     name = models.CharField(...)

# class Book(models.Model):
#     title = models.CharField(...)
#     author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
#     rating = models.FloatField()
#     published_at = models.DateField()

# Напиши запросы:

# получить всех авторов с их средним рейтингом книг (только авторы с >= 3 книг), отсортированных по среднему рейтингу desc;
# Author.objects.annotate(avg_rating=Avg('books__rating')).filter(books__count__gte=3).order_by('-avg_rating')
# получить книги, опубликованные за последние 2 года, с автором (без N+1).
# Book.objects.filter(published_at__gt=timezone.now() - datetime.timedelta(days=365*2)).select_related('author')





































# # 1-2 пропущу, не надо проверять
# # 3) copy - делает просто поверхностную копию объекта. deep-copy - влючая все подобъекты объекта(например, списки в списке)
# # 4) генератор - частный, более простой способ создать итератор. Генераторная фукнкция должна обладать оператором yield. Данная функция выполняется до тех пор, пока не встретит yield. Потом, чтобы продолжить выполнение, нужно использовать next. Тогда вернется значение и действие генератор-функции продолжится до следующего yield. Отличаются тем, что значения в них не высчитывается сразу, не хранится в памяти, а высчитывается налету, когда надо.
# # 5) описал выше. Возвращает значение из генератор-функции и продолжает ее работу до следующего yield

# # # 1)

# nums = [1, 2, 3, 2, 1, 4, 5, 3]
# new = []
# for i in nums:
#     if i not in new:
#         new.append(i)
# # Ожидаемый результат: [1, 2, 3, 4, 5]

# # 2)
# def flatten(lst: list):
#     for i in lst:
#         if isinstance(i, (list, tuple)):
#             yield from flatten(i)
#         else:
#             yield i
# # Реализуй функцию flatten(lst), которая превращает вложенные списки в один:

# print(list(flatten([1, [2, [3, 4]], 5])))  
# результат: [1, 2, 3, 4, 5]

# 3)
# class MyReversed:
#     def __init__(self, elements):
#         self.elements = elements
#         self.current = len(elements)
#     def __iter__(self):
#         return self
#     def __next__(self):
#         if self.current > 0:
#             self.current-=1
#             return self.elements[self.current]
#         raise StopIteration

# iterator = MyReversed([1, 2,3 ,5 ,7])
# print()
# for i in iterator:
#     print(i)











# # 1)
# class VowelIterator:
#     def __init__(self, text):
#         self.text = text
#         self.current = 0
        
#     def __iter__(self):
#         return self
    
#     def __next__(self):
#         for char in self.text[self.current:]:
#             self.current+=1
#             if char in 'аеёиоуыэюяaeiouy':
#                 return char
#         raise StopIteration
# # 1. Сделай итератор, который проходит по строке и возвращает только гласные буквы.
# # Пример:
# # for c in VowelIterator("hello world"):
# #     print(c)  # e o o
    
# # 2)
# class fibonacci:
#     def __init__(self, n):
#         self.n = n
#         self.current_indx = 0
#         self.prev = 0
#         self.fib = 1
#     def __iter__(self):
#         return self
#     def __next__(self):
#         if self.current_indx == 0:
#             self.current_indx += 1
#             return 0
#         if self.current_indx == 1:
#             self.fib = 1
#             self.current_indx += 1
#             return self.fib
#         if self.current_indx <= self.n:
#             temp_prev = self.prev
#             self.prev = self.fib
#             self.fib += temp_prev
#             self.current_indx +=1
#             return self.fib
#         raise StopIteration
        
# # Реализуй генератор fibonacci(n), который выдаёт первые n чисел Фибоначчи.
# # Пример:
# # print()
# # for num in fibonacci(5):
# #     print(num)  # 0 1 1 2 3

# # 3)
# class MyRange:
#     def __init__(self, start, stop, step):
#         self.start = start
#         self.stop = stop
#         self.step = step
#         self.current = 0
    
#     def __iter__(self):
#         return self
#     def __next__(self):
#         if self.current+self.step < self.stop:
#             self.current += self.step
#             return self.current
#         raise StopIteration
    
# # # Пример:
# # for i in MyRange(2, 10, 2):
# #     print(i)  # 2 4 6 8
    
# # 4)
# import itertools
# iterator = itertools.islice(range(0, 10000, 2), 10)
# for i in iterator:
#     print(i)


# # 5)
# def error_lines(file_path):
#     with open(file_path, 'r') as file:
#         for line in file:
#             if "ERROR" in line:
#                 yield line




# # 1)
# import math
# class Shape:
#     def area(self):
#         return 0
    
# class Circle:
#     def __init__(self, r):
#         self.r = r
#     def area(self):
#         return math.pi * self.r**2
# class Rectangle:
#     def __init__(self, a, b):
#         self.a = a
#         self.b = b
        
#     def area(self):
#         return self.a*self.b
# def print_areas(shapes: list):
#     for shape in shapes:
#         print(shape.area())

# # print_areas([Circle(10), Rectangle(2, 4), Rectangle(6, 5)])


# # 2)
# def even_numbers(n):
#     for i in range(n+1):
#         if i%2 == 0:
#             yield i

# # for x in even_numbers(10):
# #     print(x, end=" ")

# # 3)
# words = ["apple", "banana", "cherry"]
# k = {name: len(name) for name in words}
# # print(k)

# # 4)
# def cache(func):
#     cache_dict = {}
#     def decorator(*args):
#         cached_value = cache_dict.get(args, None)
#         if cached_value is not None:
#             return cached_value
#         res = func(*args)
#         cache_dict[args] = res
#         return res
#     return decorator

# @cache
# def add(a, b):
#     print("Computing...")
#     return a + b

# # print(add(2, 3))  # Computing... 5
# # print(add(2, 3))  # 5 (без "Computing...")

# # 5)
# class MathUtils:
#     @staticmethod
#     def is_even(n):
#         return n%2==0
    
#     @classmethod
#     def from_list(cls, numbers):
#         return ['even' if cls.is_even(num) else 'odd' for num in numbers]

# # print(MathUtils.is_even(4))   # True
# # print(MathUtils.from_list([1, 2, 3, 4]))  # ['odd', 'even', 'odd', 'even']
























# 1)

# class Animal:
#     def speak(self):
#         print('animal speaking')

# class Dog(Animal):
#     def speak(self):
#         print("Woof")
        
# class Cat(Animal):
#     def speak(self):
#         print("Meow")
        
# class Cow(Animal):
#     def speak(self):
#         print("Moo")

# def animal_sound(animals: list):
#     for animal in animals:
#         animal.speak()

# dog_1, dog_2 = Dog(), Dog()
# cat = Cat()
# cow = Cow()
# # animal_sound([dog_1, cow, cat, dog_2])

# # 2)
# def infinite_counter(start=0, step=1):
#     count = start
#     while True:
#         yield count
#         count+=step
        
# gen = infinite_counter(1, 1)
# for i in range(10):
#     next(gen)

# # 3)
# data = [("Alice", 25), ("Bob", 30), ("Charlie", 35)]
# d = {name: age for name, age in data}
# print(d)

# 4)
# import datetime
# from dateutil.relativedelta import relativedelta
# class Book(models.Model):
#     title = models.CharField(max_length=255)
#     published_at = models.DateField()
#     author = models.CharField(max_length=255)
    
#     objects = BookManager()
    
#     @property
#     def age_after_published(self):
#         year = datetime.datetime.now().year
#         return max(year - self.published_at, 0)
    
# class BookManager(models.manager):
#     def recent_books(self):
#         date = datetime.datetime.now() - relativedelta(year=5)
#         return self.filter(published_at>date)



# manager в django нужен для того, чтобы наладить связь между базой данных и моделями. Позволяет делать запросы в бд. По умолчанию один менеджер привязывается к модели при создании





# 5)

# def cache_result(func, result_k={}):
#     def wrapper(num):
#         cache = result_k.get(num, None)
#         if cache:
#             return cache
#         result = func(num)
#         result_k[num] = result
#         return result
#     return wrapper

# @cache_result
# def slow_func(x):
#     print("Computing...")
#     return x * 2

# print(slow_func(5))  # -> Computing... 10
# print(slow_func(5))  # -> 10 (без "Computing...")










# #first
# def chunks(iterable, size):
#     for i in range(0, len(iterable), size):
#         yield iterable[i:i+size]

# # print(list(chunks([1,2,3,4,5], 2)))  # -> [[1,2],[3,4],[5]]

# #second
# def append_log(msg, log=None):
#     if not log:
#         log = []
#     log.append(msg)
#     return log
# print(append_log('a', []))
# #third

# def retry(times, exceptions):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             for i in range(times):
#                 try:
#                     return func(*args, **kwargs)
#                 except Exception as e:
#                     if type(e) in exceptions:
#                         continue
#                     else:
#                         raise e
#         return wrapper
#     return decorator
            

# @retry(times=3, exceptions=(ValueError,))
# def test():
#     print(1)
#     raise ValueError
    
# # test()

# #fourth
# def flatten(*args):
#     for arg in args:
#         if isinstance(arg, list):
#             yield from flatten(*arg)
#         else:
#             yield arg

# # print(list(flatten([1,[2,[3,4],5], "ab", b"cd"])))  # -> [1,2,3,4,5,"ab", b"cd"]

# #fifth
# class User:
#     def __init__(self, name: str, age: int):
#         self._validate(name, age)
#         self.name = name
#         self.age = age
        
#     @staticmethod 
#     def _validate(name, age):
#         if name in ('', ' ') or not name or age < 0:
#             raise ValueError
        
#     @classmethod 
#     def from_dict(cls, data: dict):
#         name, age = data.get('name', ''), data.get('age', -1)
#         cls._validate(name, age)
#         return cls(name, age)
        
# u1 = User.from_dict({'name': 'ghwera', 'age': 2})
# # print(u1.__dict__)

# #sixth
# import re
# def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
#     d = {}
#     for word in text.split():
#         w_formatted = re.sub(r'[^a-zA-Z0-9]', '', word)
#         d[w_formatted] = d.get(w_formatted, 0) + 1
#     final_list = [(w, c) for w, c in d.items()]
#     final_list.sort(key=lambda tup: (-tup[1], tup[0].lower()))

# top_k_words("To be, or not to be!", 2)  # -> [("be",2), ("not",1)]

# #seventh
# class Command():
#     _registry = {}
    
#     @classmethod
#     def create(cls, name: str, **kwargs):
#         cls_obj = cls._registry.get(name, None)
#         if cls_obj:
#             return cls_obj(**kwargs)
        
#     @classmethod
#     def register(cls, name):
#         def decorator(subclass):
#             cls._registry[name] = subclass
#             return subclass
#         return decorator


# # Пример:
# @Command.register("echo")
# class Echo(Command):
#     def __init__(self, text): self.text = text
#     def run(self): return self.text

# cmd = Command.create("echo", text="hi")
# print(cmd.run())  # -> "hi"