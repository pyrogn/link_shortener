from fastapi import FastAPI

app = FastAPI()


def main():
    return 0


@app.get("/")
async def _():
    return "hello from link-shortener"


@app.post("/links/shorten")
async def _(url):
    return url


if __name__ == "__main__":
    main()
