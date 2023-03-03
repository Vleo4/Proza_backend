from articles.custom_exceptions import CensorError
import re


def levenshtein_distance(s, t):
    m, n = len(s), len(t)
    d = [[0] * (n + 1) for i in range(m + 1)]

    for i in range(m + 1):
        d[i][0] = i
    for j in range(n + 1):
        d[0][j] = j

    for j in range(1, n + 1):
        for i in range(1, m + 1):
            if s[i - 1] == t[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                d[i][j] = min(d[i - 1][j], d[i][j - 1], d[i - 1][j - 1]) + 1

    return d[m][n]


def check_similarity(text1, text2):
    distance = levenshtein_distance(text1, text2)
    similarity = 1 - distance / max(len(text1), len(text2))
    return similarity


def preprocess_text(text, stop_words):
    word_tokens = re.sub("[^\w]", " ", text).lower().split()
    filtered_text = [word for word in word_tokens if word not in stop_words]
    return ' '.join(filtered_text)


def anti_plagiarism(new_poem, database):
    threshold = 0.8
    new_poem = preprocess_text(new_poem, ukrainian_stop_words)
    database = [preprocess_text(poem, ukrainian_stop_words) for poem in database]

    similarities = [check_similarity(new_poem, old_poem) for old_poem in database]
    i = 0
    for similariti in similarities:
        i += 1
        if similariti > threshold:
            return i
    return 0


def censorship(validated_text):
    text = re.sub("[^\w]", " ", validated_text).lower()
    roman_names_list = ukrainian_profanity
    for word in text:
        if word in roman_names_list:
            raise CensorError()
    return True


ukrainian_stop_words = ['a', 'б', 'в', 'е', 'ж', 'з', 'у', 'я', 'є', 'і', 'аж', 'ви', 'де', 'до', 'за', 'зі', 'ми',
                        'на', 'не', 'ну', 'ні', 'по', 'та', 'ти', 'то', 'ту', 'ті', 'це', 'цю', 'ця', 'ці', 'чи', 'ще',
                        'що',
                        'як', 'їй', 'їм', 'їх', 'її', 'або', 'але', 'ало', 'без', 'був', 'вам', 'вас', 'ваш', 'вже',
                        'все', 'всю',
                        'вся', 'від', 'він', 'два', 'дві', 'для', 'ким', 'мож', 'моя', 'моє', 'мої', 'міг', 'між',
                        'мій', 'над',
                        'нам', 'нас', 'наш', 'нею', 'неї', 'них', 'ніж', 'ній', 'ось', 'при', 'про', 'під', 'пір',
                        'раз', 'рік', 'сам',
                        'сих', 'сім', 'так', 'там', 'теж', 'тим', 'тих', 'той', 'тою', 'три', 'тут', 'хоч', 'хто',
                        'цей', 'цим', 'цих',
                        'час', 'щоб', 'яка', 'які', 'адже', 'буде', 'буду', 'будь', 'була', 'були', 'було', 'бути',
                        'вами', 'ваша',
                        'ваше', 'ваші', 'весь', 'вниз', 'вона', 'вони', 'воно', 'всею', 'всім', 'всіх', 'втім', 'далі',
                        'двох',
                        'дуже', 'зате', 'його', 'йому', 'кого', 'коли', 'кому', 'куди', 'лише', 'люди', 'мало',
                        'мати', 'мене', 'мені', 'миру', 'мною', 'може', 'нами', 'наша', 'наше', 'наші', 'ними', 'ніби',
                        'один', 'поки',
                        'пора', 'рано', 'року', 'році', 'сама', 'саме', 'саму', 'самі', 'свою', 'своє', 'свої', 'себе',
                        'собі', 'став',
                        'суть', 'така', 'таке', 'такі', 'твоя', 'твоє', 'твій', 'тебе', 'тими', 'тобі', 'того', 'тоді',
                        'тому', 'туди',
                        'хоча', 'хіба', 'цими', 'цієї', 'часу', 'чого', 'чому', 'який', 'яких', 'якої', 'якщо', "ім'я",
                        'інша', 'інше',
                        'інші', 'буває', 'будеш', 'більш', 'вгору', 'вміти', 'внизу', 'вісім', 'давно', 'даром',
                        'добре', 'довго', 'друго',
                        'дякую', 'життя', 'зараз', 'знову', 'какая', 'кожен', 'кожна', 'кожне', 'кожні', 'краще',
                        'ледве', 'майже', 'менше',
                        'могти', 'можна', 'назад', 'немає', 'нижче', 'нього', 'однак', "п'ять", 'перед', 'поруч',
                        'потім', 'проти', 'після',
                        'років', 'самим', 'самих', 'самій', 'свого', 'своєї', 'своїх', 'собою', 'справ', 'такий',
                        'також', 'тепер', 'тисяч',
                        'тобою', 'треба', 'трохи', 'усюди', 'усіма', 'хочеш', 'цього', 'цьому', 'часто', 'через',
                        'шість', 'якого', 'іноді',
                        'інший', 'інших', 'багато', 'будемо', 'будете', 'будуть', 'більше', 'всього', 'всьому',
                        'далеко', 'десять', 'досить',
                        'другий', 'дійсно', 'завжди', 'звідси', 'зовсім', 'кругом', 'кілька', 'людина', 'можуть',
                        'навіть', 'навіщо',
                        'нагорі', 'небудь', 'низько', 'ніколи', 'нікуди', 'нічого', 'обидва', 'одного', 'однієї',
                        "п'ятий", 'перший',
                        'просто', 'раніше', 'раптом', 'самими', 'самого', 'самому', 'сказав', 'скрізь', 'сьомий',
                        'третій', 'тільки',
                        'хотіти', 'чотири', 'чудово', 'шостий', 'близько', 'важлива', 'важливе', 'важливі', 'вдалині',
                        'восьмий', 'говорив',
                        "дев'ять", 'десятий', 'зайнята', 'зайнято', 'зайняті', 'занадто', 'значить', 'навколо',
                        'нарешті', 'нерідко',
                        'повинно', 'посеред', 'початку', 'пізніше', 'сказала', 'сказати', 'скільки', 'спасибі',
                        'частіше', 'важливий',
                        'двадцять', "дев'ятий", 'зазвичай', 'зайнятий', 'звичайно', 'здається', 'найбільш', 'не',
                        'можна', 'недалеко',
                        'особливо', 'потрібно', 'спочатку', 'сьогодні', 'численна', 'численне', 'численні', 'відсотків',
                        'двадцятий',
                        'звідусіль', 'мільйонів', 'нещодавно', 'прекрасно', 'четвертий', 'численний', 'будь', 'ласка',
                        'дванадцять',
                        'одинадцять', 'сімнадцять', 'тринадцять', 'безперервно', 'дванадцятий', 'одинадцятий', 'одного',
                        'разу', "п'ятнадцять",
                        'сімнадцятий', 'тринадцятий', 'шістнадцять', 'вісімнадцять', "п'ятнадцятий", 'чотирнадцять',
                        'шістнадцятий',
                        'вісімнадцятий', "дев'ятнадцять", 'чотирнадцятий', "дев'ятнадцятий"]

ukrainian_profanity = ['хуй', 'хую', 'хуя', 'хуйом', 'хуєм', 'хуйня', 'хуйлан', 'хуйло', 'похуй', 'нахуй', 'хуї',
                       'охуїти', 'ахуїти',
                       'охуєть', 'ахуєть', 'пезда', 'пізда', 'піздєц', 'піздос', 'пиздець', 'пиздос', 'хуєсос',
                       'піздолиз', 'пиздіти',
                       'пиздиш', 'пиздів', 'пиздітиме', 'пиздіти', 'пизда', 'піздою', 'піздєцом', 'єбати', 'єбать',
                       'єбатись', 'єбаний',
                       'єбана', 'єбане', 'йобаний', 'йобане', 'йобана', 'єбало', 'єбальник', 'єбучка', 'сука', 'сучка',
                       'єбуться',
                       'наєбалово', 'найоб', 'йоб', 'йобтвоюмать', 'трахати', 'трахав', 'єбуть', 'єбе', 'трахаю', 'єбу',
                       'негр',
                       ]
