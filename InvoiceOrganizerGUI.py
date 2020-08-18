#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Re: #4044 (comment) and #4044 (comment), I'm seeing the same failure. This problem was "solved" when I upgraded to
# shiboken2-5.12.3/PySide2-5.12.3.

import sys
import os
import datetime
import operator

try:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtPrintSupport import *
    from PySide2 import __version__
except ImportError:
    from PySide.QtCore import *
    from PySide.QtGui import *
    from PySide import __version__

from lib import DbLib


def find_data_file(filename):
    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.dirname(__file__)

    return os.path.join(datadir, filename)

FILE_DB = find_data_file("./db/InvoiceOrganizer.db")
FILE_STAMP = find_data_file("./stamp/img_stamp.png")
FILE_STAMP_HTML = find_data_file("./html_template/html_a4_page.html")
# FILE_STAMP_HTML = find_data_file(r"C:\Users\Softwaresky\PycharmProjects\SmetkovotstvenaKniga\html_output.html")


Q_STYLE = """
QLabel#lblTitle {font-size:35px; font-weight: bold;}
QTableView#tbStamp {padding: 0px; margin: 0px; border: 2px solid purple; color: purple; font-size: 12px; font-weight: bold;}
QTableView#tbStamp::item {padding: 0px; margin: 0px; border: 2px solid purple; }
"""

def compare_two_dict(x = {}, y = {}):

    if x and y:
        shared_items = {k: x[k] for k in x if k in y and x[k] == y[k]}
        return len(shared_items) == len(x)
    else:
        return False

class SpinBox(QSpinBox):

    def wheelEvent(self, event):
        event.ignore()

class CalendarPickerWdg(QDateEdit):

    def __init__(self, parent=None, *args, **kwargs):
        super(self.__class__, self).__init__(parent)
        # self.setSpecialValueText(" ")
        self.setDate(QDate.currentDate())
        self.setCalendarPopup(True)
        self.setDisplayFormat("dd.MM.yyyy")

    def wheelEvent(self, event):
        event.ignore()

class ComboBox(QComboBox):

    def wheelEvent(self, event):
        event.ignore()

def correct_date(str_date = ""):

    if str_date:
        day, month, year = str(str_date).split(".") if "." in str_date else str(str_date).split(",")
        dt_this = datetime.datetime(year=int(year), month=int(month), day=int(day))
        return dt_this.strftime("%d.%m.%Y")
    else:
        return str_date

class TableModel(QAbstractTableModel):

    def __init__(self, data=[], header=[]):
        super(TableModel, self).__init__()
        self._data = data
        self._header = header

    def get_row_values(self, index=0):

        if index < len(self._data):
            return self._data[index]
        return []

    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None

        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            value = self._data[index.row()][index.column()]

            if isinstance(value, float):
                # Render float to 2 dp
                return "{0:.2f}".format(value)
            elif isinstance(value, int):
                return "{0}".format(value)

            return value

        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

    def headerData(self, col, orientation=Qt.Horizontal, role=Qt.DisplayRole):
        if self._header:
            if orientation == Qt.Horizontal and role == Qt.DisplayRole:
                return self._header[col]
        return None

    def sort(self, col, order):

        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self._data = sorted(self._data, key=operator.itemgetter(col))
        if order == Qt.DescendingOrder:
            self._data.reverse()
        self.emit(SIGNAL("layoutChanged()"))

    def rowCount(self, *args):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, *args):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0]) if len(self._data) > 0 else 0

