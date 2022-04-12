# con questa versione provo a importare i dati da un json
from ast import Index
from datetime import date
import datetime
import os
import math
import json
from turtle import radians
from flask import Flask, render_template, json, request, make_response, send_from_directory
from fpdf import FPDF
from datetime import date
from ast import literal_eval






from flask import url_for



app = Flask(__name__)          
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['STATIC_URL_PATH'] = ''
app.config['STATIC_FOLDER'] = 'static'


SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_inserti_url = os.path.join(SITE_ROOT, "static/data", "inserti.json")
json_ugelli_url = os.path.join(SITE_ROOT, "static/data", "ugelli.json")
print(json_inserti_url)
print(json_ugelli_url)
# Python program to read
# json file

# Opening JSON file
f_i = open(json_inserti_url)

# returns JSON object as 
# a dictionary
inserti = json.load(f_i)

f_i.close()
# Opening JSON file
f_u = open(json_ugelli_url)

# returns JSON object as 
# a dictionary
ugelli = json.load(f_u)

# Closing file
f_u.close()



risultato = {
        "portata_effettiva_lpm": 0.0,
        "portata_in_eccesso_lpm": 0.0,
        "portata_ottimale_lpm": 0.0,
        "portata_ricircolo_lpm": 0.0,
        "perdita_pressione_bar": 0.0,
        "pressione_ugello_bar": 0.0,
        "diametro_calcolato_getti_spinta": 0.0,
        "portata_effettiva_getti_spinta": 0.0,
        "diametro-inserti-1": 0.0,
        "diametro-inserti-2": 0.0,
        "portata-1": 0.0,
        "portata-2": 0.0,
        "errore": 0,
        "fattore-di-portata": 0.0,
        "area_equivalente": 0.0,
        "spinta_kg": 0.0

}

inserto_nullo = {
                    "Tipo": "N/D",
                    "Materiale": "N/D",
                    "Orifizio (mm)": "0",
                    "Codice": "N/D",
                    "Descrizione": "N/D"
}

coefficienti_di_flusso = {
    "TEI-M4": 0.6,
    "TEI-M6": 0.6,
    "TEI-M6C": 0.9,
    "TEI-M8C": 0.8,
    "TEI-M10C": 0.9,
    "TEI-M10x1C": 0.9,
    "M12C": 0.9,
    "TEE-M6C": 0.9,
    "TEE-M10x1C": 0.9,
    "TEE-1/4C": 0.9,
    "TEE-M6W": 0.7,
    "TEE-M10x1W": 0.75,
    "Forati": 0.5 
}

            
def calcola_perdita_pressione(tubo, portata):
    perdita = 0.0
    if tubo["lunghezza"]:
        perdita = 288 * float(tubo["materiale"]["coefficiente"]) * float(tubo["lunghezza"]) * pow(float(portata), 2) / pow(float(tubo["diametro"]),5) / pow(math.pi,2)
        print(float(tubo["materiale"]["coefficiente"]))
        print("lunghezza: ", float(tubo["lunghezza"]))
        print ("diametro: ", float(tubo["diametro"]))
        print("portata: ", portata)
        print("perdita: ", perdita)
    return perdita

def calcola_diametro_ideale_obsoleto(portata, pressione, getti):
        num_getti = float(getti)
        
        speed = calcola_speed(pressione)
        if speed == 0:
            return 0.0
        return  2000.0 * math.sqrt(portata / (60000.0 * num_getti * math.pi * speed))

def calcola_diametro_ideale(portata, pressione, getti, tipo):
        print("CALCOLO DIAMETRO IDEALE!!!!")
        print("num getti: ", getti)
        print("pressione: ", pressione)
        print("portata: ", portata)
        
        num_getti = float(getti)
        
        speed = calcola_speed(pressione)
        if speed == 0:
            return 0.0
        return  2000.0 * math.sqrt(portata / (60000.0 * num_getti * coefficienti_di_flusso[tipo] * math.pi * speed))


