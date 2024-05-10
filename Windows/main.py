from kivymd.app import MDApp
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.list import OneLineListItem
from kivymd.uix.list import OneLineAvatarIconListItem
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import IconLeftWidget
from kivymd.uix.list import IconRightWidget
from kivymd.uix.banner import MDBanner
from kivy.lang import Builder
from kivy.base import EventLoop
from kivy.core.window import Window
from kivy.core.window._window_sdl2 import _WindowSDL2Storage

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from time import sleep
from copy import deepcopy
import wx

gp = gspread.service_account(filename = 'immagini/chiave_accesso.json')
gsheet = gp.open('Magazzino')
wsheet = gsheet.worksheet('Foglio1')

app=wx.App(False)
width, height = wx.GetDisplaySize()
Window.maximize()
g = width/7.2 #Grandezza icone  165

tipot = ['LAVATRICE', 'LAVATRICE C-ALTO', 'ASCIUGATRICE', 'LAVASTOVIGLIE', 'LAVASTOVIGLIE INCASSO', 'FORNO', 'CUCINA GAS', 'CUCINA ELETTRICA', 'CONGELATORE', 'FRIGORIFERO', 'FRIGORIFERO INCASSO', 'CONDIZIONATORE', 'CASSE AMPLIFICATE', 'MONOPATTINO', 'BICI', 'ALTRO']
tipo = deepcopy(tipot)
tipo.sort()
marche = deepcopy(wsheet.col_values(5)[1].split(', '))
marche.sort()
#['BEKO', 'BOSCH', 'CANDY', 'DAIKIN', 'DUCATI', 'ELECTROLUX', 'HOOVER', 'HOTPOINT', 'HYUNDAI', 'INDESIT', 'LG', 'SAMSUNG', 'SMEG', 'TREVI', 'WHIRLPOOL', 'ZEPHIR']

KV = f'''
BoxLayout:
    orientation: "vertical"
    
    MDToolbar:
        id: barra
        right_action_items: [['immagini/cerca.png', lambda x: app.passa_cerca()], ['immagini/agg.png', lambda y: app.aggiungi()]]
        
    ScreenManager:
        id: sc_man
        
        Screen:
            name: 'Principale'
            MDGridLayout:
                cols: 6
                rows: 3
'''