class TableStampWdg(QTableWidget):

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self.setObjectName("tbStamp")

        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)

        self.setColumnCount(3)
        self.setRowCount(4)

        self.setShowGrid(False)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setFocusPolicy(Qt.NoFocus)

        w = 226.77

        h = w/3

        # w = 400
        self.setFixedSize(w, h)

        self.horizontalHeader().setMinimumSectionSize(0)
        self.verticalHeader().setMinimumSectionSize(h / self.rowCount() - 1)

        if __version__ == '1.2.4':
            self.horizontalHeader().setResizeMode(0, QHeaderView.Interactive)
            self.horizontalHeader().resizeSection(0, 30)
            self.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)
            self.horizontalHeader().setResizeMode(2, QHeaderView.Stretch)

            for row in range(self.rowCount()):
                self.verticalHeader().setResizeMode(row, QHeaderView.Stretch)
        else:

            self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
            self.horizontalHeader().resizeSection(0, 30)
            self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

            for row in range(self.rowCount()):
                self.verticalHeader().setSectionResizeMode(row, QHeaderView.Stretch)

        # self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        # self.horizontalHeader().resizeSection(0, 30)
        # self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        #
        # for row in range(self.rowCount()):
        #     self.verticalHeader().setSectionResizeMode(row, QHeaderView.Stretch)

        self.organized_cells()
        self.fill_table()

    def organized_cells(self):


        for row in range(self.rowCount()):
            if row != self.rowCount() - 1:
                self.setSpan(row, 0, 1, self.columnCount())



    def fill_table(self, tip_faktura=0, data="", interen_broj="0504", reden_broj=0):

        tbiTip = QTableWidgetItem("ПРИМЕНО")
        tbiTip.setTextAlignment(Qt.AlignCenter)
        self.setItem(0, 0, tbiTip)

        tbiData = QTableWidgetItem("ДАТА: {0}".format(data))
        tbiData.setTextAlignment(Qt.AlignLeft)
        tbiData.setTextAlignment(Qt.AlignVCenter)
        self.setItem(1, 0, tbiData)

        tbiBrojStr = QTableWidgetItem("БРОЈ")
        tbiBrojStr.setTextAlignment(Qt.AlignCenter)
        self.setItem(2, 0, tbiBrojStr)

        tiBrojFiksen = QTableWidgetItem("1")
        tiBrojFiksen.setTextAlignment(Qt.AlignCenter)
        self.setItem(3, 0, tiBrojFiksen)

        interna_sifra = "{0}-{1}".format(interen_broj, tip_faktura)
        tbiInternaSifra = QTableWidgetItem(interna_sifra)
        tbiInternaSifra.setTextAlignment(Qt.AlignCenter)
        # tbiInternaSifra.setTextAlignment(Qt.AlignLeft)
        # tbiInternaSifra.setTextAlignment(Qt.AlignVCenter)
        self.setItem(3, 1, tbiInternaSifra)

        tbiRedenBroj = QTableWidgetItem(str(reden_broj))
        tbiRedenBroj.setTextAlignment(Qt.AlignCenter)
        self.setItem(3, 2, tbiRedenBroj)

    def get_pixmap(self):

        g = self.geometry()
        fg = self.frameGeometry()
        rfg = fg.translated(-g.left(), -g.top())
        pixmap = QPixmap.grabWindow(self.winId(),
                                    rfg.left(), rfg.top(),
                                    rfg.width(), rfg.height())
        return pixmap

class InsertFirmaWdg(QWidget):

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self.build_ui()

    def create_content_layout(self):

        form_layout = QFormLayout()
        form_layout.setSpacing(5)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignLeft)

        self.txtIme = QLineEdit()
        form_layout.addRow("Име на фирма:", self.txtIme)

        self.btnSubmit = QPushButton("Внеси")
        self.btnSubmit.setFixedWidth(100)
        form_layout.addRow("", self.btnSubmit)

        return form_layout

    def clear_items(self):
        self.txtIme.clear()

    def build_ui(self):
        self.setWindowTitle("Нова фирма")
        main_layout = QVBoxLayout()
        main_layout.addItem(self.create_content_layout())

        self.setLayout(main_layout)


