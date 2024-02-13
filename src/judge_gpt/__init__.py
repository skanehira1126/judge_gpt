from logging import INFO, Formatter, StreamHandler, getLogger

from judge_gpt.judge import ColumnInfo, JudgeGPT

logger = getLogger(__name__)
logger.setLevel(INFO)

stream_handler = StreamHandler()
stream_handler.setLevel(INFO)
stream_handler.setFormatter(Formatter("[{asctime} {levelname}] - {name}: {message}", style="{"))
