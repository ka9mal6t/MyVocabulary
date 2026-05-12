import inspect
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


class Log:
    BASE_DIR = Path("logs")
    BASE_DIR.mkdir(exist_ok=True)
    FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    @classmethod
    def _get_caller_name(cls) -> str:
        frame = inspect.currentframe()
        if frame is None:
            return "app"

        frame = frame.f_back
        while frame and frame.f_code.co_name in {
            "_get_caller_name", "get", "info", "warning", "error", "debug"
        }:
            frame = frame.f_back

        if frame is None:
            return "app"

        module = inspect.getmodule(frame)
        if module is None or module.__name__ == "__main__":
            return Path(frame.f_code.co_filename).stem
        return module.__name__

    @classmethod
    def _create_handler(cls, path: Path, level: int) -> TimedRotatingFileHandler:
        handler = TimedRotatingFileHandler(
            path,
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8",
        )
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter(cls.FORMAT))
        return handler

    @classmethod
    def get(cls, name: str | None = None) -> logging.Logger:
        if name is None:
            name = cls._get_caller_name()

        logger = logging.getLogger(name)
        if logger.handlers:
            return logger

        logger.setLevel(logging.INFO)
        logger.propagate = False

        log_dir = cls.BASE_DIR / name
        log_dir.mkdir(parents=True, exist_ok=True)

        logger.addHandler(cls._create_handler(log_dir / "info.log", logging.INFO))
        logger.addHandler(cls._create_handler(log_dir / "error.log", logging.ERROR))

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(cls.FORMAT))
        logger.addHandler(console_handler)

        return logger

    @classmethod
    def info(cls, msg: str, *args, **kwargs) -> None:
        cls.get().info(msg, *args, **kwargs)

    @classmethod
    def warning(cls, msg: str, *args, **kwargs) -> None:
        cls.get().warning(msg, *args, **kwargs)

    @classmethod
    def error(cls, msg: str, *args, **kwargs) -> None:
        cls.get().error(msg, *args, **kwargs)

    @classmethod
    def debug(cls, msg: str, *args, **kwargs) -> None:
        cls.get().debug(msg, *args, **kwargs)