class InsertFakturaWdg(QWidget):

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self.txtNaziv_comp = QCompleter()
        self.txtNaziv_comp.setCaseSensitivity(Qt.CaseInsensitive)
        # self.txtNaziv_comp.setCompletionRole(Qt.DisplayRole)
        # self.txtNaziv_comp.setCompletionMode(QCompleter.PopupCompletion)
        # self.txtNaziv_comp.setCompletionColumn(0)

        self.dict_reden_broj_counter = {}
        self.mode = 0

        self.build_ui()

    def create_content_layout(self):

        item_layout = QVBoxLayout()
        item_layout.setAlignment(Qt.AlignLeft)

        form_layout = QFormLayout()
        form_layout.setSpacing(5)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignLeft)

        date_tooltip = "Форматот на датумот треба да биде:\nDD.MM.YYYY\nна пример 31.12.2019"

        self.spnRedenBroj = SpinBox()
        self.spnRedenBroj.setMinimum(0)
        self.spnRedenBroj.setFixedWidth(100)
        form_layout.addRow("Реден број:", self.spnRedenBroj)

        self.txtFakturaBroj = QLineEdit()
        self.txtFakturaBroj.setFixedWidth(100)
        form_layout.addRow("Број на фактура:", self.txtFakturaBroj)

        self.txtNaziv = QLineEdit()
        self.txtNaziv.setCompleter(self.txtNaziv_comp)
        form_layout.addRow("Назив на фирма:", self.txtNaziv)

        self.txtDataPriem = QLineEdit()
        self.txtDataPriem.setFixedWidth(100)
        self.txtDataPriem.setToolTip(date_tooltip)
        self.txtDataPriem.setEnabled(False)
        form_layout.addRow("Дата на прием:", self.txtDataPriem)

        self.txtDataFaktura = QLineEdit()
        self.txtDataFaktura.setFixedWidth(100)
        self.txtDataFaktura.setToolTip(date_tooltip)
        form_layout.addRow("Дата на фактура:", self.txtDataFaktura)

        validator_double = QDoubleValidator()
        self.txtIznos = QLineEdit()
        self.txtIznos.setFixedWidth(100)
        self.txtIznos.setValidator(validator_double)
        form_layout.addRow("Износ:", self.txtIznos)

        self.txtZabeleska = QLineEdit()
        form_layout.addRow("Забелешка:", self.txtZabeleska)

        self.btnSubmit = QPushButton("Внеси")
        self.btnSubmit.setFixedWidth(100)
        form_layout.addRow("", self.btnSubmit)

        return form_layout

    def clear_items(self):
        self.spnRedenBroj.clear()
        self.txtFakturaBroj.clear()
        self.txtDataFaktura.clear()
        self.txtDataPriem.clear()
        self.txtNaziv.clear()
        self.txtIznos.clear()
        self.txtZabeleska.clear()

    def show_specific(self):

        self.txtDataPriem.setEnabled(False)

        if self.mode == 1:
            self.txtDataPriem.setEnabled(True)

    def fill_txtNaziv_completer(self, lst_item = []):

        model_item = QStringListModel(lst_item)
        self.txtNaziv_comp.setModel(model_item)

    def set_dict_reden_broj_counter(self):

        reden_broj = self.spnRedenBroj.value()
        if reden_broj not in self.dict_reden_broj_counter:
            self.dict_reden_broj_counter[self.mode] = 0
        self.dict_reden_broj_counter[self.mode] = reden_broj

    def fill_spnRedenBroj(self):

        reden_broj_counter = 0
        if self.mode in self.dict_reden_broj_counter:
            reden_broj_counter = self.dict_reden_broj_counter[self.mode]
        self.spnRedenBroj.setValue(reden_broj_counter + 1)

    def build_ui(self):
        self.setWindowTitle("Додади фактура")
        main_layout = QVBoxLayout()
        main_layout.addItem(self.create_content_layout())

        self.setLayout(main_layout)

