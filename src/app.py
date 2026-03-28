from src.infrastructure.bootstrap.application import Application


def main() -> None:
    app = Application()
    app.run_http()


if __name__ == "__main__":
    main()



