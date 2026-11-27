import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "google/gemini-2.5-flash"


def load_env():
    env_file = BASE_DIR / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"'))


def read_selected_code(args):
    if not args:
        sys.exit("Ошибка: не передан путь к файлу")

    path = Path(args[0])
    if not path.exists():
        sys.exit(f"Ошибка: файл не найден: {path}")

    lines = path.read_text(encoding="utf-8").splitlines()
    start = int(args[1]) if len(args) > 1 and args[1].isdigit() else 1
    end = int(args[2]) if len(args) > 2 and args[2].isdigit() else len(lines)
    start, end = max(1, start), min(len(lines), end)

    numbered = "\n".join(f"{i}: {lines[i - 1]}" for i in range(start, end + 1))
    if not numbered.strip():
        sys.exit("Ошибка: выделенный фрагмент пустой")
    return path.name, start, end, numbered


def ask_model(prompt, code, file_name):
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        sys.exit("Ошибка: нет OPENROUTER_API_KEY в файле .env")

    payload = {
        "model": os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL),
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Файл: {file_name}\n\n```\n{code}\n```"},
        ],
    }
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-Title": "IDEA Test Reviewer",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        sys.exit(f"Ошибка API {e.code}: {e.read().decode('utf-8', 'ignore')}")
    except urllib.error.URLError as e:
        sys.exit(f"Ошибка сети: {e.reason}")

    return data["choices"][0]["message"]["content"]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    load_env()
    prompt = (BASE_DIR / "prompt.md").read_text(encoding="utf-8")
    file_name, start, end, code = read_selected_code(sys.argv[1:])

    model = os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL)
    print(f"Ревью: {file_name}, строки {start}-{end}, модель: {model}")
    print("Отправка запроса...\n")
    print(ask_model(prompt, code, file_name))


if __name__ == "__main__":
    main()