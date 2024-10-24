import requests
import requests.cookies
import warnings
warnings.filterwarnings("ignore")

def read_cookies():
    with open("cookies.txt", "r") as r:
        cookies = r.read()
    cookies_dict = {cookie.split('=')[0]: cookie.split('=')[1] for cookie in cookies.split('; ')}
    return cookies_dict

def get_request(url, is_xml):
    session = requests.Session()
    dict = read_cookies()
    for key in dict:
        session.cookies.set(key, dict[key], domain = "antitreningi.ru")

    if (is_xml): response = session.get(url, headers={"X-Requested-With" : "XMLHttpRequest"})
    else: response = session.get(url)
    
    return response.text


def worker():
    result = []
    size_sum = 0.0

    url = "https://antitreningi.ru/api/group/by-author?limit=5&page=1"
    doc = get_request(url, False)
    page_count = int(doc.split('"pageCount":')[1].split("}")[0])
    if page_count > 1:
        for page in range(2, page_count + 1):
            url = f"https://antitreningi.ru/api/group/by-author?limit=5&page={page}"
            doc = doc + get_request(url, False)
    for line in doc.split('"id":'):
        id = line.split(',')[0]
        if id.__contains__("true"): continue
        name = line.split('"name":')[1].split(',')[0]

        path = f"Папка: {name.encode('utf-8').decode('unicode_escape')}"
        print(path)
        result.append(path)

        url = f"https://antitreningi.ru/panel/files/courses?group_id={id}&limit=12&page=1"
        doc = get_request(url, True)
        if not doc.__contains__("id"): continue
        for line in doc.split('"id":'):
                 id = line.split(',')[0]
                 if id.__contains__("{"): continue
                 name = line.split('"name":')[1].split(',')[0]
                 file_id_list = []
                 path = f"  Курс: {name.encode('utf-8').decode('unicode_escape')}"
                 print(path)
                 result.append(path)
                 url = f"https://antitreningi.ru/panel/files/notuse?tab=all&course_id={id}&type=all&sort=added&sort_type=desc&search=&page=1&limit=999"
                 doc = get_request(url, True)

                 for line in doc.split('"id":'):
                     file_id = line.split(',')[0]
                     if file_id.__contains__("files"): continue
                     file_id_list.append(file_id)

                 for file_id in file_id_list:
                     url = f"https://antitreningi.ru/panel/files/edit?course_id={id}&id={file_id}"
                     doc = get_request(url, False)
                     if not doc.__contains__("Веб версия"): continue
                     size = doc.split("<span>Веб версия:</span>")[1].split(">")[1].split(" MB")[0]
                     name = doc.split("наименование")[1].split('value="')[1].split('"')[0]
                     file_string = f"    {name}: {size} MB"
                     result.append(file_string)
                     print(file_string)
                     size_sum = size_sum + float(size)   
    total = f"РАЗМЕР ВЕБ-ВЕРСИЙ ВСЕХ ФАЙЛОВ: {size_sum} MB"
    print(total)
    result.append(total)
    return result

with open("file_list.txt", "w", encoding = "utf-8") as w:
          w.write(str.join("\n", worker()))

input()
