"""Main module for running the application."""

from status_line import StatusLine


def main():
    """Main function."""
    status_line = StatusLine()
    while True:
        try:
            model = input("Enter model: ")
            if not model:
                break
            status_line.update(model=model)
            status_line.display()
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
