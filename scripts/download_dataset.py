from pathlib import Path
from urllib.request import Request, urlopen


DATA_DIR = Path("datasets/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

URL = "https://snap.stanford.edu/data/soc-pokec-relationships.txt.gz"
OUTPUT = DATA_DIR / "soc-pokec-relationships.txt.gz"


def main():
    if OUTPUT.exists():
        print(f"Dataset already exists: {OUTPUT}")
        return

    print("Downloading SNAP soc-Pokec relationships...")
    print(f"Source: {URL}")

    request = Request(
        URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "Chrome/151.0 Safari/537.36"
            )
        },
    )

    with urlopen(request) as response:
        total_size = response.headers.get("Content-Length")

        if total_size:
            print(
                f"Download size: "
                f"{int(total_size) / (1024 * 1024):.2f} MB"
            )

        with open(OUTPUT, "wb") as file:
            while True:
                chunk = response.read(1024 * 1024)

                if not chunk:
                    break

                file.write(chunk)

    print()
    print("Download completed successfully!")
    print(f"Saved to: {OUTPUT}")
    print(f"File size: {OUTPUT.stat().st_size / (1024 * 1024):.2f} MB")


if __name__ == "__main__":
    main()