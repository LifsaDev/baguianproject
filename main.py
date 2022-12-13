 
from sqlalchemy import true
from streamlit_option_menu import option_menu
from PIL import Image
import streamlit as st
import os
import re
import time
import numpy as np
import pandas as pd
from scipy.integrate import odeint, quad
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
from streamlit_lottie import st_lottie
import json
import serial
import serial.tools.list_ports
import base64
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
from scipy.signal import find_peaks
i =0
portsconnecté = []
tab = []
valeur_x =[]
valeur_y = []
valeur_z = []
valeur_a = []
valeur_p = []
v_theta = []
patern_x = "x"
patern_y = "y"
patern_z = "z"
patern_a = "a"
patern_p = "p"

noms_courbes = ["Théorique","Accéléromètre","Encodeur","Potensiomètre"]
types_courbe = ["Théta","Théta dérivée prémière","Théta dérivée seconde"]



	# maxindex=0
	# for i in range(0,len(courbe)-1):
	#    if courbe[i]==max(courbe):
	#        maxindex=i
	#        break
	
	# lp=[]
	# for i in range(maxindex,len(courbe)-1):
	#    if courbe [i-1] <= courbe [i] and courbe [i] >= courbe [i+1] :
	#        lp.append (i)
	
	# s=0
	# for l in range (1,len (lp)) :
	#    s += lp [l] - lp [l-1]
	# return float (s) / (len (lp)-1)*dt
def periode (courbe,dt) :
	lp = []
	p = 0
	for i in range (1, len (courbe)-1) :
		if courbe [i-1] <= courbe [i] and courbe [i] >= courbe [i+1]:
			lp.append (i)
	# moyenne entre les durees entre deux maximas
	s = 0
	for l in range (1,len (lp)):
		s += lp [l] - lp [l-1]
	return float (s) / (len (lp)-1)

def theta(x,y,z):
	
	# A_xout = (((x*3.3)/4096)-1.65)/0.33
	# A_yout = (((y*3.3)/4096)-1.65)/0.33
	# A_zout = (((z*3.3)/4096)-1.65)/0.33
	
	resultat = np.arctan(x/(np.sqrt(y*y+z*z)))
	return  (180/3.14)*resultat


def pdf_reader(file):
	resource_manager = PDFResourceManager()
	fake_file_handle = io.StringIO()
	converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
	page_interpreter = PDFPageInterpreter(resource_manager, converter)
	with open(file, 'rb') as fh:
		for page in PDFPage.get_pages(fh,
									  caching=True,
									  check_extractable=True):
			page_interpreter.process_page(page)
			print(page)
		text = fake_file_handle.getvalue()

	# close open handles
	converter.close()
	fake_file_handle.close()
	return text


def show_pdf(file_path):
	with open(file_path, "rb") as f:
		base64_pdf = base64.b64encode(f.read()).decode('utf-8')
	# pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
	pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
	st.markdown(pdf_display, unsafe_allow_html=True)


def pendule(z, t):
	# Z1 = z[1]
	# Z0 = z[0]
	v = np.array([z[1],
				  -float(z[1]) -float(z[0])])
	return v

g = 9.81
l = 25 #cm
m = 0.1
k = 8

b = 0.2
c = 8

def load_lottiefile(filepath: str):
	with open(filepath, "r") as f:
		return json.load(f)
		
c="",
def loti(c) :
	lottie_coding = load_lottiefile(c)  # replace link to local lottie file
		  
	st_lottie(
			  lottie_coding,
			  speed=1,
			  reverse=False,
			  loop=True,
			  quality="high", # medium ; high
		 #renderer="svg", # canvas
			  height=None,
			  width=200,
			  key=None,
			   )  


st.markdown("""
<style>
.first_titre {
	font-size:60px !important;
	font-weight: bold;
	box-sizing: border-box;
	text-align: center;
	width: 100%;
}
.intro{
	text-align: justify;
	font-size:20px !important;
}
.grand_titre {
	font-size:30px !important;
	
	# text-decoration: underline;
	text-decoration-color: #4976E4;
	text-decoration-thickness: 5px;
}
.section{
	font-size:20px !important;
	font-weight: bold;
	text-align: center;
	text-decoration: underline;
	text-decoration-color: #111111;
	text-decoration-thickness: 3px;
}
.petite_section{
	font-size:16px !important;
	font-weight: bold;
}
.nom_colonne_page3{
	font-size:17px !important;
	text-decoration: underline;
	text-decoration-color: #000;
	text-decoration-thickness: 1px;
}
</style>
""", unsafe_allow_html=True)