def calcola_portata_ottimale(pressione_pompa, tubo):
    denominatore = 2 * float(tubo["materiale"]["coefficiente"]) * float(tubo["lunghezza"]) * 288 / pow(float(tubo["diametro"]),5)
    return math.sqrt(float(pressione_pompa) * pow(math.pi, 2) / denominatore )

def calcola_portata(perdita_pressione, tubo):
    print("perdita pressione: ", perdita_pressione)
    print("tubo[diametro]: ", tubo["diametro"])
    print("tubo[lunghezza]: ", tubo["lunghezza"])
    print("tubo['materiale']['coefficiente']: ", tubo["materiale"]["coefficiente"])
    return math.sqrt(float(perdita_pressione)*pow(float(tubo["diametro"]),5)*pow(math.pi,2)/(288*float(tubo["lunghezza"])*float(tubo["materiale"]["coefficiente"])))

def calcola_portata_gruppo(inserto, pressione, ugello, getti):
    print("type of num_getti: ", type(ugello["Nr. getti"]))
    print("type of getti: ", type(getti))
    speed = calcola_speed(pressione)
    print("type of inserto = ", type(inserto))
    if inserto:
        diametro = float(inserto["Orifizio (mm)"])
        return 60000.0 * float(getti) * float(speed) * float(math.pi) * pow(0.001 * float(diametro),2) / 4
    else:
        return 0.0

def calcola_spinta(pressione,portata,num_fori, gradi):
    print('calcolo della spinta: ')
    print('pressione: ', pressione, ', portata: ', portata, ", num_fori: ", num_fori, ", gradi: ", gradi)
    return 0.0228*math.sqrt(float(pressione))*float(portata)*int(num_fori)*math.cos(math.radians(float(gradi)))

def new_func(pressione):
    print("type of pressione: ", type(pressione))

def calcola_speed(pressione):
    print("type of pressione", type(pressione))
    if float(pressione) <= 0:
        return 0.0
    return 0.0408429411 * math.sqrt(100000.0 * float(pressione))

def controlla_tipo(inserto, tipo):
    if inserto:
        return inserto["Tipo"] == tipo
    else:   
        return "None"
def get_inserto_gruppo(diametro_calcolato, myNozzle):
    inserti_filtrati = list(filter(lambda x: controlla_tipo(x, myNozzle["Tipo getti"]), inserti["inserti"]))
    print(inserti_filtrati)
    inserto_minimo = inserti_filtrati[0]
    print("INSERTI FILTRATI: ", inserti_filtrati)
    print("inserto minimo", inserto_minimo)
    print("diametro calcolato: ", diametro_calcolato)
    if float(inserto_minimo["Orifizio (mm)"]) > diametro_calcolato:
        return inserto_nullo

    for i in inserti_filtrati:
        if float(i["Orifizio (mm)"]) > diametro_calcolato:
            index = inserti_filtrati.index(i)
            i_gruppo = inserti_filtrati[index-1]
          
            return i_gruppo
    return inserto_nullo

def calcola_area_equivalente(portata, speed):
    return 1000000/60*float(portata)/float(speed)/1000

def calcola_fattore_di_portata(portata,pressione):
    print("calcolo fattore di portata:")
    print("portata: ", portata)
    print("pressione: ", pressione)
    return float(portata)/22.8/math.sqrt(float(pressione))


@app.route("/", methods = ['GET', 'POST'])
def docon():
    return render_template("docon.html")