class App(MDApp):
    scpr = ['Principale']
    diz = {}
    coordinate=None
    numer = '0'
    car = '^ì!"2'

    def build(self):
        self.title = 'App magazzino'
        self.theme_cls.theme_style = 'Light'
        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.primary_hue = "700"
        return Builder.load_string(KV)
    
    def on_start(self):
        self.aggiorna_dati()
        EventLoop.window.bind(on_keyboard=self.indietro)
        
    def indietro(self, window, key, *args):
        if key == 27 and len(self.scpr)>1:
            self.root.ids.sc_man.current = self.scpr[-2]
            del self.scpr[-1]
            return True
            
    def indie(self):
        self.root.ids.sc_man.current = self.scpr[-2]
        del self.scpr[-1]
        return True
    
    def aggiorna_dati(self):
        self.dati = deepcopy(wsheet.get_all_values())
        tot = 0
        for y in range(len(self.dati)):
            try: tot += int(self.dati[y][3])
            except: pass
        self.root.ids['barra'].title = 'Magazzino ('+str(tot)+')' 
        return(self.dati)
    
    def trova(self, ogg):
        s=0
        for y in range(len(self.dati)):
            for x in range(len(self.dati[y])):
                if self.dati[y][x] == ogg:
                    s=1
                    return([y, x])
        if s == 0:
            return(None)
    
    def colonna(self, n):
        l=[]
        for i in range(len(self.dati)):
            l.append(self.dati[i][n])
        return(l)
    
    def bottone_on(self,t):
        self.root.ids.sc_man.current = 'marche'
        self.scpr = ['Principale']
        self.scpr.append('marche')
        dati = self.dati
        #getattr(self.root.ids, t).clear_widgets()
        self.root.ids.marche.clear_widgets()
        m = []
        for i in range(len(dati)):
            ti = dati[i][0]
            ma = dati[i][1]
            if ti == t and ma not in m:
                #self.root.ids.t.add_widget(TwoLineListItem(text=dati[i+1][2], secondary_text="Quantità: "+str(dati[i+1][3])))
                m.append(ma)
                #getattr(self.root.ids, t).add_widget(TwoLineListItem(text=ma, secondary_text="Quantità: "+str(dati[i+1][3])))
                #self.root.ids.marche.add_widget(OneLineListItem(text=ma, on_press=lambda x:self.prodotti(self.root.ids.marche)))
        m.sort()
        for i in m:
            self.root.ids.marche.add_widget(OneLineListItem(text=i, on_press=lambda x, mar=i: self.prodotti(mar,t)))
                    
    def prodotti(self, marca, tipo):
        self.root.ids.sc_man.current = 'prodotti'
        self.scpr.append('prodotti')
        dati = self.dati
        self.root.ids.prodotti.clear_widgets()
        p = []
        for i in range(len(dati)):
            ti = dati[i][0]
            ma = dati[i][1]
            if ti == tipo and ma == marca:
                p.append(dati[i][2]+self.car+str(i))
        p.sort()
        for i in p:
            r = i.index(self.car)+len(self.car)
            self.root.ids.prodotti.add_widget(TwoLineListItem(text=dati[int(i[r:])][2], secondary_text="Quantità: "+str(dati[int(i[r:])][3]), on_press=lambda x, mar=dati[int(i[r:])][1], tip=dati[int(i[r:])][0], nome=dati[int(i[r:])][2], num=dati[int(i[r:])][3]: self.modifica(tip, mar, nome, num)))
                
    def modifica(self, tipo, marca, nome, numero):
        self.root.ids.sc_man.current = 'modifica'
        self.scpr.append('modifica')
        dati = self.dati
        self.coordinate = self.trova(nome)
        li=['nome', 'tipo', 'marca']
        li2=['articolo', 'tipo', 'marca']
        self.diz={'nome':nome, 'tipo':tipo, 'marca':marca, 'numero':numero}
        self.numer=numero
        #self.root.ids.modifica.add_widget(MDLabel(text=nome, halign='center', font_style='H3'))
        #self.root.ids.modifica.add_widget(MDTextField(hint_text='Modifica articolo...', mode='rectangle'))
        for i in range(3):
            self.root.ids[li[i]].text=self.diz[li[i]]
            self.root.ids[li[i]+'_m'].text= ''
            self.root.ids[li[i]+'_m'].hint_text= 'Modifica '+li2[i]
        self.root.ids['numero'].text='Numero articoli: '+self.diz['numero']
        
        #listItem = OneLineAvatarIconListItem(text="Numero articoli: "+numero)
        #listItem.add_widget(IconLeftWidget(icon='immagini/piuu.png'))
        #listItem.add_widget(IconRightWidget(icon='immagini/meno.png'))
        #self.root.ids.modifica.add_widget(listItem)
    
    def piu(self):
        self.diz['numero']=str(int(self.diz['numero'])+1)
        if self.diz['numero'] != self.numer:
            self.root.ids['numero'].text='Numero articoli('+self.numer+'): '+self.diz['numero']
        else:
            self.root.ids['numero'].text='Numero articoli: '+self.diz['numero']
        
    def meno(self):
        if int(self.diz['numero']) > 0:
            self.diz['numero']=str(int(self.diz['numero'])-1)
            if self.diz['numero'] != self.numer:
                self.root.ids['numero'].text='Numero articoli('+self.numer+'): '+self.diz['numero']
            else:
                self.root.ids['numero'].text='Numero articoli: '+self.diz['numero']
    
    def piu_n(self):
        self.diz['numero']=str(int(self.diz['numero'])+1)
        self.root.ids['numero_n'].text='Numero articoli: '+self.diz['numero']
        
    def meno_n(self):
        if int(self.diz['numero']) > 1:
            self.diz['numero']=str(int(self.diz['numero'])-1)
            self.root.ids['numero_n'].text='Numero articoli: '+self.diz['numero']
            
    def s_mod(self):
        tipo = self.root.ids['tipo_m'].text
        marca = self.root.ids['marca_m'].text
        nome = self.root.ids['nome_m'].text
        numero = self.root.ids['numero'].text[self.root.ids['numero'].text.index(':')+2:]
        self.scrivi(tipo, marca, nome.upper(), int(numero), 'm')
    
    def scrivi(self, tipo, marca, nome, numero, s):
        x=[tipo,marca,nome,numero]
        if numero == 0:
            coord_n = len(self.dati)
            for i in range(len(x)):
                #wsheet.update_cell(self.coordinate[0]+1, i+1, self.dati[coord_n-1][i])
                #wsheet.update_cell(coord_n, i+1, '')
                pass
        elif s == 'm':
            for i in range(len(x)):
                if x[i] != '':
                    #wsheet.update_cell(self.coordinate[0]+1, i+1, x[i])
                    pass
        elif s == 'a':
            #wsheet.append_row([tipo, marca, nome.upper(), int(numero)])
            #for i in range(len(x)):
            #    wsheet.update_cell(len(wsheet.get_all_values())+1, i+1, x[i])
            pass
        self.root.ids.sc_man.current = 'Principale'
        if s == 'm':
            self.scpr.append('Principale')
        elif s == 'a':
            self.scpr = ['Principale']
        self.aggiorna_dati()
    
    def passa_cerca(self):
        self.root.ids.sc_man.current = 'cerca'
        self.scpr.append('cerca')
        
    def cerca(self):
        self.root.ids.cerca_l.clear_widgets()
        c = self.root.ids['testo_cerca'].text.upper()
        s = 0
        l = []
        for no in self.colonna(2):
            if c == no.upper()[:len(c)] and no.upper() != 'ARTICOLO':
                s = 1
                l.append(no)
        l.sort()
        for no in l:
            self.coordinate = self.trova(no)
            ti = self.dati[self.coordinate[0]][0]
            ma = self.dati[self.coordinate[0]][1]
            nu = self.dati[self.coordinate[0]][3]
            self.root.ids.cerca_l.add_widget(TwoLineListItem(text=no, secondary_text="Quantità: "+nu, on_press=lambda x, mar=ma, tip=ti, nome=no, num=nu: self.modifica(tip, mar, nome, num)))
        if s == 0:
            self.root.ids.cerca_l.add_widget(OneLineListItem(text='Nessun risultato trovato'))
                
    def aggiungi(self):
        self.diz = {'numero':'1', 'marca':'', 'nome':'', 'tipo':''}
        self.root.ids.sc_man.current = 'aggiungi'
        self.scpr.append('aggiungi')
        for i in ['nome', 'marca', 'tipo']:
            self.root.ids[i+'_m_n'].text = ''
            self.root.ids[i+'_m_n'].hint_text = ''
        self.root.ids['numero_n'].text = 'Numero articoli: 1'
        
    def riscrivi(self, ogg, par):
        del self.scpr[-1]
        ag='_n'
        sc='aggiungi'
        if '2' in ogg:
            ogg = ogg[:-1]
            ag=''
            sc='modifica'
        self.diz[ogg] = par
        self.root.ids.sc_man.current = sc
        self.root.ids['nome_m'+ag].text = self.diz['nome']
        self.root.ids['marca_m'+ag].text = self.diz['marca']
        self.root.ids['tipo_m'+ag].text = self.diz['tipo']
        if self.diz['numero'] != self.numer and ag == '':
            self.root.ids['numero'+ag].text = 'Numero articoli('+self.numer+'): '+self.diz['numero']
        else:
            self.root.ids['numero'+ag].text = 'Numero articoli: '+self.diz['numero']
        
    def scegli(self, ogg):
        ag='_n'
        if '2' in ogg:
            ag=''
            ogg=ogg[:-1]
        self.diz['nome'] = self.root.ids['nome_m'+ag].text
        self.diz['numero'] = self.root.ids['numero'+ag].text[self.root.ids['numero'+ag].text.index(':')+2:]
        if ogg == 'tipo':
            self.diz['marca'] = self.root.ids['marca_m'+ag].text
        if ogg == 'marca':
            self.diz['tipo'] = self.root.ids['tipo_m'+ag].text
        self.root.ids.sc_man.current = 'sc_'+ogg+ag
        self.scpr.append('sc_'+ogg+ag)
            
    def controllo(self, mode):
        s=0
        if mode == 'a':
            for i in ['nome', 'marca', 'tipo']:
                if self.root.ids[i+'_m_n'].text == '':
                    s=1
                    self.root.ids[i+'_m_n'].hint_text = 'Questo campo non può essere lasciato vuoto'
                else:
                    self.diz[i] = self.root.ids[i+'_m_n'].text
            if self.root.ids['nome_m_n'].text != '':
                x=self.trova(self.root.ids['nome_m_n'].text.upper())
                if x != None:
                    self.root.ids['nome_m_n'].hint_text = 'Nome articolo già in uso'
                    s=1
            if s == 0:
                self.scrivi(self.diz['tipo'], self.diz['marca'], self.diz['nome'], self.diz['numero'], 'a')
        if mode == 'm':
            if self.root.ids['nome_m'].text != '':
                x=self.trova(self.root.ids['nome_m'].text.upper())
                if x != None:
                    self.root.ids['nome_m'].hint_text = 'Nome articolo già in uso'
                    s=1
            if s == 0:
                self.s_mod()

