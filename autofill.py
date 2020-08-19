from lib import DbLib
import os

FILE_DB = os.path.abspath("./db/InvoiceOrganizer.db")

def auto_fill():
    import random
    import time

    def str_time_prop(start, end, format, prop):
        """Get a time at a proportion of a range of two formatted times.

        start and end should be strings specifying times formated in the
        given format (strftime-style), giving an interval [start, end].
        prop specifies how a proportion of the interval to be taken after
        start.  The returned time will be in the specified format.
        """

        stime = time.mktime(time.strptime(start, format))
        etime = time.mktime(time.strptime(end, format))

        ptime = stime + prop * (etime - stime)

        return time.strftime(format, time.localtime(ptime))

    def random_date(start, end, prop):
        return str_time_prop(start, end, "%d.%m.%Y", prop)

    api_db = DbLib.SmetKnigaDB(FILE_DB)

    api_db.remove_all_row("firma")
    api_db.remove_all_row("faktura")
    api_db.remove_all_row("lista_na_firmi")

    api_db.insert_firma("Firma 1")
    dict_firma = api_db.get_last_record("firma")

    api_db.insert_druga_firma("Druga Firma 1")
    dict_druga_firma = api_db.get_last_record("lista_na_firmi")

    for i in range(100):
        dict_kwargs = {}

        dict_kwargs["firma_id"] = dict_firma["id"]
        dict_kwargs["reden_broj"] = i + 1
        dict_kwargs["druga_firma_id"] = dict_druga_firma["id"]
        dict_kwargs["iznos"] = random.randrange(0, 100000)
        tip_faktura_id = random.randint(1, 2)
        dict_kwargs["tip_faktura_id"] = tip_faktura_id
        dict_kwargs["broj_na_faktura"] = "бр: {0:0>2d}".format(i + 1)

        data_na_priem = ""

        data_na_faktura = random_date("01.01.2019", "13.06.2020", random.random())
        # print (dict_kwargs)

        """
        {'id': 1, 'tip': 1, 'ime': 'влезна'}
        {'id': 2, 'tip': 2, 'ime': 'излезна'}
        """
        if tip_faktura_id == 1:
            data_na_priem = random_date("01.01.2019", "13.06.2020", random.random())

        dict_kwargs["data_na_priem"] = data_na_priem
        dict_kwargs["data_na_faktura"] = data_na_faktura

        api_db.insert_faktura(**dict_kwargs)

auto_fill()