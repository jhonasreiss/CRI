import os, sys
import requests
import copy
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QGridLayout, QPushButton, QLabel, QGroupBox, QScrollArea,
                             QMessageBox, QTableWidget, QTableWidgetItem, QSpacerItem, 
                             QSizePolicy, QFileDialog, QDialog)
from PIL import Image
from io import BytesIO

class ScrapingData(QMainWindow):
    def __init__(self):
        super().__init__()
        os.system('cls')
        self.set_init()
        self.scraping_table()
        self.design_widget()
        
    
    def set_init(self):
        self.setWindowTitle('Check-In de Imposto 2024')
        self.setFixedSize(1000,600)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_layout = QGridLayout()
        self.central_widget.setLayout(self.central_layout)

    def design_widget(self):
        scroll_area = QScrollArea()
        scroll_widget = QWidget(scroll_area)
        layout_scroll = QVBoxLayout(scroll_widget)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        slot_1, self.slot_2 = [],[]
        get_num_slot1 = []        
        for i in range(self.data.__len__()):
            if i > 0:
                self.list_1, list_2 = self.data[i][0], self.data[i][1]
                #slot_1 Dê
                split_loc = self.list_1.split('Até ')
                for i in split_loc:
                    rem_d = i.split('De ')
                    for c in rem_d:
                        rem_d_2 = c.split('Acima de ')
                        for c2 in rem_d_2:
                            rem_d_3 = c2.split('R$ ')
                            for values in rem_d_3:
                                final_value = values.split(' até ')
                                for n in final_value:
                                    if n != '':
                                        get_num_slot1.append(n)
                
                #slot_2 (%)
                get_num_slot2 = list_2.split('%')
                get_num_slot2.pop()
                converter_num_slot_2 = get_num_slot2[0].replace(',','.')
                self.slot_2.append(float(converter_num_slot_2))
        
        
        for i in range(len(get_num_slot1)):
        # Verificar se há um ponto no elemento atual
            if '.' in get_num_slot1[i]:
            # Remover o ponto e atualizar o elemento na lista
                get_num_slot1[i] = get_num_slot1[i].replace('.', '')
                get_num_slot1[i] = get_num_slot1[i].replace(',', '.')
        
        self.tabela_imposto = copy.deepcopy(get_num_slot1)     
        
        fig, ax = plt.subplots()
        labels = ['até R$2.259','2.259,21 / 2.828,65','2.828,66 / 3.751,05','3.751,06 / 4.664,68','Acima de R$4.664,68']
        values = self.slot_2
        ax.bar(labels, values)
        ax.set_title('Comparação de Alíquota')
        ax.set_xlabel('Salários')
        ax.set_ylabel('Imposto %')

        ax.set_xticklabels(labels, fontsize=6)

        canvas = FigureCanvas(fig)

        buffer = BytesIO()
        fig.savefig(buffer, format='png')
        buffer.seek(0)

        # Converter a imagem em QPixmap
        image = Image.open(buffer)
        qimage = image.convert("RGBA").toqpixmap()

        # Criar um QLabel para exibir a imagem
        label = QLabel()
        label.setPixmap(qimage)

        self.data.pop(0)
        num_rows = len(self.data)
        num_cols = len(self.data[0])

        tabela_view = QTableWidget(num_rows,num_cols)
        tabela_view.setColumnWidth(0,250)
        tabela_view.setColumnWidth(1,170)
        tabela_view.setColumnWidth(2,206)
        tabela_view.resizeRowsToContents()
        tabela_view.setFixedHeight(146)

        layout_scroll.addWidget(tabela_view)
        tabela_view.setHorizontalHeaderLabels(['Salário base de Cálculo','Alíquota %','Parcela em R$ IR'])
        layout_scroll.addWidget(label)


        
        for row, rowData in enumerate(self.data):
            for col, val in enumerate(rowData):
                item = QTableWidgetItem(str(val))
                tabela_view.setItem(row, col, item)
        

        group_space = [QGroupBox() for i in range(2)]
        group_import = QGroupBox()
        layout_group = [QVBoxLayout() for i in range(2)]
        layout_import = QVBoxLayout()
        group_import.setLayout(layout_import)
        group_import.setTitle('Importar')
        list_name_title = ['Gráfico','Exportar']
        button_export = [QPushButton() for i in range(2)]
        button_import = QPushButton('.XLSX')
        button_import.setFixedHeight(80)
        list_button_name = ['.CSV','.XLSX']

        group_space[0].setFixedWidth(700)
        layout_import.addWidget(button_import)

        for i in range(2):
            button_export[i].setText(list_button_name[i])
            button_export[i].setFixedHeight(80)
            group_space[i].setLayout(layout_group[i])
            group_space[i].setTitle(list_name_title[i])
            layout_group[0].addWidget(scroll_area)
            layout_group[1].addWidget(button_export[i])
        
        self.central_layout.addWidget(group_space[0],1,1,2,1)
        self.central_layout.addWidget(group_space[1],1,2,1,1)
        self.central_layout.addWidget(group_import,2,2,1,1)

        button_export[0].clicked.connect(lambda: self.load_sheet(1))
        button_export[1].clicked.connect(lambda: self.load_sheet(0))
        button_import.clicked.connect(lambda: self.select_file(0))

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout_group[1].addItem(spacer)


    def scraping_table(self):
        url = 'https://g1.globo.com/ro/nova-tabela-do-imposto-de-renda-deducao-valor-a-declarar-em-2024.ghtml'
        response = requests.get(url)
        raw_html = response.text
        html_parser = BeautifulSoup(raw_html,'html.parser')
        
        tabela = html_parser.find('table')
        if tabela:
            self.data = []
            for linha in tabela.find_all('tr'):
                col = linha.find_all(['th','td'])
                row_data = []
                for row in col:
                    row_data.append(row.text.strip())
                self.data.append(row_data)
        else:
            print("Não foi possível coletar os dados da tabela!")
        

    def select_file(self, index):
        file_option = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Abrir Arquivo", "", "Todos os Arquivos (*);;Arquivos de Texto (*.txt)", options=file_option)
        self.load_sheet_imported(file_name)

    def load_sheet_imported(self, path_file):
        self.planilha = pd.read_excel(path_file)
        labels_title_list = self.planilha.columns.tolist()

        self.select_column = QDialog()
        self.select_column.setFixedSize(400,80)
        self.select_column.setWindowTitle('Escolha a coluna')

        scroll_column = QScrollArea()
        widget_column = QWidget(scroll_column)
        layout_column = QHBoxLayout(widget_column)
        scroll_column.setWidget(widget_column)
        scroll_column.setWidgetResizable(True)

        central_layout = QHBoxLayout()
        self.select_column.setLayout(central_layout)
        button_column = [QPushButton() for i in range(labels_title_list.__len__())]

        central_layout.addWidget(scroll_column)
        
        for i in range(button_column.__len__()):
            column_name = labels_title_list[i]
            button_column[i].setText(column_name)
            button_column[i].clicked.connect(lambda  checked=None, name=column_name: self.choose_column(name))
            layout_column.addWidget(button_column[i])

        self.select_column.exec()

    def choose_column(self, name_column):
        self.name_c = name_column
        self.select_column.close()

    def load_sheet(self, index): 
        recalcular = self.planilha[self.name_c]
        novo_valor = []
        imposto_d = []
        for i in recalcular:
            if float(i) < float(self.tabela_imposto[0]):
                novo_valor.append(round(i - (float(i) * float(self.slot_2[0])/100)))
                imposto_d.append(self.slot_2[0])

            elif float(i) >= float(self.tabela_imposto[1]) and float(i) < float(self.tabela_imposto[2]):
                novo_valor.append(round(i - (float(i) * float(self.slot_2[1])/100)))
                imposto_d.append(self.slot_2[1])

            elif float(i) >= float(self.tabela_imposto[3]) and float(i) < float(self.tabela_imposto[4]):
                novo_valor.append(round(i - (float(i) * float(self.slot_2[2])/100)))
                imposto_d.append(self.slot_2[2])

            elif float(i) >= float(self.tabela_imposto[5]) and float(i) <= float(self.tabela_imposto[6]):
                novo_valor.append(round(i - (float(i) * float(self.slot_2[3])/100)))
                imposto_d.append(self.slot_2[3])

            elif float(i) > float(self.tabela_imposto[7]):
                novo_valor.append(round(i - (float(i) * float(self.slot_2[4])/100)))
                imposto_d.append(self.slot_2[4])

        self.planilha['Imposto Descontado'] = imposto_d
        self.planilha['Reajuste'] = novo_valor

        try:
            if os.path.exists('exported'):
                if index == 0:
                    self.planilha.to_excel('exported/reajuste_de_salario.xlsx', index=False)
                if index == 1:
                    self.planilha.to_csv('exported/reajuste_de_salario.csv', index=False)
                self.message_window('Finalizado','Seu arquivo foi exportado com sucesso!')
                print('Exportado com sucesso!')
            else:
                os.makedirs('exported')
                if index == 0:
                    self.planilha.to_excel('exported/reajuste_de_salario.xlsx', index=False)
                if index == 1:
                    self.planilha.to_csv('exported/reajuste_de_salario.csv', index=False)
                self.message_window('Falha','Houve uma falha ao exportar seu arquivo!')
        except:
            print('não foi possível exportar o arquivo!')

    def import_file(self):
        pass

    def message_window(self,title_msn, msn, space=10):
        mensagem = QMessageBox(self)
        mensagem.setText(msn)
        mensagem.setContentsMargins(0,0,30,0)
        mensagem.setWindowTitle(title_msn)
        mensagem.setFixedSize(200,50)
        mensagem.exec()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ScrapingData()
    window.show()
    sys.exit(app.exec())