@app.route("/step1", methods = ['GET', 'POST'])
def step1():
    portata = 0.0
    
    portata_rimanente = []
    
    global perdita_pressione 
    perdita_pressione = 0.0

    etichetta_materiale = None

    
    if (request.method == 'POST'):
        entry_content = request.form.to_dict()
        print(entry_content)
        print("Type of entry_content: ", type(entry_content))
        print("Type of risultato: %s", type(risultato))

        print("SONO ENTRATO nella funzione step1")
            
        global tubo 
        if entry_content["materiale-tubo"] == "1.2517":
            etichetta_materiale = "Gomma"
        elif entry_content["materiale-tubo"] == "1.0013":
            etichetta_materiale = "Termoplastico"
        tubo = {"diametro": entry_content["diametro-tubo"], "lunghezza": entry_content["lunghezza-tubo"],
                "materiale": {"coefficiente": entry_content["materiale-tubo"] ,
                             "etichetta": etichetta_materiale} }   
    
        global dati 
        dati = {"azienda": entry_content["azienda"], "nominativo": entry_content["nominativo"], "note": entry_content["note"],
                "pressione_bar": entry_content["pressione"], "portata_lpm": entry_content["portata"], "ugello": None,
                "applicazione": entry_content["applicazione"], "tubo": tubo}
        
            
        # Se si considera la prssione netta all'ugello si 
        # ipotizza che non ci siano perdite di pressione distribuite lungo il tubo
        # La pressione è indipendente dalla portata
        # La semplificazione consiste nell'assumere che la portata e la pressione sono indipendenti 
        # dall'altra. Questo non ha significato fisico

        portata_ottimale = 0.0

        # COEFFICIENTI PRESI A CASO.
        
        if dati["applicazione"] == "Lavaggio":
            portata_ottimale = float(dati["portata_lpm"])
            perdita_pressione = calcola_perdita_pressione(tubo,portata_ottimale)
            if perdita_pressione > 0.4 * float(dati["pressione_bar"]):
                pressione_ugello_bar = 0.6 * float(dati["pressione_bar"])
                perdita_pressione = float(dati["pressione_bar"]) - pressione_ugello_bar
                portata_ottimale = calcola_portata(perdita_pressione, tubo)
            if portata_ottimale < 0.5 * float(dati["portata_lpm"]):
                risultato["errore"] = 998
        elif dati["applicazione"] == "Sfondamento":
            portata_ottimale = 0.2 * float(dati["portata_lpm"])
            perdita_pressione = calcola_perdita_pressione(tubo, portata_ottimale)
            if perdita_pressione >= 0.7 * float(dati["pressione_bar"]):
                risultato["errore"] = 999
        elif dati["applicazione"] == "Tagliaradici":
            portata_ottimale = 0.3 * float(dati["portata_lpm"])
            perdita_pressione = calcola_perdita_pressione(tubo, portata_ottimale)
            if perdita_pressione >= 0.8 * float(dati["pressione_bar"]):
                risultato["errore"] = 999
        elif dati["applicazione"] == "Dissabbiatori":    
            print("calcolo la portata ottimale e le perdite di pressione")
            print("dati[pressione_bar] ", dati["pressione_bar"])
            portata_ottimale = calcola_portata_ottimale(dati["pressione_bar"],tubo)
            if portata_ottimale > float(dati["portata_lpm"]):
                portata_ottimale = float(dati["portata_lpm"])       
            perdita_pressione = calcola_perdita_pressione(tubo, float(portata_ottimale))
            if perdita_pressione >= 0.8 * float(dati["pressione_bar"]):
                risultato["errore"] = 999
       
        print("perdita di pressione: ", perdita_pressione)
        # perdita_totale = 0.0        
        # for perdita_i in perdite_pressione:
        #     perdita_totale += perdita_i
        pressione_ugello_bar = float(dati["pressione_bar"]) - perdita_pressione
        speed = float(calcola_speed(pressione_ugello_bar))

        portata_rimanente.append(float(portata))
        print("portata_rimanente[0]", portata_rimanente[0])
        
        portata_ricircolo = float(dati["portata_lpm"]) - float(portata_ottimale)
        
        risultato["portata_ottimale_lpm"] = "{:5.1f}".format(portata_ottimale)    
        risultato["perdita_pressione_bar"] = "{:5.1f}".format(perdita_pressione) 
        risultato["portata_ricircolo_lpm"] = "{:5.1f}".format(portata_ricircolo) 
        risultato["fattore-di-portata"] = "{:5.2f}".format(calcola_fattore_di_portata(portata_ottimale, pressione_ugello_bar))    
        risultato["area_equivalente"] = "{:5.2f}".format(calcola_area_equivalente(portata_ottimale, speed))    
        risultato["pressione_ugello_bar"] = "{:5.2f}".format(float(dati["pressione_bar"]) - perdita_pressione)
        risultato["speed"] = "{:5.2f}".format(calcola_speed(float(risultato["pressione_ugello_bar"])))
        
        
        
        # GESTIONE DEGLI ERRORI
        risultato["errore"] = 0
        if float(risultato["perdita_pressione_bar"]) >= 0.8 * float(dati["pressione_bar"]):
            risultato["errore"] = 999
        
    print('perdita_pressione: ', perdita_pressione)
    print('portata_ottimale: ', portata_ottimale)
    print('tubo', tubo)
    print('perdita_totale', perdita_pressione)
    print('dati["pressione_bar"]', dati["pressione_bar"])
    print('pressione-ugello-bar', pressione_ugello_bar)

    return render_template("docon1.html", dati = dati, 
                            ugelli = ugelli["ugelli"],
                            risultato = risultato, 
                            tubo = tubo
                            )

