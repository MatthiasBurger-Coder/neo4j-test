from src.infrastructure.bootstrap.application import Application


def main() -> None:
    app = Application()
    context = app.start()

    try:
        context.logger.info("Program is running")
        # Start actual workflow here.
    finally:
        app.stop()


if __name__ == "__main__":
    main()



