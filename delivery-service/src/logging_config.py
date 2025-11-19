import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        # format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        format='%(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),  # Вывод в терминал
            logging.FileHandler('app.log')      # Запись в файл
        ]
    )
    
    # Установите уровень логирования для разных библиотек
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    logging.getLogger('uvicorn').setLevel(logging.INFO)