choose = option_menu("Pendule Non actionné",["Home","Rapport","IHM","Ressources"],
	icons=['house','bi bi-card-heading','bi bi-window-split','person lines fill'],
	menu_icon = "None", default_index=0,
	styles={
		"container": {"padding": "5!important", "background-color": ""},
		"icon": {"color": "orange", "font-size": "20px"}, 
		"nav-link": {"font-size": "10px", "text-align": "left", "margin":"5px", "--hover-color": ""},
		"nav-link-selected": {"background-color": ""},
	},orientation = "horizontal"
	)

if choose=="Home":
	st.markdown('<p class="first_titre">Projet : Pendule Non actionné </p>', unsafe_allow_html=True)
	st.write("---")
	c1, c2 = st.columns((4, 1))
	with c1:
		st.header("Description")
		st.markdown(
			'<p class="intro"><b>Dans ce projet nous souhaitons instrumenter un pendule simple, c’est-à-dire mesure les déplacements, vitesses et accélérations du pendule. Dans un premier temps,vous devrez réaliser le système de mesure, puis dans un second temps vous devrez exploiter vos résultats de mesure pour les comparer avec la théorie.</b></p>',
			unsafe_allow_html=True)
		
		
	with c2:
		loti("lotties/22605-smooth-swinging.json")
	
   
	vi1, vi2 = st.columns((3, 2))
	vi3, vi4 = st.columns((3, 2))
	st.subheader("Teams")
	st.write(
			"• [BAGUIAN HAROUNA/GitHub](https://github.com/Diaffat)")


if choose=="IHM":
	cmt = 0
	t = np.linspace(0, 100, 500)
	with st.sidebar:
		st.markdown(
			'<p class="intro"><b>Connexion</b></p>',
			unsafe_allow_html=True)

		c0, c10 = st.columns(2)
		c1, c2 = st.columns(2)

		connect = st.checkbox("connexion")
		ser = serial.Serial()
		ser.port = "COM4"
		ser.baudrate = 115200
		if connect:
			ser.open()
			st.balloons()
			
			
			while(len(v_theta)<500):
				msg = ser.readline()
				msg = msg.decode("utf-8")
				
				#valeur de x

				if re.search(patern_x,msg):
					string=re.split(patern_x, msg)[1]
					dispatch= re.split("t", string)
					v = dispatch[0]
					string = dispatch[1]
					valeur_x.append(float(v))
					cmt = cmt+1
				
				#valeur de y

				if re.search(patern_y,msg):
					string=re.split(patern_y, msg)[1]
					dispatch= re.split("u", string)
					v = dispatch[0]
					string = dispatch[1]
					valeur_y.append(float(v))
					cmt = cmt+1
				
				# valeur de z
				
				if re.search(patern_z,msg):
					string=re.split(patern_z, msg)[1]
					dispatch= re.split("v", string)
					v = dispatch[0]
					string = dispatch[1]
					valeur_z.append(float(v))
					cmt = cmt+1

				# valeur de a
				
				if re.search(patern_a,msg):
					string=re.split(patern_a, msg)[1]
					dispatch= re.split("w", string)
					v = dispatch[0]
					string = dispatch[1]
					valeur_a.append(float(v))
					
				
				# valeur de la position
				
				if re.search(patern_p,msg):
					string=re.split(patern_p, msg)[1]
					dispatch= re.split("f", string)
					v = dispatch[0]
					string = dispatch[1]
					valeur_p.append(float(v))
				
				# theta
				if(cmt==3):
					a = theta(valeur_x[i],valeur_y[i],valeur_z[i])
					v_theta.append(a)
					i = i+1
				
				cmt = 0
				time.sleep(0.02)
			ser.close()
		
	st.header("Simulation")

	for i in range(0,len(v_theta)):
		v_theta[i]=abs(v_theta[i])

	T0 = periode(v_theta,0.02)

	deriv_potentio = np.diff(valeur_a)/0.02
	deriv_potentio = np.append(deriv_potentio,0)


	fig = px.line(x=t, y=v_theta, title='theta Accéléromètre')

	st.plotly_chart(fig)

	fig = px.line(x=t, y=valeur_a, title='theta Potentiomètre')

	st.plotly_chart(fig)

	fig = px.line(x=t, y=valeur_p, title='vitesse encodeur')

	st.plotly_chart(fig)

	st.write("T0 : "+str(T0))    

	fig = px.line(x=t, y=deriv_potentio)

	st.plotly_chart(fig)



	
	Z0=[np.pi-0.1, 0]
	
	Y=odeint(pendule,Z0,t)
	
	# c_fro, c_masse, c_long, c_posi = st.columns(4)
	# v_fro = c_fro.number_input("Coéfficient de froteement")
	# v_masse=c_masse.number_input("Masse")
	# v_long = c_long.number_input("Longueur")
	# v_posi = c_posi.number_input("Angle de départ")
	# vid1,vid2 = st.columns(2)
	# g3,g4 = st.columns(2)
	# typec = g3.selectbox("Type de courbe",types_courbe)
	# g1, g2 = st.columns((3,2))
	# with g1:
	#     st.header(typec)
	fig = px.scatter(x=t, y=Y[:,0])

	st.plotly_chart(fig)
			
	# with g2:
		
	#     st.header("Choix de Courbes")
		
	#     st.multiselect("Courbes Théta",noms_courbes)

	st.header("Estimateur")
	c2,c3 = st.columns(2)
	if c2.button("Calculer"):
		c3.header("25 cm")

