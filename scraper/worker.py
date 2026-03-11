import time
import re
import requests
from bs4 import BeautifulSoup
from utils.signature import sign_payload
from utils.normalize_car import prepare_car_data
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_URL = os.getenv("API_URL")
HEADERS = {
    "User-Agent": os.getenv("USER_AGENT", "Mozilla/5.0")
}


def fetch_page(url):
    """Загружает страницу и возвращает HTML."""
    try:
        print(f"Fetching URL: {url}")
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.encoding = r.apparent_encoding
        print(f"Status code: {r.status_code}")
        return r.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def parse_price_from_text(text):
    """Из текста цены вида '139.8万円' извлекает целое число (в йенах)."""
    if not text:
        return None
    m = re.search(r"(\d+(?:\.\d+)?)", text.replace(",", ""))
    if not m:
        return None
    return int(float(m.group(1)) * 10000)


def parse_year(text):
    """Из текста с годом извлекает четырёхзначное число."""
    if not text:
        return None
    m = re.search(r"(\d{4})", text)
    return int(m.group(1)) if m else None


def parse_detail_page(url):
    """
    Загружает детальную страницу и возвращает словарь со всеми данными автомобиля.
    """
    result = {
        "brand": None,
        "model": None,
        "price": None,
        "year": None,
        "color": None,
        "url": url
    }

    print(f"Parsing detail page: {url}")
    try:
        html = fetch_page(url)
        if not html:
            print("No HTML content from detail page")
            return result

        soup = BeautifulSoup(html, "lxml")

        # 1. Марка и модель из h1.title1
        h1 = soup.select_one("h1.title1")
        if h1:
            # Клонируем, чтобы не портить оригинал для дальнейшего поиска
            h1_copy = h1
            span = h1_copy.find("span")
            if span:
                span.extract()  # удаляем span, оставляем только текст до него
            full_title = h1_copy.get_text(strip=True)  # например "日産 デイズ"
            # Разделяем на марку и модель по первому пробелу (или &nbsp; который уже стал пробелом)
            parts = full_title.split(maxsplit=1)
            if len(parts) == 2:
                result["brand"] = parts[0].strip()
                result["model"] = parts[1].strip()
            elif len(parts) == 1:
                result["brand"] = parts[0].strip()
                result["model"] = ""   # на случай, если модель отсутствует (маловероятно)
        else:
            print("h1.title1 not found")

        # 2. Цена из атрибута content у .basePrice__price (самый надёжный)
        price_tag = soup.select_one(".basePrice__price")
        if price_tag and price_tag.has_attr("content"):
            price_str = price_tag["content"].replace(",", "")
            try:
                result["price"] = int(price_str)
                print(f"Found price from content: {result['price']}")
            except:
                pass
        else:
            # Если нет content, пробуем распарсить текст
            if price_tag:
                price_text = price_tag.get_text(strip=True)
                result["price"] = parse_price_from_text(price_text)
                print(f"Found price from text: {result['price']}")

        # 3. Год и цвет из всех таблиц defaultTable
        tables = soup.select(".defaultTable__table")

        for table in tables:
            rows = table.select("tr")

            for row in rows:
                ths = row.select("th")
                tds = row.select("td")

                for th, td in zip(ths, tds):
                    header = th.get_text(strip=True)
                    value = td.get_text(strip=True)

                    if "年式" in header and not result["year"]:
                        result["year"] = parse_year(value)
                        print(f"Found year: {result['year']}")

                    elif header == "色" and not result["color"]:
                        result["color"] = value
                        print(f"Found color: {result['color']}")
        else:
            print("Table .defaultTable not found, trying alternative selectors")
            # Запасной вариант: ищем по всей странице
            all_tds = soup.find_all("td")
            for td in all_tds:
                prev_th = td.find_previous("th")
                if prev_th:
                    header = prev_th.get_text(strip=True)
                    if "年式" in header and not result["year"]:
                        result["year"] = parse_year(td.get_text(strip=True))
                    elif "色" in header and not result["color"]:
                        result["color"] = td.get_text(strip=True)

    except Exception as e:
        print(f"Error parsing detail page {url}: {e}")
        import traceback
        traceback.print_exc()

    return result


