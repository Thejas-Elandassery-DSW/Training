import logging

def main():
    logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
    logging.debug('This is a debug message')
    logging.info('This is an info message')
    logging.warning('This is a warning message')
    logging.error('This is an error message')
    logging.critical('This is a critical message')
    # logging.basicConfig(filename="errors.log", level=logging.ERROR)

    try:
        result = 10 / 0
    except Exception as e:
        logging.error("Exception occurred", exc_info=True)


main()