# https://stackoverflow.com/questions/11556958/sending-data-from-html-form-to-a-python-script-in-flask

@app.route("/step2", methods = ['GET', 'POST'])
def step2():
    
    global tubo 
    global gruppo
    global dati 
    global risultato
    
    
    print("Sono entrato nella funzione step2")
  
    if request.method == 'POST':
        entry_content = request.form.to_dict()
        print(entry_content)
        # print("Type of entry_content: ", type(entry_content))
        # print("Type of risultato: %s", type(risultato))
        print("type of entry_content: ", type(entry_content))
        print("tubo: ", entry_content["tubo"])
        print("dati: ", entry_content["dati"])
        print("risultato: ", entry_content["risultato"])
        

        tubo = literal_eval(entry_content["tubo"])
        dati = literal_eval(entry_content["dati"])
        risultato = literal_eval(entry_content["risultato"])
        #print("risultato: ", risultato)
        gruppo = {
            'tipo-gruppo-1': 'Forati',
            'num-getti-1': entry_content['num-getti-1'],
            'portata-percentuale-1': entry_content['portata-percentuale-1'],
            'gradi-1': entry_content['gradi-1'],
            'foro-calcolato-1': 0.0,
            'foro-scelto-1': '',
            'portata-1': entry_content['portata-1'], 
            'spinta_kg': 0.0 
        }

        print('gruppo: ', gruppo)
        print('risultato: ', risultato)
        print('type of risultato :', type(risultato))

        perc_1 = gruppo["portata-percentuale-1"]
        print("percentuale 1: ", perc_1)
        portata_ottimale_lpm = risultato["portata_ottimale_lpm"]
        print("portata ottimale lpm: ", portata_ottimale_lpm)
        q_1 = float(perc_1)/100*float(portata_ottimale_lpm)
        v_1 = float(risultato["speed"])
        area_eq_1 = calcola_area_equivalente(q_1,v_1)
        p = float(risultato["pressione_ugello_bar"])
        d_1 = calcola_diametro_ideale(q_1, p, int(gruppo["num-getti-1"]), gruppo["tipo-gruppo-1"])
        

        gruppo['area-equivalente-1'] = "{:5.2f}".format(area_eq_1)
        
        gruppo["foro-calcolato-1"] = "{:5.1f}".format(d_1)
            
        

        # GESTIONE DEGLI ERRORI
        
        # risultato["errore"] = 0
        # if float(risultato["perdita_pressione_bar"]) >= 0.8 * float(dati["pressione_bar"]):
        #     risultato["errore"] = 999
        # elif inserti_taratura[1] == inserto_nullo or inserti_taratura[2] == inserto_nullo:
        #     risultato["errore"] = 998  
        # elif myNozzle == None:
        #     risultato["errore"] = 997
        # elif myNozzle["Famiglia"] == "Raut" and  inserti_taratura[0] == inserto_nullo:
        #     risultato["errore"] = 996



    return render_template("docon2.html", inserti = inserti["inserti"], dati = dati, tubo = tubo, risultato = risultato, gruppo = gruppo)