def forma_modello(KV):
    for i in tipot:
        KV+=f'''
                MDIconButton:
                    id: "{i}"
                    icon: "immagini/{i}.png"
                    user_font_size: {g}
                    on_press: app.bottone_on('{i}')
'''

    KV+='''
        Screen:
            name: 'marche'
            ScrollView:
                MDList:
                    id: marche
        Screen:
            name: 'prodotti'
            ScrollView:
                MDList:
                    id: prodotti
        Screen:
            name: 'modifica'
            MDGridLayout:
                id: modifica
                cols: 1
                rows: 8
                MDLabel:
                    id: nome
                    halign: 'center'
                    font_style: 'H3'
                MDTextField:
                    id: nome_m
                    halign: 'center'
                    font_style: 'H3'
                    mode: 'rectangle'
'''
    for i in ['marca', 'tipo']:
        KV+=f'''                
                MDLabel:
                    id: {i}
                    halign: 'center'
                    font_style: 'H3'
                MDTextField:
                    id: {i}_m
                    halign: 'center'
                    font_style: 'H3'
                    mode: 'rectangle'
                    on_focus: if self.focus: app.scegli('{i}2')
'''
    KV+='''
                OneLineAvatarIconListItem:
                    id: numero
                    IconRightWidget:
                        icon: 'immagini/piuu.png'
                        on_press: app.piu()
                    IconLeftWidget:
                        icon: 'immagini/meno.png'
                        on_press: app.meno()
                MDGridLayout:
                    cols: 3
                    rows:1
                    MDRaisedButton:
                        text: 'ANNULLA'
                        helign: 'center'
                        on_release: app.indie()
                    MDLabel:
                        text: ''
                    MDRaisedButton:
                        text: 'CONFERMA'
                        helign: 'center'
                        on_release: app.controllo('m')    
        
        Screen:
            name: 'aggiungi'
            MDGridLayout:
                id: aggiungi
                cols: 1
                rows: 8
                MDLabel:
                    id: nome_n
                    text: 'Articolo'
                    halign: 'center'
                    font_style: 'H3'
                MDTextField:
                    id: nome_m_n
                    halign: 'center'
                    font_style: 'H3'
                    mode: 'rectangle'
'''
    for i in ['marca', 'tipo']:
        a = i[0].upper()+i[1:]
        KV+=f'''                
                MDLabel:
                    id: {i}_n
                    text: '{a}'
                    halign: 'center'
                    font_style: 'H3'
                MDTextField:
                    id: {i}_m_n
                    halign: 'center'
                    font_style: 'H3'
                    mode: 'rectangle'
                    on_focus: if self.focus: app.scegli('{i}')
'''
    KV+='''
                OneLineAvatarIconListItem:
                    id: numero_n
                    IconRightWidget:
                        icon: 'immagini/piuu.png'
                        on_press: app.piu_n()
                    IconLeftWidget:
                        icon: 'immagini/meno.png'
                        on_press: app.meno_n()
                MDGridLayout:
                    cols: 3
                    rows: 1
                    MDRaisedButton:
                        text: 'ANNULLA'
                        helign: 'center'
                        on_release: app.indie()
                    MDLabel:
                        text: ''
                    MDRaisedButton:
                        text: 'CONFERMA'
                        helign: 'center'
                        on_release: app.controllo('a')
'''
    for q in ['', '_n']:
        s=''
        if q == '':
            s='2'
        for p in ['tipo', 'marca']:
            KV+=f'''     
        Screen:
            name: 'sc_{p+q}'
            MDGridLayout:
                rows: 1
                cols: 1
                ScrollView:
                    MDList:
'''
            if p == 'tipo':
                for i in tipo:
                    KV+=f'''
                        OneLineListItem:
                            text: '{i}'
                            on_press: app.riscrivi('{p+s}', '{i}')
'''
            if p == 'marca':
                for i in marche:
                    KV+=f'''
                        OneLineListItem:
                            text: '{i}'
                            on_press: app.riscrivi('{p+s}', '{i}')
'''


    KV+='''         
        Screen:
            name: 'cerca'
            MDGridLayout:
                cols: 1
                rows: 3
                MDTextFieldRound:
                    id: testo_cerca
                    hint_text: 'Cerca il prodotto...'
                MDRaisedButton:
                    text: "CERCA"
                    size_hint_x: 0.1
                    md_bg_color: 0,0,1,0.8
                    on_press: app.cerca()
                ScrollView:
                    MDList:
                        id: cerca_l
'''
    return(KV)

KV = forma_modello(KV)
App().run()