def parse_card(card):
    """
    Из карточки в списке извлекает только ссылку на детальную страницу,
    затем парсит детальную страницу и возвращает полные данные.
    """
    try:
        # Поиск ссылки на детальную страницу
        link_tag = card.select_one("a.carCardList__bukkenLink")
        if not link_tag:
            # Если нет точного класса, пробуем первый a с подходящим href
            all_links = card.find_all("a", href=True)
            for link in all_links:
                if "/usedcar/detail/" in link["href"]:
                    link_tag = link
                    break
        if not link_tag:
            print("No link to detail page found in card")
            return None

        link = link_tag["href"]
        if not link.startswith("http"):
            url = BASE_URL + link
        else:
            url = link

        print(f"Detail URL: {url}")

        # Получаем данные с детальной страницы
        car = parse_detail_page(url)

        # Проверяем обязательные поля
        if not car.get("brand") or not car.get("model"):
            print(f"Missing brand or model for {url}")
            return None

        return car

    except Exception as e:
        print(f"Error parsing card: {e}")
        import traceback
        traceback.print_exc()
        return None


def send_car(car):
    """Отправляет данные автомобиля в API с повторными попытками."""
    if not car:
        print("No car data to send")
        return False

    print(f"Attempting to send car to API: {car}")

    for attempt in range(3):
        try:
            payload, signature = sign_payload(car)

            headers = {
                "X-Signature": signature,
                "Content-Type": "application/json"
            }

            r = requests.post(
                API_URL,
                data=payload,
                headers=headers,
                timeout=5
            )
            print(f"API response status: {r.status_code}")
            print(f"API response body: {r.text[:200]}")

            if r.status_code in (200, 201):
                print(f"Successfully sent car: {car['brand']} {car['model']}")
                return True
            else:
                print(f"API returned error status: {r.status_code}")

        except requests.exceptions.ConnectionError as e:
            print(f"Connection error (attempt {attempt + 1}/3): {e}")
            print(f"Make sure the backend is running at {API_URL}")
        except Exception as e:
            print(f"Error sending car (attempt {attempt + 1}/3): {e}")

        if attempt < 2:
            time.sleep(2)

    return False


def scrape():
    """Основной цикл сбора данных со страниц списка."""
    print("Starting scrape function")

    # URL для первой страницы со списком автомобилей
    # Вместо перебора можно сразу указать правильный:
    base_list_url = "https://www.carsensor.net/usedcar/index.html"
    cars_found = False

    for page in range(1, 4):  # парсим первые 3 страницы
        url = f"{base_list_url}?page={page}"
        print(f"\nScraping page {page}: {url}")

        html = fetch_page(url)
        if not html:
            continue

        soup = BeautifulSoup(html, "lxml")

        # Поиск карточек автомобилей – основной класс carCardList__item
        cards = soup.select("li.carCardList__item")
        if not cards:
            # Если не нашли, пробуем другие возможные селекторы
            alt_selectors = [".cassette", ".usedCarCassette", ".carCassette"]
            for sel in alt_selectors:
                cards = soup.select(sel)
                if cards:
                    print(f"Found {len(cards)} cards with selector '{sel}'")
                    break

        if not cards:
            print("No cards found on page")
            # Сохраняем HTML для анализа
            with open(f"debug_page_{page}.html", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Saved debug HTML to debug_page_{page}.html")
            continue

        print(f"Processing {len(cards)} cards")

        for idx, card in enumerate(cards, 1):
            print(f"\n--- Processing card {idx} ---")
            try:
                car = parse_card(card)
                if car:
                    car = prepare_car_data(car)
                    
                    if send_car(car):
                        cars_found = True
                    time.sleep(2)  # пауза между отправками
                else:
                    print(f"Failed to parse card {idx}")
            except Exception as e:
                print(f"Error processing card {idx}: {e}")
                import traceback
                traceback.print_exc()
            time.sleep(1)  # пауза между карточками

        time.sleep(3)  # пауза между страницами

    if not cars_found:
        print("\n⚠️ No cars were successfully processed and sent to API!")
        print("Please check:")
        print("1. Is the backend running at", API_URL)
        print("2. Are the HTML selectors correct for the current website structure")
        print("3. Check the debug HTML files saved in the current directory")


def worker():
    """Бесконечный цикл работы парсера."""
    print("Starting worker. Press Ctrl+C to stop.")

    while True:
        try:
            scrape()
        except KeyboardInterrupt:
            print("\nStopping worker...")
            break
        except Exception as e:
            print(f"Worker error: {e}")
            import traceback
            traceback.print_exc()

        print("\n" + "="*50)
        print("Sleeping for 5 minutes before next scrape cycle")
        print("="*50 + "\n")
        time.sleep(300)


if __name__ == "__main__":
    worker()