class SmetkovotstvenaKnigaWdg(QWidget):

    def __init__(self, parent=None, dict_firma = {}, db_api=DbLib.SmetKnigaDB):
        super(self.__class__, self).__init__(parent)

        self.dict_firma = dict_firma
        self.dict_tip_faktura = {}
        self.db_api = db_api

        self.dict_cb_items = {}
        self.lst_dict_fakturi = []
        self.lst_dict_lista_na_firmi = []

        self.insertFakturaWdg = InsertFakturaWdg()
        self.insertFakturaWdg.show_specific()
        self.insertFakturaWdg.btnSubmit.clicked.connect(self.clicked_insertFakturaWdg_btnSubmit)

        self.build_ui()

        self.fill_firma_title()
        self.fill_faktura_tip()
        # self.fill_fakturi()
        self.fill_completer_txtNaziv()

    def create_delete_firma_layout(self):
        item_layout = QHBoxLayout()
        item_layout.setAlignment(Qt.AlignRight)

        self.btnRemoveFirma = QPushButton("Избриши Фирма")
        item_layout.addWidget(self.btnRemoveFirma)

        return item_layout

    def create_firma_title_layout(self):
        item_layout = QHBoxLayout()
        item_layout.setAlignment(Qt.AlignCenter)

        self.lblFirmaIme = QLabel("")
        self.lblFirmaIme.setObjectName("lblTitle")
        item_layout.addWidget(self.lblFirmaIme)

        return item_layout

    def create_faktura_tip_layout(self):
        item_layout = QHBoxLayout()
        item_layout.setSpacing(5)
        item_layout.setAlignment(Qt.AlignLeft)

        lblFakturaTip = QLabel("Фактура тип: ")
        lblFakturaTip.setObjectName("lblFakturaTip")
        item_layout.addWidget(lblFakturaTip)

        self.cmbFakturaTip = ComboBox()
        self.cmbFakturaTip.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.cmbFakturaTip.currentIndexChanged.connect(self.currentIndexChanged_cmbFakturaTip)

        item_layout.addWidget(self.cmbFakturaTip)

        return item_layout

    def create_insert_faktura_layout(self):
        item_layout = QHBoxLayout()
        item_layout.setSpacing(5)
        item_layout.setAlignment(Qt.AlignLeft)

        self.grp_insert_faktura = QGroupBox()
        self.grp_insert_faktura.setTitle("Нова фактура")
        self.grp_insert_faktura.setCheckable(True)
        self.grp_insert_faktura.setChecked(True)

        grp_insert_faktura_layout = QVBoxLayout()

        grp_insert_faktura_layout.addWidget(self.insertFakturaWdg)

        self.grp_insert_faktura.setLayout(grp_insert_faktura_layout)

        item_layout.addWidget(self.grp_insert_faktura)

        self.grp_insert_faktura.toggled.connect(lambda: self.toggleGroup(self.grp_insert_faktura))

        self.grp_insert_faktura.setChecked(False)

        return item_layout

    def create_table_fakturi_layout(self):
        item_layout = QVBoxLayout()
        item_layout.setSpacing(5)

        table_top_layout = QHBoxLayout()

        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(5)

        filter_date_layout = QHBoxLayout()
        filter_date_layout.setSpacing(5)
        filter_date_layout.setAlignment(Qt.AlignLeft)
        self.dpFilterDataOd = CalendarPickerWdg()
        self.dpFilterDataOd.setFixedWidth(100)
        self.dpFilterDataOd.dateChanged.connect(self.dateChanged_dtFilter)
        filter_date_layout.addWidget(self.dpFilterDataOd)
        filter_date_layout.addWidget(QLabel("-"))
        self.dpFilterDataDo = CalendarPickerWdg()
        self.dpFilterDataDo.setFixedWidth(100)
        self.dpFilterDataDo.dateChanged.connect(self.dateChanged_dtFilter)
        filter_date_layout.addWidget(self.dpFilterDataDo)
        filter_layout.addItem(filter_date_layout)

        filter_naziv_layout = QHBoxLayout()
        filter_naziv_layout.setAlignment(Qt.AlignLeft)
        self.txtFilterNaziv = QLineEdit()
        self.txtFilterNaziv.setPlaceholderText("Назив на фирма")
        self.txtFilterNaziv.setFixedWidth(200)
        self.txtFilterNaziv.textChanged.connect(self.textChanged_txtFilterNaziv)
        filter_naziv_layout.addWidget(self.txtFilterNaziv)
        filter_layout.addItem(filter_naziv_layout)

        table_top_layout.addItem(filter_layout)

        right_layout = QHBoxLayout()
        right_layout.setSpacing(5)
        right_layout.setAlignment(Qt.AlignRight)

        self.cmbPrintType = QComboBox()
        self.cmbPrintType.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.cmbPrintType.addItem("-- Избери --")
        self.cmbPrintType.addItem("Печат")
        self.cmbPrintType.addItem("Табела")
        right_layout.addWidget(self.cmbPrintType)

        self.btnPrintPreview = QPushButton("Print Preview")
        self.btnPrintPreview.setFixedWidth(100)
        self.btnPrintPreview.clicked.connect(self.clicked_btnPrintPreview)
        right_layout.addWidget(self.btnPrintPreview)

        table_top_layout.addItem(right_layout)

        item_layout.addItem(table_top_layout)

        table_layout = QHBoxLayout()
        table_layout.setSpacing(5)

        self.tbFakturi = QTableView()
        self.tbFakturi.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbFakturi.setSortingEnabled(True)
        self.tbFakturi.setSelectionMode(QAbstractItemView.SingleSelection)
        # self.tbFakturi.clicked.connect(self.clicked_tbFakturi)

        self.tbFakturi.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tbFakturi.customContextMenuRequested.connect(self.customContextMenu_tbFakturi)
        table_layout.addWidget(self.tbFakturi)

        table_right_layout = QVBoxLayout()
        table_right_layout.setAlignment(Qt.AlignTop)
        self.tbStamp = TableStampWdg()
        table_right_layout.addWidget(self.tbStamp)

        table_layout.addItem(table_right_layout)

        table_layout.setStretch(0, 100)
        table_layout.setStretch(1, 0)

        item_layout.addItem(table_layout)

        return item_layout

    def customContextMenu_tbFakturi(self, pos):

        faktura_id = 0
        lst_sel_index = self.tbFakturi.selectedIndexes()
        if lst_sel_index:
            lst_value = self.tbFakturi.model().get_row_values(lst_sel_index[0].row())
            faktura_id = lst_value[0]

        menu = QMenu(self)
        act_delete_faktura = QAction('Избриши фактура', self, triggered=lambda f=self.clicked_act_delete_faktura, arg=faktura_id: f(arg))
        act_delete_faktura.setEnabled(True if lst_sel_index else False)
        menu.addAction(act_delete_faktura)

        # add other required actions
        menu.popup(QCursor.pos())

    def clicked_act_delete_faktura(self, faktura_id=0, *args):
        if faktura_id:
            if isinstance(self.db_api, DbLib.SmetKnigaDB):
                self.db_api.remove_faktura(faktura_id)

                self.fill_fakturi()

    def textChanged_txtFilterNaziv(self, *args):
        self.fill_fakturi()

    def currentChanged_tbFakturi(self, *args):
        self.fill_table_stamp()

    def dateChanged_dtFilter(self):
        self.fill_fakturi()

    def clicked_insertFakturaWdg_btnSubmit(self):

        try:
            if not self.dict_firma or 'id' not in self.dict_firma:
                raise Exception("Немате одбрато фирма!")

            if 'id' not in self.dict_tip_faktura:
                raise Exception("Немате одбрато тип на фактура!")

            naziv_firma = self.insertFakturaWdg.txtNaziv.text()
            naziv_firma = str(naziv_firma).strip()
            reden_broj = self.insertFakturaWdg.spnRedenBroj.value()

            dict_druga_firma = {}
            for dict_druga_firma_ in self.lst_dict_lista_na_firmi:
                if dict_druga_firma_["naziv"] == naziv_firma:
                    dict_druga_firma = dict_druga_firma_
                    break

            # firma_id=-1, tip_faktura_id=-1, reden_broj=-1, data_na_priem='', data_na_faktura='', broj_na_faktura='', naziv='', iznos=0.0, zabeleska=''
            dict_kwargs = {}
            dict_kwargs["firma_id"] = self.dict_firma["id"]
            dict_kwargs["tip_faktura_id"] = self.dict_tip_faktura["id"]
            dict_kwargs["reden_broj"] = reden_broj
            dict_kwargs["data_na_priem"] = correct_date(self.insertFakturaWdg.txtDataPriem.text())
            dict_kwargs["data_na_faktura"] = correct_date(self.insertFakturaWdg.txtDataFaktura.text())
            dict_kwargs["broj_na_faktura"] = self.insertFakturaWdg.txtFakturaBroj.text()
            dict_kwargs["iznos"] = float(self.insertFakturaWdg.txtIznos.text())
            dict_kwargs["zabeleska"] = self.insertFakturaWdg.txtZabeleska.text()

            if not self.insertFakturaWdg.txtDataPriem.hasAcceptableInput():
                raise Exception("Датумот мора да биде фо формат DD.MM.YYYY\nна пример 31.12.2019")

            if not self.insertFakturaWdg.txtDataFaktura.hasAcceptableInput():
                raise Exception("Датумот мора да биде фо формат DD.MM.YYYY\nна пример 31.12.2019")

            if not self.insertFakturaWdg.txtIznos.hasAcceptableInput():
                raise Exception("Износот мора да биде децимален број, несмее да има други знаци!")

            if isinstance(self.db_api, DbLib.SmetKnigaDB):

                if not dict_druga_firma:
                    self.db_api.insert_druga_firma(naziv=naziv_firma)
                    dict_druga_firma = self.db_api.get_last_record("lista_na_firmi")

                dict_kwargs["druga_firma_id"] = dict_druga_firma["id"]

                self.db_api.insert_faktura(**dict_kwargs)

                self.insertFakturaWdg.set_dict_reden_broj_counter()

            self.insertFakturaWdg.clear_items()
            self.insertFakturaWdg.fill_spnRedenBroj()

            self.fill_completer_txtNaziv()
            self.fill_fakturi()

        except Exception as err:
            QMessageBox.critical(self, "Error", str(err))

    def currentIndexChanged_cmbFakturaTip(self, *args):

        selected_faktura_tip = self.cmbFakturaTip.currentText()
        self.dict_tip_faktura = {}

        if selected_faktura_tip in self.dict_cb_items:
            self.dict_tip_faktura = self.dict_cb_items[selected_faktura_tip]
            self.insertFakturaWdg.mode = self.dict_tip_faktura["tip"]
            self.insertFakturaWdg.show_specific()
            self.insertFakturaWdg.fill_spnRedenBroj()

        self.fill_fakturi()
        self.fill_table_stamp()

    def fill_firma_title(self):

        self.lblFirmaIme.clear()

        if "ime" in self.dict_firma:
            self.lblFirmaIme.setText(self.dict_firma["ime"])
        else:
            self.lblFirmaIme.setText(u"[Одбери фирма]")

    def fill_faktura_tip(self):
        selected_faktura_tip = self.cmbFakturaTip.currentText()

        self.cmbFakturaTip.clear()
        self.dict_cb_items = {}

        if self.db_api and isinstance(self.db_api, DbLib.SmetKnigaDB):

            index = 0
            for dict_tip_f in self.db_api.get_tip_faktura():
                self.dict_cb_items[dict_tip_f["ime"]] = dict_tip_f

                self.cmbFakturaTip.addItem(dict_tip_f["ime"])

                if selected_faktura_tip == dict_tip_f["ime"]:
                    self.cmbFakturaTip.setCurrentIndex(index)

                index += 1

    def fill_fakturi(self):

        self.lst_dict_fakturi = []
        lst_data = []
        lst_header = ["id", "Реден број", "Назив на фирма", "Тип фактура", "Број на фактура", "Дата на прием", "Дата на фактура", "Износ", "Забелешка"]

        firma_id = self.dict_firma.get("id")
        tip_faktura_id = self.dict_tip_faktura.get("id")
        tdDateFilterOd = self.dpFilterDataOd.date().toPython()
        tdDateFilterDo = self.dpFilterDataDo.date().toPython()
        naziv_firma_filter = self.txtFilterNaziv.text()

        date_format = "%d.%m.%Y"

        if tip_faktura_id is not None and firma_id is not None:
            if self.db_api and isinstance(self.db_api, DbLib.SmetKnigaDB):
                lst_fakturi = self.db_api.get_fakturi(firma_id=firma_id, tip_faktura_id=tip_faktura_id)
                if lst_fakturi:
                    for dict_fakturi in lst_fakturi:
                        str_date_faktura = dict_fakturi["data_na_faktura"]
                        dtFaktura = datetime.datetime.strptime(str_date_faktura, date_format).date()
                        state_date = tdDateFilterOd <= dtFaktura <= tdDateFilterDo
                        state_naziv = True
                        if naziv_firma_filter:
                            state_naziv = str(naziv_firma_filter).lower() in str(dict_fakturi["naziv"]).lower()

                        if state_date and state_naziv:
                            self.lst_dict_fakturi.append(dict_fakturi)
                            lst_data.append(list(dict_fakturi.values()))

        table_model = TableModel(lst_data, lst_header)
        self.tbFakturi.setModel(table_model)
        self.tbFakturi.setColumnHidden(0, True)

        self.tbFakturi.selectionModel().currentChanged.connect(self.currentChanged_tbFakturi)


        self.fill_table_stamp()

    def fill_table_stamp(self):

        tip_faktura = self.dict_tip_faktura["tip"] if self.dict_tip_faktura["tip"] else 0
        reden_broj = 0
        f_data = ""

        lst_sel_index = self.tbFakturi.selectedIndexes()
        if lst_sel_index:

            lst_value = self.tbFakturi.model().get_row_values(lst_sel_index[0].row())
            if lst_value:
                faktura_id = lst_value[0]

                dict_faktura = {}
                for dict_f in self.lst_dict_fakturi:
                    if dict_f["id"] == faktura_id:
                        dict_faktura = dict_f
                        break

                f_data = dict_faktura["data_na_priem"] if dict_faktura["data_na_priem"] else dict_faktura["data_na_faktura"]
                reden_broj = dict_faktura["reden_broj"]

        self.tbStamp.fill_table(data=f_data, tip_faktura=tip_faktura, reden_broj=reden_broj)

    def fill_completer_txtNaziv(self):

        lst_naziv_firmi = []
        self.lst_dict_lista_na_firmi = []

        if isinstance(self.db_api, DbLib.SmetKnigaDB):
            lst_list_na_firmi = self.db_api.get_lista_na_firmi()
            for dict_druga_firma in lst_list_na_firmi:
                self.lst_dict_lista_na_firmi.append(dict_druga_firma)
                lst_naziv_firmi.append(dict_druga_firma["naziv"])

        self.insertFakturaWdg.fill_txtNaziv_completer(lst_naziv_firmi)


    def get_table_html(self):

        lst_html = []
        lst_html.append("<table border=1 cellPadding=0 cellSpacing=0 width=100%>")

        tbFakturi_model = self.tbFakturi.model()

        lst_html.append("\t<thead>")

        if isinstance(tbFakturi_model, TableModel):
            lst_html.append("\t\t<tr>")
            for col in range(1, tbFakturi_model.columnCount()):
                value = tbFakturi_model.headerData(col)
                lst_html.append("\t\t\t<th>{0}</th>".format(value))

            lst_html.append("\t\t</tr>")

        lst_html.append("\t</thead>")
        lst_html.append("\t<tbody>")

        for row in range(tbFakturi_model.rowCount()):

            lst_html.append("\t\t<tr>")

            for col in range(1, tbFakturi_model.columnCount()):
                model_index = tbFakturi_model.index(row, col)
                table_value = tbFakturi_model.data(model_index)
                lst_html.append("\t\t\t<td>{0}</td>".format(table_value))
            lst_html.append("\t\t</tr>")

        lst_html.append("\t</tbody>")
        lst_html.append("</table>")

        return "\n".join(lst_html)


    def clicked_btnPrintPreview(self):

        html_content = ""

        with open(FILE_STAMP_HTML, "r", encoding="utf-8") as f:
            html_content = f.read()

        if self.cmbPrintType.currentIndex() == 1:   # Stamp html content

            pixmap = self.tbStamp.get_pixmap()
            pixmap.save(FILE_STAMP, "png")
            abs_path = os.path.abspath(FILE_STAMP)

            html_content = str(html_content).replace("{page_content}", '<img class="img_stamp" src="{file_stamp}">').replace("{file_stamp}", abs_path)

        if self.cmbPrintType.currentIndex() == 2:   # Table html content
            html_content = str(html_content).replace("{page_content}", self.get_table_html())

        document = QTextDocument()
        document.setHtml(html_content)

        dialog = QPrintPreviewDialog()
        dialog.paintRequested.connect(document.print_)
        # dialog.paintRequested.connect(self.handlePaintRequest)
        dialog.exec_()


    def toggleGroup(self, ctrl):
        state = ctrl.isChecked()
        if state:
            ctrl.setFixedHeight(ctrl.sizeHint().height())
        else:
            ctrl.setFixedHeight(30)

    def build_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setAlignment(Qt.AlignTop)

        main_layout.addItem(self.create_delete_firma_layout())
        main_layout.addItem(self.create_firma_title_layout())
        main_layout.addItem(self.create_faktura_tip_layout())
        main_layout.addItem(self.create_insert_faktura_layout())
        main_layout.addItem(self.create_table_fakturi_layout())
        self.setLayout(main_layout)

