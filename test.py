from random import choice as random_choice
from typing import Tuple
from random import uniform as random_uniform


common_mult = 1.2
uncommon_mult = 7.6
rare_mult = 19.8
epic_mult = 917
legendary_mult = 3846

base_mult = 0.01
# 0.1 1000 hours
# 0.01 100 hours
# 0.01 100 hours
# 0.001 10 hours increasing ~x3 the chance
# 0.0005 5 hours
# 0.0001 1 hour
pool_size_increase = 50*(base_mult*500) # +50 for 20 hours
pool_size = min(int(50 + pool_size_increase), 850) # stop on 160th hour
 
RARITY_WEIGHTS = {
    'обычный': 1+(common_mult*0.1*base_mult),
    'необычный': 1+(uncommon_mult*0.2*base_mult),
    'редкий': 1+(rare_mult*0.4*base_mult),
    'эпический': 1+(epic_mult*1.2*base_mult),
    'легендарный': 1+(legendary_mult*1.8*base_mult),
}


def get_weighted_name(pool_size=50):
    """Генерирует пул ников, выбирает один с учётом редкости и веса."""
    name_pool = []

    for _ in range(pool_size):
        nickname = get_random_name()
        rarity = check_rarity(nickname)
        weight = RARITY_WEIGHTS.get(rarity, 1)
        name_pool.append((nickname, rarity, weight))

    total_weight = sum(w for _, _, w in name_pool)
    rnd = random_uniform(0, total_weight)
    upto = 0
    for name, rarity, weight in name_pool:
        if upto + weight >= rnd:
            return name, rarity
        upto += weight

    return name_pool[-1][:2]  # fallback


count = {}
def start():
    for i in range(10000):
        nickname, rarity = change_nickname()
        count[rarity] = count.get(rarity, 0) + 1




def change_nickname():
    nickname, rarity = get_weighted_name(pool_size=pool_size)
    
    return nickname, rarity




def get_random_name():
    return random_choice(RU_FIRST_NAMES) + ' ' + random_choice(RU_LAST_NAMES)






def split_name(full_name: str) -> Tuple[str, str]:
    """Разделяет полное имя на имя и фамилию."""
    parts = full_name.split()
    return (parts[0], parts[1]) if len(parts) == 2 else ("", "")

def is_legendary(full_name: str) -> bool:
    """Проверяет, является ли имя легендарным (в списке)."""
    return full_name in RU_LEGENDARY_NAMES

def is_epic(full_name: str) -> bool:
    """Проверяет, является ли имя эпическим (сравнение последних букв)."""
    """Эпическое, если последние 3 буквы имени и фамилии совпадают."""
    first_name, second_name = split_name(full_name)

    if not first_name or not second_name:
        return False

    # Проверяем условия
    if len(first_name) < 3 or len(second_name) < 3 or abs(len(first_name) - len(second_name)) > 3:
        return False
    first_sub = first_name[-3:]
    second_sub = second_name[-3:]
    return first_sub == second_sub

def is_rare(full_name: str) -> bool:
    """Проверяет, является ли имя редким (первая буква совпадает)."""
    first_name, second_name = split_name(full_name)
    return first_name and second_name and first_name[0].lower() == second_name[0].lower()

def is_uncommon(full_name: str) -> bool:
    """Проверяет, является ли имя необычным (длина имени = длине фамилии)."""
    first_name, second_name = split_name(full_name)
    return first_name and second_name and len(first_name) == len(second_name)


def check_rarity(full_name):
    if is_legendary(full_name):
        return ROLES[4]
    elif is_epic(full_name):
        return ROLES[3]
    elif is_rare(full_name):
        return ROLES[2]
    elif is_uncommon(full_name):
        return ROLES[1]
    return ROLES[0]
















ROLES = ['обычный', 'необычный', 'редкий', 'эпический', 'легендарный', 'анти-легендарный']