res = ["Sujet","Datashets","STM32","Circuit électronique","eagle"]
if choose=="Ressources":
	with st.sidebar:
		st.header("Ressources du projet")
		st.selectbox("ressources",res)


	pdf_file = st.sidebar.file_uploader("Choose your Resume",type=["pdf"])
	if pdf_file is not None:
			
			# st.write(type(pdf_file))
			# file_details = {"filename":pdf_file.name,"filetype":pdf_file.type,"filesize":pdf_file.size}
			# st.write(file_details)
			save_image_path = './ressourses/'+pdf_file.name
			with open(os.path.join("./ressourses",pdf_file.name), "wb") as f:
					f.write(pdf_file.getbuffer())
			show_pdf(save_image_path)


plan = ["Introduction","Etude Dynamique","Réseau de capteurs","Circuit imprimé","IHM","Conclusion"]
if choose=="Rapport":
	
	with st.sidebar:
		ele_plan = st.radio("Plan",plan)
	if ele_plan=="Introduction":
		st.markdown('<p class="first_titre">Rapport : Projet Pendule Non actionné </p>', unsafe_allow_html=True)
		st.write("---")
		st.markdown(
			'<b>Notre projet de IPS S7 consiste à simuler et récupérer les données d’une pendule non actionnée avec une carte STM32 et trois capteurs (Accéléromètre, Encodeur et Potentiomètre). <p>Ces capteurs servent à mesurer l’accélération, la vitesse et la position de la masse et en comparant ces valeurs grâce à la dérivation et l’intégration, nous pouvons observer l’influence du bruit sur notre système. <p>Nous avons également fait un estimateur qui, grâce aux données des capteurs, va estimer à quelle distance se situe la masse par rapport au bras de la pendule.<p></b>',
			unsafe_allow_html=True)
		#Diagramme_Fonctionnel
		image = Image.open("images/Diagramme_Fonctionnel.jpg")
		st.image(image)
		st.markdown('<p>Nous avons planifié ce projet, sur ce diagramme de Gantt : ',unsafe_allow_html=True)
		image = Image.open("images/gantt.PNG")
		st.image(image)
	
	elif ele_plan=="Etude Dynamique":
		st.markdown('<p class="first_titre">Etude Dynamique </p>', unsafe_allow_html=True)
		st.write("---")
		st.markdown(
			'<p class="intro"><b>On a commencé à faire l’étude dynamique du pendule théoriquement en déterminant l’équation du mouvement avec frottements secs et en la simulant sous python</b></p>',unsafe_allow_html=True) 
		img_cp1, img_cp2 = st.columns(2)
		with img_cp1:
			image = Image.open("images/frottements_secs.png")
			st.image(image)
		
		
		with img_cp2:
			image1 = Image.open("images/pendule.png")

			st.image(image1,width=200)
	
	elif ele_plan=="IHM":
		st.markdown('<p class="first_titre">IHM</p>', unsafe_allow_html=True)
		st.write("---")
		st.markdown(
		'''<p class="intro"><b>Comme vous pouvez l'observer, notre IHM est implémenté sur notre page web, codée en python grâce à Streamlit. Streamlit est un outil open-source qui sert à fabriquer des applications web avec des fonctionnalités en python, et on l’utilise en tandem avec serial, numpy et plotly pour sa fonctionnalité. Nous avons utilisé notre IHM pour effectuer les calculs que notre STM32 ne peut pas effectuer efficacement (par exemple, arctan() et des opérations de grandes listes) ainsi que les graphiques des courbes. On récupère les données avec un port série et sous notre format (“x%.2f ty%.2f uz%.2f va%d wp%.2f f\r\n”) pour faciliter le traitement. On effectue une simulation sur 10 secondes, et ensuite on affiche les courbes reçues pour identifier l’influence du bruit ainsi que la distance estimée de la masse.</b></p>''',
		unsafe_allow_html=True)
		img_acc = Image.open("images/Simulation.PNG")
		st.image(img_acc)
		st.markdown(
		'(courbe 1 : Theta Accéléromètre, courbe 2 : Theta Potentiomètre, courbe 3 : Vitesse Encodeur)',
		unsafe_allow_html=True)
		st.markdown(
		'<p class="intro"><b>Lors des tests, nous avons rencontré des problèmes d’affichage avec notre potentiomètre. En effet, notre potentiomètre envoyait des sauts brusques. C’était à cause de notre valeur qui faisait un tour complet et retourne la valeur de l’autre côté.</b></p>',
		unsafe_allow_html=True)
 
	elif ele_plan=="Conclusion":
		st.markdown('<p class="first_titre">Conclusion</p>', unsafe_allow_html=True)
		st.write("---")
		st.markdown(
			'<p class="intro"><b>Ce projet nous a permis d’utiliser en pratique nos enseignements et de confronter le rendu des équations théoriques calculées à la réalité des données récupérées. Il nous a aussi permis de découvrir le logiciel de CAO Électronique EAGLE et d’approfondir nos compétences en acquisition de données (STM32) et en réalisation d’un IHM. Cependant, nous avons rencontré des problèmes lors de ce projet notamment avec notre circuit imprimé, car c’est la première fois que nous avons effectué un projet comme celui-ci, mais nous nous sommes adaptés et on a appris beaucoup sur la planification et l’impression des circuits imprimés.</b></p>',
			unsafe_allow_html=True)
	elif ele_plan=="Réseau de capteurs":
		st.markdown('<p class="first_titre">Réseau de capteurs </p>', unsafe_allow_html=True)
		st.write("---")
		equation_Aout = r'''
			$$ 
			A_{out} = \frac{\frac{ADC*V_{ref}}{4096}-1.65}{0.33}
			$$
			'''
		equation_Theta = r'''
			$$
			\theta=arctan(\frac{A_x}{\sqrt{A_y²+A_z²}})
			$$
			'''
		equation_Position = r'''
			$$
			position=V_{out}*\frac{360}{5*4096}
			$$
			'''
		equation_Encodeur = r'''
			$$
			speed=(valeur actuelle -valeur précédente)*\frac{360}{2048}
			$$
			'''
		st.markdown(
			'<p class="intro"><b> Lors de ce projet, nous avons implémenté trois capteurs afin de simuler l’influence du bruit mais aussi pour estimer le position de la masse sur la pendule.</b></p>',unsafe_allow_html=True)
		
		st.markdown(
			'<p class="grand_titre">1 - Accéléromètre : ADXL335</p>',unsafe_allow_html=True)
		st.markdown(
			'<p class="intro"><b> Nous avons utilisé le ADC1 de notre carte STM32 en mode DMA (direct memory access) afin de lire les 3 valeurs directement de l’accéléromètre.</b></p>',unsafe_allow_html=True)
	  
		img_c1, img_c2 = st.columns(2)
		with img_c1:
		
			st.markdown(equation_Aout)
			st.markdown(equation_Theta)
		with img_c2:

			img_acc = Image.open("images/accelorometre.webp")
			st.image(img_acc,width=200)
		st.markdown(
			'<p class="grand_titre">2 - Potentiomètre : Vishay Model 357</p>',unsafe_allow_html=True)
		st.markdown(
			'<p class="intro"><b>  Après conditionnement, amplification et filtrage, on reçoit cette donnée également avec notre ADC1 en DMA et on effectue la suivante : </b></p>',unsafe_allow_html=True)

		img_cp1, img_cp2 = st.columns(2)
		with img_cp1:
		
		   st.markdown(equation_Position)
		with img_cp2:

			img_acc = Image.open("images/potentio.jpg")
			st.image(img_acc,width=200)
		
		st.markdown(
			'<p class="grand_titre">3 - Encodeur Rotatif : Encodeur-Baumer_IVO_GI342</p>',unsafe_allow_html=True)
		st.markdown(
			'<p class="intro"><b> Pour recevoir les données de l’encodeur sur la carte STM32, il faut configurer un timer en mode encodeur, c-à-d avoir un timer qui s’incrémente lors de chaque pulsation d’encodeur.<p>Cette valeur est à diviser par 4 et la dernière valeur doit être sauvegardé afin de calculer la vitesse : </b></p>',unsafe_allow_html=True) 
	   
		st.markdown(equation_Encodeur)
		
		img_ce1, img_ce2 = st.columns(2)
		with img_ce2:
			img_acc = Image.open("images/encodeur.webp")
			st.image(img_acc,width=200)
	   
		st.markdown(
			'<p class="intro"><b>  2048 : nombre de coups d’horloge par révolution.</b></p>',unsafe_allow_html=True)
   
		
	elif ele_plan=="Circuit imprimé":
		st.markdown('<p class="first_titre">Circuit imprimé </p>', unsafe_allow_html=True)
		st.write("---")
		st.markdown(
		'<p class="intro">On a divisé cette partie en trois phases une première qui consiste à faire une certaine étude préliminaire du circuit, une deuxième où on faisait des tests et une troisième qui concerne notre PCB :</p>',
		unsafe_allow_html=True)
		st.markdown(
		'<p class="grand_titre"><b>=> Phase de décision sur les composants du circuit :</b></p>',
		unsafe_allow_html=True)
		st.markdown(
		'<p class="intro">La chaîne d’acquisition des données des capteurs consiste à passer par plusieurs étages.<p></p>',
		unsafe_allow_html=True)
		
		st.markdown(
		'<p class="grand_titre">- Conditionnement : consiste à rendre la mesure issue du capteur exploitable.<p></p>',
		unsafe_allow_html=True)
		st.markdown(
		'<p class="intro">Le montage en pont de Wheatstone est un groupement de résistances électriques qui permettent de mesurer précisément les variations de résistance. Par ailleurs, grâce à la nature différentielle de la mesure récupérée à la sortie du pont, le signal sera moins sensible aux bruits ainsi qu’aux dérivés de la source. Cependant, un équilibrage du pont est nécessaire, et cela n’est possible que si R1.R4=R2.R3 est vérifiée. A cet effet, nous avons bien choisi des résistances identiques à la résistance du capteur qui est de 10kΩ.</p>',
		unsafe_allow_html=True)
		
		st.markdown(
		'<p class="grand_titre">- Amplification : consiste à adapter le niveau du signal issu du capteur à la chaîne globale d’acquisition.</p>',
		unsafe_allow_html=True)
		st.markdown(
		'<p class="intro">On a opté pour le choix d’un amplificateur d’instrumentation (AD621) afin de passer d’une tension qui ne dépasse pas 1V à une tension de 3.3V. Ce choix vient du fait que cet amplificateur est unipolaire, donc on aura qu’une source de tension positive à gérer.</p>',
		unsafe_allow_html=True)
		
		st.markdown(
		'<p class="grand_titre">- Filtrage : permet de limiter le contenu spectral du signal aux fréquences désirées.</p>',
		unsafe_allow_html=True)
		st.markdown(
		'<p class="intro">On a choisi un filtre passe bas afin d’atténuer les hautes fréquences qui peuvent parvenir des bruits. La fréquence de coupure est fixée à partir de la période d’oscillation du pendule et le produit RC qui convient à cette fréquence est équivalente à 100nF pour le condensateur et 33 KΩ pour la résistance, ce qui donne une fréquence de coupure de la valeur de 48Hz.</p>',
		unsafe_allow_html=True)
		
		st.markdown(
		'<p class="grand_titre"><b>=> Phase de test :</b></p>',
		unsafe_allow_html=True)
		st.markdown(
		'<p class="intro">Après avoir choisi les composants de chaque étage d’acquisition, on a lié tous ces composants sur un protoboard afin de vérifier si tout fonctionne bien en mesurant le signal sortant avec un oscilloscope.',
		unsafe_allow_html=True)
		st.markdown(
		'<p class="grand_titre"><b>=> Phase d’implémentation sur Eagle:</b></p>',
		unsafe_allow_html=True)
		st.markdown(
		'<p class="intro">Cette phase consiste à faire une schématique au début qui n’est qu’un aperçu de notre maquette de test. Après la schématique on passe au PCB où il faut faire le routage optimal permettant d’avoir le minimum encombrement possible pour éviter les problèmes de soudage ou de perturbation des pistes. Lors de cette étape, on devait bien respecter les règles imposées sur le format du circuit, ainsi que des composants et ensuite vérifier s’il y en a des erreurs afin de les corriger.</p>',
		unsafe_allow_html=True)
		img_acc = Image.open("images/cao.PNG")
		st.image(img_acc)