# @app.route("/step3", methods = ['GET', 'POST'])
# def step3():

#     if request.method == 'POST':
#         entry_content = request.form.to_dict()
#         print(entry_content)
#         dati = entry_content("dati")
#         risultato = entry_content("risultato")
#         i = 1
#         gruppi = []
#         while entry_content("sel-tipo-gruppo -" + i):
#             gruppi[i-1] = {
#                 "tipo-" + i : entry_content("sel-tipo-gruppo -" + i), 
#                 "num-getti-" + i : entry_content("num-getti-" + i),
#                 "portata-percentuale-" + i : entry_content("portata-percentuale-" + i),
#                 "gradi-" + i : entry_content("gradi-" + i),
#                 "foro-calcolato-" + i : entry_content("foro-calcolato-" + i),
#                 "foro-scelto-" + i : entry_content("foro-scelto-" + i),
#                 "portata-gruppo-" + i : entry_content("portata-gruppo-" + i),
#             }
#             i += 1

#     # print_pdf(dati, myNozzle, portata_gruppo, inserti_taratura, perdita_pressione, tubo, gruppi)
#     return render_template("docon3.html", inserti = inserti["inserti"], dati = dati, risultato = risultato, gruppi = gruppi)

@app.route("/step3", methods = ['GET', 'POST'])
def step3():

    global tubo 
      
    global dati
     
    global gruppo
    

    print("Sono entrato nella funzione step3")
  
    if request.method == 'POST':
        entry_content = request.form.to_dict()
        print(entry_content)
        # print("Type of entry_content: ", type(entry_content))
        # print("Type of risultato: %s", type(risultato))

        tubo = literal_eval(entry_content["tubo"])
        dati = literal_eval(entry_content["dati"])
        risultato = literal_eval(entry_content["risultato"])
        spinta_kg = calcola_spinta(risultato["pressione_ugello_bar"], risultato["portata_ottimale_lpm"], gruppo["num-getti-1"], gruppo["gradi-1"])
        gruppo = literal_eval(entry_content["gruppo"])
        gruppo["spinta_kg"] = "{:5.2f}".format(spinta_kg)
        gruppo["foro-scelto-1"] = entry_content["foro-scelto-1"]

    return render_template("docon3.html", dati = dati, risultato = risultato, gruppo = gruppo)

@app.route("/reset", methods = ['GET', 'POST'])

def reset():
    global perdita_pressione
    perdita_pressione = []
    global dati 
    dati = {}
    global tubo 
    tubo = []

    return render_template("docon.html")