""" NAMES CONSTANTS """
RU_FIRST_NAMES = [
    'Христофор', 'Илья', 'Сеня', 'Жека', 'Тоха',
    'Олег', 'Константин', 'Андрей', 'Артём', 'Никита',
    'Игорь', 'Витёк', 'Гога', 'Савелий', 'Вова', 'Ярик',
    'Всеволод', 'Митяй', 'Вениамин', 'Алексей', 'Яша',
    'Данила', 'Лёва', 'Саша', 'Саня', 'Женя',
    'Костян', 'Аристарх', 'Альвиан', 'Артур',
    'Спиридон', 'Пахомий', 'Мэн', 'Жора',
    'Павлик', 'Захар', 'Самуил', 'Армен', 'Петя',
    'Миша', 'Владик', 'Денчик', 'Юра', 'Жан', 'Сэм',
    'Клим', 'Серый', 'Радик', 'Трофим',
    'Таир', 'Кабан', 'Тимурка', 'Юрик', 'Даня', 'Бока',
    'Панфутий', 'Арчи', 'Герчик', 'Сава', 'Багратион',
    'Гагик', 'Виктор', 'Иммануил', 'Попка', 'Иннокентий',
    'Дима', 'Гена', 'Жак', 'Прокопий', 'Серега', 'Илюша',
    'Сергей', 'Женька', 'Анатолий', 'Олежа', 'Олежка',
    'Костик', 'Костечка', 'Андрюша', 'Андрейка',
    'Артёмка', 'Никитос', 'Владислав', 'Михаил', 'Митюша', 'Веник',
    'Сашка', 'Яшка', 'Артурка', 'Пахомка', 'Павлуша',
    'Петруша', 'Юрка', 'Гера', 'Кеша', 'Димон', 'Ростик',
    'Ростислав', 'Паисий', 'Шурик', 'Руся', 'Моня', 'Боба',
    'Гит', 'Кирилл', 'Микола', 'Джек', 'Педро', 'Эдуардо',
    'Майк', 'Абрахам', 'Яромир', 'Святогор', 'Арсен', 'Филипп',
    'Радмир', 'Ринат', 'Рамиль', 'Тихон', 'Самир', 'Ильдар',
    'Марсель', 'Роберт', 'Айдар', 'Тамерлан', 'Альберт',
    'Влад', 'Игнат', 'Рустам', 'Ян', 'Назар', 'Эмиль',
    'Артемий', 'Гордей', 'Мирослав', 'Даниэль', 'Герман', 'Марат',
    'Фёдор', 'Демид', 'Мирон', 'Елисей', 'Лев', 'Макар', 'Марк',
    'Тимофей', 'Егор', 'Миха', 'Русик', 'Руслан', 'Пётр',
    'Жося', 'Жостик', 'Валёк', 'Гоги', 'Кэл', 'Афанасий',
    'Вадик', 'Вадим', 'Павел', 'Эдик', 'Эдя', 'Эдуард',
    'Феоктист', 'Киса', 'Иржан', 'Генка', 'Святополк', 'Дамир',
    'Дамирка', 'Яков', 'Рома', 'Роман', 'Ромка',
    'Витян', 'Кирюха', 'Кирюша', 'Изя', 'Изечка', 'Родион',
    'Родечка', 'Дроп', 'Дед', 'Дрон', 'Юрец', 'Илюха', 'Карлуша', 'Коля',
    'Костыль', 'Гарри', 'Ким', 'Эврар', 'Эрнест', 'Жерар', 'Люпен', 'Рикардо',
    'Эльфанзо', 'Прохор', 'Больжедор', 'Равшан', 'Рафик', 'Иван', 'Ваня', 'Ивасик',
    'Рафаэль'
]
RU_LAST_NAMES = [
    'Работник', 'Программист', 'Тридемакс', 'Дотер',
    'Тиктокер', 'Ястреб', 'Ненаркоторговец', 'Очко',
    'Петух', 'Шиза', 'Пошлый', 'Заднеприводной', 'Заводской',
    'Вертухай', 'Анимешник', 'Кабанчик', 'Вист', 'Охрана',
    'Кальяньщик', 'Хирург', 'Дюбель', 'Всемогущий',
    'Аристократ', 'Дихлофос', 'Коптёр', 'Чужой', 'Мальчик',
    'Хук', 'Секретарь', 'Шницель', 'Овощебаза', 'Потец',
    'Монгол', 'Иуда', 'Ипотека', 'Бугор', 'Жока',
    'Тамада', 'Пекуш', 'Робин', 'Торч', 'РХБЗ', 'Хрюк',
    'Робокоп', 'Репа', 'Тесак', 'Плесень', 'РЖД', 'Слесарь',
    'Верховный', 'Ноль', 'Грибник', 'Бородач', 'Барыга',
    'Шприц', 'Арбидол', 'Суходрищев', 'Сиплый', 'Гаджет',
    'Шульц', 'Кацман', 'Япончик', 'Сотона', 'Корч', 'Примус',
    'Кардан', 'Приличный', 'Сбалансированный', 'Приемлемый',
    'Умный', 'Красивый', 'Урод', 'Мужчина', 'Газобетон',
    'Сова', 'Касперидзе', 'Жмых', 'Жислый', 'Кислый',
    'Конченный', 'Свинец', 'Секач', 'Хипстер', 'Небоскрёб',
    'Мякиш', 'Тыкволобик', 'Дебилоид', 'Ландер',
    'Косипоша', 'Александровский', 'Пахан', 'Маргинал',
    'Унтерменш', 'Злой', 'Чифир', 'Фуфел', 'Барбарис',
    'Чирик', 'Воробей', 'Настоечка', 'Батя', 'Парамедик',
    'Змей', 'Спецназ', 'Добрый', 'Бомж', 'Нищета', 'Саныч',
    'Знаменосец', 'Керосинка', 'Вымпел', 'Межрайгаз',
    'Газонокосилка', 'ДВС', 'Полкан', 'Хороший', 'Нищуган',
    'Выходной', 'Зуко', 'Дирол', 'Сыч', 'Терминатор',
    'Пуш', 'Люканг', 'Шамбамбулиш', 'Демидрол', 'Навтизин',
    'Метан', 'Пиджак', 'Кукиш', 'Биб', 'Цыкса', 'Элипод',
    'Тварь', 'Падла', 'Гироскоп', 'Инфаркт', 'Дефибриллятор', 'Инсульт',
    'Кудрявый', 'Бибурат', 'Раб', 'Жирогон', 'Прораб', 'Фострал',
    'Мехос', 'Пупок', 'Могикан', 'Коновал', 'Монк', 'Ветролёт',
    'Штиль', 'Липкий', 'Палец', 'Стручок', 'Гиря', 'Обурец', 'Пипетка',
    'Токсик', 'Фитиль', 'Инфернал', 'Кладмэн', 'Глоркс', 'Некросс',
    'Икспло', 'Табутаск', 'Монолит', 'Комиссар', 'Махотин', 'Софти',
    'Криспо', 'Бздиловатый', 'Кирпич', 'Люся', 'Махно', 'Сизый',
    'Лютый', 'Майор', 'Сырок', 'Пикантный', 'Воркута', 'Гастролёр',
    'Дядя', 'Трудовик', 'Тренер', 'Пентиум', 'Флюс', 'Всола',
    'Жирный', 'Сметана', 'Братан', 'Глыба', 'Пупсень', 'Вупсень',
    'Алюминий', 'Везунчик', 'Снайлер', 'Потный', 'Таксист', 'Косой',
    'Деревня', 'Госдеп', 'Панк', 'Капелька', 'Отбитый', 'Грузин',
    'Пикатиний', 'Пукич', 'Электрод', 'Горчишник', 'Синтол',
    'Джентельмен', 'Сырный', 'Припой', 'Понч', 'Косяк', 'Сдобный',
    'Копирайтер', 'Прыщь', 'Харон', 'Жиган', 'Меченый', 'Глазастый',
    'Слякоть', 'Беленький', 'Слоупок', 'Лапа', 'Правильный', 'Жиробас',
    'Опасный', 'Лещ', 'Рыло', 'Шниппель', 'Мятый', 'Туловище',
    'Генотип', 'Насвай', 'Инстаграмщик', 'Сишарп', 'Плюха', 'Лепёха',
    'Лялечка', 'Директор', 'Копченый', 'Бобик', 'Особенный',
    'Ограниченный', 'Мероприятие', 'Полторашка', 'Спартак', 'Верстак',
    'Кот', 'Трансформатор', 'Пичот', 'Саратовский', 'Контрольный', 'Зеон', 'Автокад',
    'Жилистый', 'Фантазер', 'Баскервилей', 'Кухонный', 'Жирик', 'Пожилой',
    'Комнатный', 'Юбилейный', 'Коммит', 'Годовасик', 'Нехорошилов', 'Мороз',
    'Душный', 'Почетный', 'Романов', 'Сутенер', 'Суслик', 'Скворец', 'Жмурик',
    'Бстр', 'Панини', 'Винторез', 'Кожан', 'Добренький', 'Червяк', 'Сельдерей',
    'Сливочный', 'Кицураги', 'Дюбуа', 'Курага', 'Ряженка', 'Поджатый', 'Сталевар',
    'Сапёр', 'Автомеханик', 'Сантехник', 'Греча', 'Чернослив', 'Сгущенка',
    'Изюм', 'Сухарь', 'Важный', 'Бумажный', 'Ибупрофен', 'Пёс', 'Шарик',
    'Калека', 'Воротник', 'Стелька', 'Медный', 'Монитор', 'Пузо', 'Праздник',
    'Рябой', 'Культяпка', 'Блохастый', 'Убийца', 'Подсолнух', 'Гибкий',
    'Выдра', 'Половник', 'Сквозняк', 'Прохвост', 'Кутила', 'Разгильдяй',
    'Космонавт', 'Гуччи', 'Флекс', 'Примат', 'Вавилон', 'Римский',
    'Моцарелла', 'Крайний', 'Промах', 'Открывашка', 'Мясорубка', 'Лаврушка',
    'Победитель', 'Форсунка', 'Конвейер', 'Вырубатель', 'Мертвечина', 'Бездуховный',
    'Прах', 'Бальзам', 'Новороссийский', 'Солнечный', 'Епифанцев', 'Горшков', 'Клей',
    'Бабурехов', 'Вторник', 'Шляпкин', 'Пупкин', 'Жук', 'Грешник', 'Жадина',
    'Текила', 'Танго', 'Костромской', 'Живодёр', 'Садист', 'Мазохист', 'Нудист',
    'Дупло', 'Сырник', 'Прадо', 'Суприм', 'Бог', 'Бессмертный', 'Вездесущий', 'Атлет',
    'Котлета', 'Сосиска', 'Желчный', 'Гадина', 'Жиробоков', 'Кожемяка', 'Хрящ',
    'Костолом', 'Пушка', 'Сталкер', 'Невыносимый', 'Наполеон', 'Правдивый', 'Лжец',
    'Рассвет', 'Закат', 'Дискотека', 'Газовщик', 'Репортёр', 'Гнилоуст',
    'Сэнсэй', 'Гайдзин', 'Авторитет', 'Мясоедов', 'Эденбург', 'Тугохрякин',
    'Узумакин', 'Жепепе', 'Киста', 'Художник', 'Клоун', 'Амфибия', 'Дзен', 'Нирвана',
    'Монах', 'Стритрэйсер', 'Тугодумов', 'Шутняра', 'Забубенский',
    'Комбайн', 'Низкокалорийный', 'Чайка', 'Каратель', 'Ломакин',
    'Жатва', 'Протокол', 'Гомункул', 'Волгин', 'Каблук', 'Сливовый',
    'Вор', 'Пентагон', 'Агент', 'Цирюльник', 'Парикмахер',
    'Шевелюра', 'Гренадёр', 'Жокей', 'Диджей', 'Солянкин', 'Пышка',
    'Какаду', 'Пират', 'Удовольствие', 'Пехотинец', 'Танкист', 'Летчик',
    'Мухоловкин', 'Славянин', 'Печкин', 'Телогрейкин', 'Жаба', 'Кринж',
    'Лебёдкин', 'Сюрстрёмминг', 'Агутин', 'Кекс', 'Шпекс', 'Сервелат',
    'Либидо', 'Эстроген', 'Пивас', 'Солод', 'Хмельной', 'Алкоголик',
    'Глянец', 'Запор', 'Жбан', 'Крузенштерн', 'Тротил', 'Квакша',
    'Артист', 'Сапожок', 'Амёба', 'Паразит', 'Животик', 'Щетина',
    'Репетитор', 'Глист', 'Иммунитет', 'Быстров', 'Политрук',
    'Кремлёвчик', 'Чертыла', 'Денди', 'Заряженый', 'Масло',
    'Дешёвка', 'Узелков', 'Хмельницкий', 'Легион', 'Летун',
    'Поплавок', 'Загон', 'Натянутый', 'Прикорм', 'Наживка',
    'Кочегар', 'Жандарм', 'Кляп', 'Разработанный',
    'Чубайс', 'Жидкий', 'Мантикора', 'Пингвин', 'Ктулху',
    'Уточка', 'Женьшень', 'Фронтендер', 'Бабайка',
    'Аналитик', 'Уругвай', 'Вилка', 'Хрюндель', 'Пятак',
    'Кэп', 'Дабстеп', 'Танцор', 'Горшок', 'Кукушечка',
    'Слобода', 'Тамбов', 'Бишкек', 'Никельбек', 'Амогус',
    'Закваска', 'Пивасик', 'Яичко', 'Дракула', 'Кровосос', 'Пивосос',
    'Пивозавр', 'Творожок', 'Амброзиус-Кусто', 'Сансет', 'Баранкин',
    'Бублик', 'Дырокол', 'Шерман', 'Черчилль', 'Разнобой', 'Среда', 'Клапан',
    'Миротворец', 'Блейм', 'Курдюк', 'Кумыс', 'Корнишон', 'Хорни', 'Корень',
    'Пицца', 'Паста', 'Бивень', 'Жижень', 'Лярва',
    'Бафомет', 'Импортный', 'Берец', 'Друган', 'Пирожок',
    'Кексик', 'Овсянка', 'Ноздря', 'Морзе', 'Хорошилов',
    'Абапер', 'Сатанист', 'Культист', 'Снюс', 'Копатыч',
    'Табуретка', 'Шишка', 'Портянка', 'Подошва', 'Носок',
    'Аквалангист', 'Биба', 'Боба', 'Поридж', 'База', 'Импортозамещенный',
    'Подгузник', 'Грудничок', 'Тыква', 'Бульба', 'Ябеда',
    'Лягушка', 'Попрыгун', 'Гренка', 'Орешкин', 'Отаку',
    'Фраер', 'Апельсин', 'Фрукт', 'Революционер', 'Блатной',
    'Мужик', 'Козел', 'Шестёрка', 'Шнырь', 'Фуфлыжник',
    'Якудза', 'Император', 'Сёгун', 'Самурай', 'Сеппуку',
    'Ниндзя', 'Вайб', 'Щенок', 'Стелс', 'Бомбардировщик',
    'Газ', 'Вонь', 'Запашок', 'Эрудит', 'Балаболкин'
]
RU_LEGENDARY_NAMES = [
    'Олег Пошлый', 'Вова Вист', 'Илья Торч', 'Джек Воробей', 'Бока Жока',
    'Илья Кальяньщик', 'Илья Заводской', 'Андрей Выходной', 'Илья Косипоша',
    'Артёмка Жмых', 'Костян Тыкволобик', 'Гит Пуш', 'Кабан Кабанчик',
    'Никита Инфаркт', 'Илюша Инфаркт', 'Олежа Кудрявый', 'Олег Барбарис',
    'Артёмка Всола', 'Илюха Плюха', 'Гит Монолит', 'Илья Зеон', 'Илья Автокад',
    'Андрей Жилистый', 'Андрей Анимешник', 'Никита Баскервилей', 'Никита Кухонный',
    'Никита Суходрищев', 'Олежа Жирик', 'Дед Мороз', 'Иван Кожан',
    'Леха Лепёха', 'Жан Кожан', 'Клим Саныч', 'Серега Пират', 'Анатолий Чубайс', 'Никита Бишкек',
    'Жак Пиджак'
]
EN_FIRST_NAMES = [
    'Christopher', 'Ilya', 'Senya', 'Zheka', 'Toha',
    'Oleg', 'Konstantin', 'Andrei', 'Artyom', 'Nikita',
    'Igor', 'Vityok', 'Goga', 'Savely', 'Vova', 'Yarik',
    'Vsevolod', 'Mityai', 'Veniamin', 'Alexey', 'Yasha',
    'Danila', 'Lyova', 'Sasha', 'Sanya', 'Zhenya',
    'Kostyan', 'Aristarkh', 'Alvian', 'Artur',
    'Spiridon', 'Pachomius', 'Man', 'Zhora',
    'Pavlik', 'Zakhar', 'Samuel', 'Armen', 'Petya',
    'Misha', 'Vladik', 'Denchik', 'Yura', 'Jean', 'Sam',
    'Klim', 'Gray', 'Radik', 'Trofim',
    'Tair', 'Kaban', 'Timurka', 'Yurik', 'Danya', 'Boka',
    'Panfutius', 'Archie', 'Gerchik', 'Sava', 'Bagration',
    'Gagik', 'Victor', 'Immanuel', 'Popka', 'Innokentius',
    'Dima', 'Gena', 'Jacques', 'Procopius', 'Serega', 'Ilyusha',
    'Sergei', 'Zhenka', 'Anatoly', 'Oleg', 'Olezhka',
    'Kostik', 'Kostechka', 'Andriusha', 'Andreika',
    'Artyomka', 'Nikitos', 'Vladislav', 'Mikhail', 'Mityusha', 'Venyk',
    'Sashka', 'Yashka', 'Arturka', 'Pakhomka', 'Pavlusha',
    'Petrusha', 'Yurka', 'Gera', 'Kesha', 'Dimon', 'Rostik',
    'Rostislav', 'Paisii', 'Shurik', 'Rusya', 'Monya', 'Boba',
    'Git', 'Kirill', 'Mikola', 'Jack', 'Pedro', 'Eduardo',
    'Mike', 'Abraham', 'Jaromir', 'Svyatogor', 'Arsen', 'Philip',
    'Radmir', 'Rinat', 'Ramil', 'Tikhon', 'Samir', 'Ildar',
    'Marcel', 'Robert', 'Aidar', 'Tamerlan', 'Albert',
    'Vlad', 'Ignat', 'Rustam', 'Jan', 'Nazar', 'Emil',
    'Artemy', 'Gordej', 'Miroslav', 'Daniel', 'Herman', 'Marat',
    'Fedor', 'Demid', 'Miron', 'Eliseus', 'Lev', 'Makar', 'Mark',
    'Timothy', 'Yegor', 'Mikha', 'Rusik', 'Ruslan', 'Peter',
    'Zhosya', 'Zhostik', 'Valyok', 'Gogi', 'Cal', 'Afanasy',
    'Vadik', 'Vadim', 'Pavel', 'Edik', 'Edya', 'Edward',
    'Feoktist', 'Kisa', 'Irzhan', 'Genka', 'Svyatopolk', 'Damir',
    'Damirka', 'Jacob', 'Roma', 'Roman', 'Romka',
    'Vityan', 'Kiryukha', 'Kiryusha', 'Izya', 'Izechka', 'Rodion',
    'Rodechka', 'Drop', 'Ded', 'Dron', 'Yurets', 'Ilyukha', 'Karlusha', 'Kolya',
    'Crutch', 'Harry', 'Kim', 'Evrare', 'Ernest', 'Gerard', 'Lupin', 'Ricardo',
    'Elfanzo', 'Prokhor', 'Boljedor', 'Ravshan', 'Rafik', 'Ivan', 'Vanya', 'Ivasik',
    'Rafael'
]
EN_LAST_NAMES = [
    'Worker', 'Programmer', 'Tridemax', 'Doter',
    'Ticktocker', 'Hawk', 'Non-Drug Dealer', 'Point',
    'Cock', 'Sheezy', 'Naughty', 'Backstabber', 'Factory',
    'Chink', 'Anime Man', 'Boar', 'Whist', 'Guard',
    'Hooker', 'Surgeon', 'Dubel', 'Almighty',
    'Aristocrat', 'Dichlophos', 'Copter', 'Alien', 'Boy',
    'Hook', 'Secretary', 'Schnitzel', 'Vegetable Farm', 'Sweatshop',
    'Mongol', 'Judas', 'Mortgage', 'Bugor', 'Jock',
    'Toastmaster', 'Pecush', 'Robin', 'Torch', 'RHBZ', 'Grunt',
    'Robocop', 'Turnip', 'Corkscrew', 'Mildew', 'RZD', 'Locksmith',
    'Supreme', 'Zero', 'Mushroom Man', 'Beardface', 'Barber',
    'Spritz', 'Arbidol', 'Sukhodrishchev', 'Sipy', 'Gadget',
    'Shultz', 'Katsman', 'Japon', 'Sotona', 'Korch', 'Primus',
    'Cardan', 'Decent', 'Balanced', 'Acceptable',
    'Smart', 'Handsome', 'Freak', 'Man', 'Gascon',
    'Owl', 'Kasperidze', 'Cheeky', 'Sour', 'Sour',
    'Konned', 'Lead', 'Sekach', 'Hipster', 'Skyscraper',
    'Meatball', 'Pumpkinhead', 'Debiloid', 'Lander',
    'Kosiposha', 'Alexandrovsky', 'Pahan', 'Marginal',
    'Untermensch', 'Wicked', 'Chifir', 'Fufel', 'Barbaris',
    'Chirik', 'Sparrow', 'Nastoychka', 'Batya', 'Paramedic',
    'Snake', 'Spetsnaz', 'Kind', 'Bum', 'Pauper', 'Sanych',
    'Bannerbearer', 'Kerosinka', 'Vympel', 'Mezhraygaz',
    'Lawnmower', 'DVS', 'Polkan', 'Good', 'Nishchugan',
    'Weekend', 'Zuko', 'Dirol', 'Sych', 'Terminator',
    'Push', 'Lucang', 'Shambambulish', 'Demidrol', 'Navtizin',
    'Methane', 'Jacket', 'Kukish', 'Bib', 'Zyxa', 'Elipod',
    'Creature', 'Padla', 'Gyroscope', 'Infarction', 'Defibrillator', 'Stroke',
    'Curly', 'Biburat', 'Slave', 'Girogon', 'Foreman', 'Fostral',
    'Mechos', 'Navel', 'Mohican', 'Konoval', 'Monk', 'Windjammer',
    'Stil', 'Sticky', 'Finger', 'Weight', 'Auburn', 'Pipette',
    'Toxic', 'Wick', 'Infernal', 'Cladman', 'Glorx', 'Necross',
    'Xplo', 'Tabutask', 'Monolith', 'Commissar', 'Mahotin', 'Softy',
    'Crispo', 'Bzdilovaty', 'Brick', 'Lucia', 'Makhno', 'Sizy',
    'Livid', 'Major', 'Cheese', 'Spicy', 'Vorkuta', 'Gastroller',
    'Uncle', 'Trudovik', 'Coach', 'Pentium', 'Flux', 'Wsola',
    'Fatty', 'Smeana', 'Bratan', 'Lump', 'Poopsy', 'Woopsy',
    'Aluminum', 'Lucky', 'Snapper', 'Sweaty', 'Taxi Driver', 'Squint',
    'The Village', 'Gosdep', 'Punk', 'The Dropper', 'The Chopper', 'The Georgian',
    'Picatinium', 'Pukich', 'Electrode', 'Gorchishnik', 'Sintol',
    'Gentleman', 'Cheesy', 'Solder', 'Ponch', 'Koksiak', 'Sodny',
    'Copywriter', 'Pimple', 'Charon', 'Ziggy', 'Swordy', 'Eyeball',
    'Slushy', 'Whitey', 'Sloppy', 'Paw', 'Righty', 'Fatso',
    'Dangerous', 'Lech', 'Snout', 'Schnippy', 'Crumpled', 'Torso',
    'Genotype', 'Nasvay', 'Instagrammer', 'Sisharp', 'Spit', 'Leppy',
    'Lyalychka', 'Director', 'Smokey', 'Bobik', 'Special',
    'Restricted', 'Event', 'Half and Half', 'Spartacus', 'Workbench',
    'Cat', 'Transformer', 'Peachot', 'Saratov', 'Control', 'Zeon', 'Autocad',
    'Fatty', 'Fancier', 'Baskerville', 'Kitchen', 'Girik', 'Aged',
    'Roomy', 'Jubilee', 'Commit', 'Yearling', 'Nekhoroshilov', 'Frosty',
    'Smother', 'Honorable', 'Romanov', 'Pimp', 'Gopher', 'Starling', 'Grasshopper',
    'Bstr', 'Panini', 'Vintorez', 'Leatherman', 'Goodyear', 'Worm', 'Celery',
    'Creamy', 'Kitsuragi', 'Dubois', 'Rooster', 'Ryazhenka', 'Podzhatny', 'Steeler',
    'Sapper', 'Car Mechanic', 'Plumber', 'Buckwheat', 'Prune', 'Condensed milk',
    'Raisin', 'Sugar', 'Important', 'Paper', 'Ibuprofen', 'Dog', 'Balloon',
    'Cripple', 'Collar', 'Insole', 'Copper', 'Monitor', 'Belly', 'Holiday',
    'Rugged', 'Stumpy', 'Flea', 'Killer', 'Sunflower', 'Flexible',
    'Otter', 'Pothead', 'Skivvoznik', 'Slacker', 'Kutila', 'Rascal',
    'Cosmonaut', 'Gucci', 'Flex', 'Primate', 'Babylon', 'Roman',
    'Mozzarella', 'Extreme', 'Missed', 'Opener', 'Meatgrinder', 'Lavrushka',
    'Winner', 'Injector', 'Conveyor', 'Chopper', 'Deadbeat', 'Spiritless',
    'Ashes', 'Balsam', 'Novorossiysky', 'Sunny', 'Epifantsev', 'Gorshkov', 'Glue',
    'Baburekhov', 'Tuesday', 'Shlyapkin', 'Pupkin', 'Zhuk', 'Sinner', 'Greedy',
    'Tequila', 'Tango', 'Kostroma', 'Viper', 'Sadist', 'Masochist', 'Nudist',
    'Duplo', 'Cheese Man', 'Prado', 'Supremus', 'God', 'Immortal', 'Omnipresent', 'Athlete',
    'Cutlet', 'Sausage', 'Bile', 'Gadina', 'Girobokov', 'Kozhemyaka', 'Cartilage',
    'Kostolom', 'Cannon', 'Stalker', 'Insufferable', 'Napoleon', 'Truthful', 'Liar',
    'Dawn', 'Sunset', 'Disco', 'Gasman', 'Reporter', 'Rotter',
    'Sensei', 'Gaidzin', 'Authoritet', 'Meathead', 'Edenburg', 'Tugohryakin',
    'Uzumakin', 'Jepepe', 'Kista', 'Artist', 'Clown', 'Amphibian', 'Zen', 'Nirvana',
    'Monk', 'Streaker', 'Tugodumov', 'Shutnyara', 'Zabubensky',
    'Harvester', 'Low-Calorie', 'Seagull', 'Karatel', 'Lomakin',
    'Harvest', 'Protocol', 'Homunculus', 'Volgin', 'Heel', 'Plum',
    'Thief', 'Pentagon', 'Agent', 'Barber',
    'Hair', 'Grenadier', 'Jockey', 'DJ', 'Salty', 'Chick',
    'Kakadu', 'Pirate', 'Pleasure', 'Infantryman', 'Tankman', 'Aviator',
    'Flycatcher', 'Slav', 'Pechkin', 'Telogreekin', 'Toad', 'Kringe',
    'Lebedkin', 'Surströmming', 'Agutin', 'Keks', 'Speks', 'Servelat',
    'Libido', 'Estrogen', 'Beer', 'Malt', 'Hop', 'Alcoholic',
    'Glossy', 'Zapor', 'Frog', 'Krusenstern', 'Trothil', 'Quack',
    'Artist', 'Slipper', 'Amoeba', 'Parasite', 'Animal', 'Bristle',
    'Tutor', 'Worm', 'Immunity', 'Bystrov', 'Polytruk',
    'Kremlovchik', 'Chertyla', 'Dandy', 'Charged', 'Butter',
    'Deshevka', 'Uzelkov', 'Khmelnitsky', 'Legion', 'Letun',
    'Float', 'Enclosure', 'Strung', 'Feed', 'Bait',
    'Barber', 'Gendarme', 'Gag', 'Developed',
    'Chubais', 'Liquid', 'Manticore', 'Penguin', 'Cthulhu',
    'Duck', 'Ginseng', 'Frontender', 'Babaika',
    'Analyst', 'Uruguay', 'Fork', 'Grundel', 'Fiver',
    'Cap', 'Dabstep', 'Dancer', 'Pot', 'Cuckoo',
    'Sloboda', 'Tambov', 'Bishkek', 'Nickelbeck', 'Amogus',
    'Zakvaska', 'Pivasik', 'Yaichko', 'Dracula', 'Bloodsucker', 'Beersucker',
    'Beerosaurus', 'Whey', 'Ambrosius-Cousto', 'Sunset', 'Barankin',
    'Bagel', 'Hooker', 'Sherman', 'Churchill', 'Variety', 'Medium', 'Valve',
    'Peacemaker', 'Blame', 'Kurdyuk', 'Kumys', 'Cornish', 'Horney', 'Root',
    'Pizza', 'Pasta', 'Beef', 'Zhizhen', 'Ljarva',
    'Baphomet', 'Imported', 'Berez', 'Drugan', 'Piezhok',
    'Cupcake', 'Oatmeal', 'Nostril', 'Morse', 'Khoroshilov',
    'Abaper', 'Satanist', 'Cultist', 'Snus', 'Kopatych',
    'Stool', 'Shishka', 'Slipper', 'Sole', 'Sock',
    'Aqualangist', 'Biba', 'Boba', 'Porridge', 'Base', 'Imported',
    'Diaper', 'Toddler', 'Pumpkin', 'Bulba', 'Jabeda',
    'Frog', 'Poppy', 'Pretzel', 'Walnut', 'Otaku',
    'Fraer', 'Orange', 'Fruit', 'Revolutionary', 'Blatnoy',
    'Man', 'Goat', 'Six', 'Snitch', 'Fake',
    'Yakuza', 'Emperor', 'Shogun', 'Samurai', 'Seppuku',
    'Ninja', 'Wibe', 'Puppy', 'Stealth', 'Bomber',
    'Gas', 'Stink', 'Smell', 'Erudite', 'Balabolkin'
]
EN_LEGENDARY_NAMES = [
    'Oleg Poshly', 'Vova Vist', 'Ilya Torch', 'Jack Sparrow', 'Boca Jocka',
    'Ilya Kalyanshchik', 'Ilya Zavodskoy', 'Andrew Weekend', 'Ilya Kosiposha',
    'Artyomka Zhykh', 'Kostyan Pumpkin', 'Git Push', 'Kabanchik the Boar',
    'Nikita Infarct', 'Ilyusha Infarct', 'Oleg Curly', 'Oleg Barbaris',
    'Artyomka Vsola', 'Ilyukha Plukha', 'Git Monolith', 'Ilya Zeon', 'Ilya Autocad',
    'Andrei Zhilisty', 'Andrei Animeshnik', 'Nikita Baskerville', 'Nikita Kukhnyy',
    'Nikita Sukhodrischev', 'Oleza Zhirik', 'Ded Moroz', 'Ivan Kozhan',
    'Lekha Lepekha', 'Zhan Kozhan', 'Klim Sanych', 'Seryoga Pirat', 'Anatoly Chubais', 'Nikita Bishkek',
    'Jacques Jacket'
]







# start()









l = "['Работник', 'Программист', 'Тридемакс', 'Дотер', 'Тиктокер', 'Ястреб', 'Ненаркоторговец', 'Очко']"
print(l.replace("'", "").replace("[", "").replace("]", "").replace(",", ""))