class SmetkovotstvenaKnigaWin(QMainWindow):

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self.dict_selected_firma = {}

        self.db_api = DbLib.SmetKnigaDB(FILE_DB)

        self.insertFirma = InsertFirmaWdg()
        self.insertFirma.btnSubmit.clicked.connect(self.clicked_insertFirma_btnSubmit)


        self.smetkovotstvenaKnigaWdg = SmetkovotstvenaKnigaWdg(db_api=self.db_api, dict_firma=self.dict_selected_firma)
        self.setCentralWidget(self.smetkovotstvenaKnigaWdg)

        self.smetkovotstvenaKnigaWdg.btnRemoveFirma.clicked.connect(self.clicked_btnRemoveFirma)

        self.setWindowTitle("Сметковотствена Книга")

        self.menubar = self.menuBar()
        self.menu_firma = self.menubar.addMenu("Фирма")

        if isinstance(self.menu_firma, QMenu):
            self.submenu_firmi = self.menu_firma.addMenu("Фирми")
            self.menu_firma.addSeparator()
            self.menu_firma.addAction(QAction("Нова фирма", self, triggered=self.clicked_act_new_firma))

        self.fill_firmi()

        self.setStyleSheet(Q_STYLE)
        self.installEventFilter(self)

    def clicked_btnRemoveFirma(self):

        if self.dict_selected_firma:
            msg = "Дали сте сигурни за бришење на фирмата '{0}' ?".format(self.dict_selected_firma["ime"])
            reply = QMessageBox.question(self, "Бришење на фирма", msg)

            if reply == QMessageBox.Yes:
                if isinstance(self.db_api, DbLib.SmetKnigaDB):
                    self.db_api.remove_firma(self.dict_selected_firma["id"])
                    self.dict_selected_firma = {}

                    self.fill_firmi()
                    self.fill_other_items()

    def clicked_insertFirma_btnSubmit(self):

        if self.insertFirma.isVisible():

            firma_ime = self.insertFirma.txtIme.text()
            self.db_api.insert_firma(firma_ime)

            dict_firma_last = self.db_api.get_last_record("firma")
            self.dict_selected_firma = dict_firma_last

            self.insertFirma.clear_items()
            self.insertFirma.close()

            self.fill_firmi()
            self.fill_other_items()


    def clicked_act_new_firma(self, *args):

        if not self.insertFirma.isVisible():
            self.insertFirma.setWindowModality(Qt.ApplicationModal)
            self.insertFirma.clear_items()
            self.insertFirma.show()

    def clicked_act_change_firma(self, dict_firma={}):

        self.dict_selected_firma = dict_firma

        self.fill_other_items()


    def fill_firmi(self):

        if self.submenu_firmi and isinstance(self.submenu_firmi, QMenu):

            act_group = QActionGroup(self)
            act_group.setExclusive(True)
            self.submenu_firmi.clear()

            for dict_firma in self.db_api.get_firma():

                acr_firma = QAction(dict_firma["ime"], self, checkable=True, triggered=lambda f=self.clicked_act_change_firma, arg=dict_firma:f(arg))
                act_group.addAction(acr_firma)

                if compare_two_dict(self.dict_selected_firma, dict_firma):
                    acr_firma.setChecked(True)

                self.submenu_firmi.addAction(acr_firma)

    def fill_other_items(self):

        self.smetkovotstvenaKnigaWdg.dict_firma = self.dict_selected_firma
        self.smetkovotstvenaKnigaWdg.fill_firma_title()
        self.smetkovotstvenaKnigaWdg.fill_fakturi()

    def showEvent(self, event):

        h = 576
        w = h * 1.77
        self.resize(w, h)
        self.moveTocenter()

    def moveTocenter(self):
        # geometry of the main window
        qr = self.frameGeometry()

        # center point of screen
        cp = QDesktopWidget().availableGeometry(self).center()

        # move rectangle's center point to screen's center point
        qr.moveCenter(cp)

        # top left of rectangle becomes top left of window centering it
        self.move(qr.topLeft())

def autofill_db():
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

    for i in range(100):
        dict_kwargs = {}

        dict_kwargs["firma_id"] = 16
        dict_kwargs["reden_broj"] = i + 1
        dict_kwargs["druga_firma_id"] = 1
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

def clear_db():
    api_db = DbLib.SmetKnigaDB(FILE_DB)

    api_db.remove_all_row("faktura")
    api_db.remove_all_row("lista_na_firmi")
    api_db.remove_all_row("firma")
    pass

def main():
    app = QApplication(sys.argv)
    smetkovotstvenaKnigaWin = SmetkovotstvenaKnigaWin()
    smetkovotstvenaKnigaWin.show()
    sys.exit(app.exec_())

main()