def print_pdf(dati, myNozzle, portata_gruppo, inserti_taratura, perdita_pressione, tubo, gruppi):
    
    print("sto generando un pdf")
    print("perdita_pressione: ", perdita_pressione)
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()  
    pdf.set_left_margin(15)
    pdf.set_auto_page_break(True, 0)

        
    pdf.image("static/images/logo-nct.jpg", x = 15, y = 5,  w = 25, h = 11, type='jpg')
    
    pdf.set_y(10)
           
    # Select Arial bold 15
    pdf.set_font('Arial', 'B', 28)
    # Framed title
    pdf.cell(180, 10, 'DOCON', 0, 1, 'R')
    pdf.set_font('Arial', '', 15)
    pdf.cell(180, 10, 'Rapporto di calibrazione ugelli', 0, 1, 'R')
            
    # Line break
    pdf.ln(20)
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(40, 10, myNozzle["Codice"], 0, 1, 'L')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 12)
    pdf.cell(40, 10, myNozzle["Descrizione estesa"], 0, 1, 'L')

    pdf.set_y(50)
    pdf.cell(150)
    pdf.image(name = "static/images/" + myNozzle["Codice"] + ".jpg", x = 140, y = 50, w = 60, h = 60, type = 'jpg', link = '')

    pdf.set_y(120)
    pdf.set_text_color(0, 0, 255)
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(40, 5, "Capacità pompa", 0, 1, 'L')
    pdf.set_text_color(0,0,255)
    pdf.set_font('Arial','',8)
    pdf.cell(40, 5, "Portata", 0, 0, 'L')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'B', 8)
    stringa_servizio = dati["portata_lpm"] + " l/min"
    pdf.cell(20, 5, stringa_servizio, 0, 1, 'L')
    pdf.set_text_color(0, 0, 255)
    pdf.set_font('Arial', '', 8)
    pdf.cell(40, 5, "Pressione:", 0, 0, 'L')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'B', 8)
    stringa_servizio = dati["pressione_bar"] + " bar"
    pdf.cell(20, 5, stringa_servizio, 0, 1, 'L')
    
    pdf.ln(5)
    pdf.set_text_color(0, 0, 255)
    pdf.set_font('Arial', 'B', 8)
    if tubo:
        pdf.cell(40, 5, "Configurazione tubo:", 0, 1, 'L')
    
    # print("len(tubo) = ", len(tubo))
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 8)  
    if tubo["lunghezza"] != "" and tubo["diametro"] != "" and tubo["materiale"]["etichetta"] != "":
            pdf.cell(60, 5, str(i + 1) + ". Lunghezza = " + tubo["lunghezza"] + " m, " + tubo["materiale"]["etichetta"], 0, 0, 'L')
            pdf.cell(60, 5, "DN = " + tubo["diametro"] + " mm", 0, 0, 'L')
            
    pdf.ln(5)
    
    pressione_ugello = float(dati["pressione_bar"]) - perdita_pressione
    
    portata_totale = 0.0
    for q_i in portata_gruppo:
        portata_totale += q_i
    
    portata_in_eccesso = float(dati["portata_lpm"]) - portata_totale
    pdf.set_text_color(0, 0, 255)
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(40, 5, "Calcoli", 0, 1, 'L')
    
    pdf.set_text_color(0, 0, 255)
    pdf.set_font('Arial', '', 8)
    pdf.cell(40, 5, "Pressione persa:", 0, 0, 'L')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'B', 8)
    if perdita_pressione > 100.0:
        stringa_servizio = "{:5.1f}".format(perdita_pressione) + " bar"
    elif perdita_pressione > 10.0:
        stringa_servizio = "{:4.1f}".format(perdita_pressione) + " bar"
    elif perdita_pressione > 1.0:
        stringa_servizio = "{:3.1f}".format(perdita_pressione) + " bar"
    else:
        stringa_servizio = "{:2.1f}".format(perdita_pressione) + " bar"
    pdf.cell(20, 5, stringa_servizio, 0, 1, 'L')
    pdf.set_text_color(0, 0, 255)
    pdf.set_font('Arial', '', 8)
    pdf.cell(40, 5, "Pressione all'ugello:", 0, 0, 'L')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'B', 8)
    if pressione_ugello > 100.0:
        stringa_servizio = "{:5.1f}".format(pressione_ugello) + " bar"
    elif perdita_pressione > 10.0:
        stringa_servizio = "{:4.1f}".format(pressione_ugello) + " bar"
    elif pressione_ugello > 1.0:
        stringa_servizio = "{:3.1f}".format(pressione_ugello) + " bar"
    else:
        stringa_servizio = "{:2.1f}".format(pressione_ugello) + " bar"
    pdf.cell(20, 5, stringa_servizio, 0, 1, 'L')
    pdf.set_text_color(0, 0, 255)
    pdf.set_font('Arial', '', 8)
    pdf.cell(40, 5, "Portata effettiva:", 0, 0, 'L')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'B', 8)
    if portata_totale > 100.0:
        stringa_servizio = "{:5.1f}".format(portata_totale) + " lit/min"
    elif portata_totale > 10.0:
        stringa_servizio = "{:4.1f}".format(portata_totale) + " lit/min"
    elif portata_totale > 1.0:
        stringa_servizio = "{:3.1f}".format(portata_totale) + " lit/min"
    else:
        stringa_servizio = "{:2.1f}".format(portata_totale) + " lit/min"
    
    pdf.cell(20, 5, stringa_servizio, 0, 1, 'L')
    pdf.set_text_color(0, 0, 255)
    pdf.set_font('Arial', '', 8)
    pdf.cell(40, 4, "Portata in eccesso:", 0, 0, 'L')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'B', 8)
    if portata_in_eccesso > 100.0:
        stringa_servizio = "{:5.1f}".format(portata_in_eccesso) + " lit/min"
    elif portata_in_eccesso > 10.0:
        stringa_servizio = "{:4.1f}".format(portata_in_eccesso) + " lit/min"
    elif portata_totale > 1.0:
        stringa_servizio = "{:3.1f}".format(portata_in_eccesso) + " lit/min"
    else:
        stringa_servizio = "{:2.1f}".format(portata_in_eccesso) + " lit/min"
    
    pdf.cell(20, 5, stringa_servizio, 0, 1, 'L')
    pdf.ln(5)
    pdf.set_text_color(0, 0, 255)
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(40, 5, "Assemblaggio", 0, 1, 'L')
    
    i = 0
    print("dati['gruppi']", gruppi)
    for j in gruppi:
        if j > 0:    
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Arial', '', 8)
            pdf.cell(40, 5, "J" + str(i) + " = " + str(j) + " x " + str(inserti_taratura[i]["Orifizio (mm)"]), 0, 0, 'L')
            pdf.cell(40, 5, inserti_taratura[i]["Codice"] + " " + inserti_taratura[i]["Descrizione"], 0, 1, 'L')
        i += 1    

    
    
    # footer
    
    pdf.set_y(290)
    # Select Arial bold 8
    pdf.set_font('Arial', '', 8)
    pdf.cell(60, 5, 'Versione 1.0', 0, 0, 'L')
    pdf.cell(60, 5, 'www.nuovacontec.com', 0, 0, 'C')
    pdf.cell(50, 5, 'Data di stampa: ' + str(date.today().day) + "/" + str(date.today().month) + "/" + str(date.today().year), 0, 1, 'R')
    
    
    
    pdf.output('uploads/report.pdf', 'F')





def get_materiale_inserti(tipo):
    for i in inserti["inserti"]:
        if i["tipo"] == tipo:
            return i["materiale"]
    return "N/D"
    
@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    # Appending app path to upload folder path within app root folder
    uploads = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    # Returning file from appended path
    return send_from_directory(directory=uploads, path=filename, as_attachment=True)

    

@app.route("/inserti")
def showInserti():
#    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
#    json_inserti_url = os.path.join(SITE_ROOT, "static/data", "inserti.json")
#    inserti = json.load(open(json_inserti_url))
   
    return render_template('inserti.html', inserti = inserti["inserti"])
@app.route("/ugelli")
def showUgelli():
#    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
#    json_ugelli_url = os.path.join(SITE_ROOT, "static/data", "ugelli.json")
#    ugelli = json.load(open(json_ugelli_url))
    return render_template('ugelli.html', ugelli = ugelli["ugelli"])



#return app