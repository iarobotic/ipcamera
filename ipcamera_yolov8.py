import cv2
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import numpy as np
from ultralytics import YOLO
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from decimal import Decimal

model = YOLO("yolov8n.pt")

root = tk.Tk()
root.title("IP Camera Detection")
root.option_add("*tearOff", False) # This is always a good idea

# Make the app responsive
root.columnconfigure(index=0, weight=1)
root.columnconfigure(index=1, weight=1)
root.columnconfigure(index=2, weight=1)
root.rowconfigure(index=0, weight=1)
root.rowconfigure(index=1, weight=1)
root.rowconfigure(index=2, weight=1)

# Create a style
style = ttk.Style(root)

# YOUR OWN CONFIGURATION
# TU PROPIA CONFIGUARCION

aplication_password = '...'  # gmail account 
remitente = 'fj.ollero.pacheco@gmail.com' # gmail address
# time that must elapse between detections in seconds
# tiempo que debe transcurrir entre detecciones en segundos
detection_time = 300 


# VARIABLES DEL PROGRAMA
user_change = True
clase_usuario = []
precision_usuario = []
tiempo_evento = [datetime.datetime(2023, 3, 29, 12, 30, 45), datetime.datetime(2023, 3, 29, 12, 30, 45) , datetime.datetime(2023, 3, 29, 12, 30, 45)]
path_log = './log/'

# Funcion para actualizar las variables de deteccion
def update():
    global clase_usuario, precision_usuario
    
    clase_usuario = []
    clase_usuario.append(clase1.get())
    clase_usuario.append(clase2.get())
    clase_usuario.append(clase3.get())

    precision_usuario = []
    precision_usuario.append(Decimal(precision1.get()))
    precision_usuario.append(Decimal(precision2.get()))
    precision_usuario.append(Decimal(precision3.get()))

# Funcion para detectar los cambios en las variables de deteccion
def on_entry_change_detections(*args):
    global user_change
    if user_change:
        update()
    user_change = True

# Funcion de aviso de cambio de IP
def on_entry_change_ip(*args):
    global user_change
    if user_change:
        messagebox.showinfo("Attention", "Close the program and restart it to apply the changes")
    user_change = True

# VARIABLES DE LA INTERFACE
show_image = tk.BooleanVar()
show_detection = tk.BooleanVar()
detection_on = tk.BooleanVar()
show_image.set(True)
show_detection.set(False)
detection_on.set(False)
combo_list1 = ["person", "bicycle", "car", "motorcycle", "bus", "train", "truck", "boat", "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe"]
combo_list2 = ["person", "bicycle", "car", "motorcycle", "bus", "train", "truck", "boat", "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe"]
combo_list3 = ["person", "bicycle", "car", "motorcycle", "bus", "train", "truck", "boat", "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe"]
show_img = tk.BooleanVar(value=True)
show_det = tk.BooleanVar(value=False)
detection_on = tk.BooleanVar(value=False)
theme = tk.BooleanVar(value=True)
clase1 = tk.StringVar()
clase1.trace_add("write", on_entry_change_detections)
clase2 = tk.StringVar()
clase2.trace_add("write", on_entry_change_detections)
clase3 = tk.StringVar()
clase3.trace_add("write", on_entry_change_detections)
precision1 = tk.StringVar()
precision1.trace_add("write", on_entry_change_detections)
precision2 = tk.StringVar()
precision2.trace_add("write", on_entry_change_detections)
precision3 = tk.StringVar()
precision3.trace_add("write", on_entry_change_detections)
email = tk.StringVar()
ip = tk.StringVar()
ip.trace_add("write", on_entry_change_ip)
file = tk.StringVar()

# Leer los datos del archivo txt y actualizar las variables
with open("configuration.txt", "r") as f:

    clase1.set(f.readline().strip())
    clase2.set(f.readline().strip())
    clase3.set(f.readline().strip())
    precision1.set(f.readline().strip())
    precision2.set(f.readline().strip())
    precision3.set(f.readline().strip())
    email.set(f.readline().strip())
    user_change = False
    ip.set(f.readline().strip())
    file.set(f.readline().strip())
    if(f.readline().strip()=='True'):
        theme.set(True)
    else:
        theme.set(False)
    
if theme.get():
    # Import the tcl file
    root.tk.call("source", "forest-dark.tcl")

    # Set the theme with the theme_use method
    style.theme_use("forest-dark")
else:
    # Import the tcl file
    root.tk.call("source", "forest-light.tcl")

    # Set the theme with the theme_use method
    style.theme_use("forest-light")


# VARIABLES DEL PROGRAMA 2
source_camera = 'rtsp://'+ ip.get() +'/12'
cap = cv2.VideoCapture(source_camera)

# FUNCIONES DE LA INTERFACE
# Salir del programa y guardar los datos
def exit():
    
    with open("configuration.txt", "w") as f:

        f.write(clase1.get() + "\n")
        f.write(clase2.get() + "\n")
        f.write(clase3.get() + "\n")
        f.write(precision1.get() + "\n")
        f.write(precision2.get() + "\n")
        f.write(precision3.get() + "\n")
        f.write(email.get()+ "\n")
        f.write(ip.get()+ "\n")
        f.write(file.get()+ "\n")
        if theme.get():
            f.write("True"+ "\n")
        else:
            f.write("False"+ "\n")

  
    root.destroy()

# FUNCIONES PROCESOS

# Función para capturar y mostrar la imagen de la cámara en una ventana Tkinter
def show_frame():
    global model, clase_usuario, precision_usuario, path_log, show_img, show_det

    ret, frame = cap.read()
    
    if ret:
        #frame = cv2.resize(frame, (600, 300))
        # Aplicar la detección de objetos si el botón "Show Detection" está marcado

        if detection_on.get()==True:
            # llamada a la predicción de la imagen
            # show : por si se quiere mostrar la imagen con las detecciones
            # save_conf : si queremos el log con la precision
            # save_txt : si queremos el log con las detecciones
            # save : si queremos guardar la imagen con las detecciones

            m_detect = show_detection.get()
            results = model.predict(source=frame, show=m_detect, save_conf=False, save_txt=False, save=False)
            
            clase = []
            precision = []
            label_onoff.config(text='...process...')
            # procesamos la respuesta
            for r in results:
                # recorremos las clases detectadas
                for c in r.boxes.cls:
                    clase.append(model.names[int(c)])
                    nuevo_texto = model.names[int(c)]
                    label_onoff.config(text=nuevo_texto)
                for p in r.boxes.conf:
                    precision.append(p.cpu().numpy())

            # chequeamos los resultados
                with open(path_log + file.get(), mode='a+', encoding='utf-8') as archivo:
                    for i, c in enumerate(clase):
                        if c in clase_usuario:
                            indice_usuario = clase_usuario.index(c)
                            if precision[i] > precision_usuario[indice_usuario]:
                                tiempo_actual = datetime.datetime.now()
                                diferencia = tiempo_actual - tiempo_evento[indice_usuario]
                                if diferencia.total_seconds() > detection_time: # time that must elapse between detections
                                    label_detection.config(text='Detectado: '+c+' con una precision de: '+str(precision[i]))
                                    tiempo_evento[indice_usuario] = tiempo_actual
                                    fecha_actual = tiempo_actual.strftime('%Y%m%d')
                                    hora_actual = tiempo_actual.strftime('%H%M%S')
                                    linea = f'{fecha_actual}, {hora_actual}, {c}, {precision[i]}\n'
                                    archivo.write(linea)
                                    imagen = path_log+fecha_actual+hora_actual+'.jpg'
                                    cv2.imwrite(imagen, frame)
                                    mensaje = f'Fecha: {fecha_actual}\nHora: {hora_actual}\nClase: {c}\nPrecision: {precision[i]}'
                                    send_email(imagen, email.get(), mensaje)
                                    
        else:
            img = frame
            label_onoff.config(text='...off...')

        # Convertir el marco en un objeto de imagen Tkinter
        if show_image.get()==True:
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)

            label.imgtk = imgtk
            label.configure(image=imgtk)
      
    # Llamar a esta función nuevamente después de 10 milisegundos
    label.after(10, show_frame)

# Función evento de email
def send_email(img, destinatario, texto):
    # Define los parámetros del correo electrónico

    asunto = 'Alert detection camera'
    ruta_imagen = img

    # Carga la imagen como un archivo binario
    with open(ruta_imagen, 'rb') as archivo_imagen:
        imagen = MIMEImage(archivo_imagen.read())
        imagen.add_header('Content-Disposition', 'attachment', filename=ruta_imagen)

    # Crea el objeto MIMEMultipart y agrega los elementos de texto e imagen
    mensaje = MIMEMultipart()
    mensaje['From'] = remitente
    mensaje['To'] = destinatario
    mensaje['Subject'] = asunto
    mensaje.attach(MIMEText(texto))
    mensaje.attach(imagen)

    # Inicia sesión en el servidor SMTP y envía el correo electrónico
    servidor_smtp = smtplib.SMTP('smtp.gmail.com', 587)
    servidor_smtp.starttls()
    servidor_smtp.login(remitente, aplication_password)
    servidor_smtp.sendmail(remitente, destinatario, mensaje.as_string())
    servidor_smtp.quit()

# DISEÑO DE LA INTERFAZ

# Create a Frame for input widgets
widgets_frame = ttk.Frame(root, padding=(0, 0, 0, 0))
widgets_frame.grid(row=1, column=0, pady=(30, 10), sticky="nsew")
widgets_frame.columnconfigure(index=0, weight=1)
# Switch
switch_theme = ttk.Checkbutton(widgets_frame, text="Theme Light/Dark", style="Switch", variable=theme)
switch_theme.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
# Switch
switch_image = ttk.Checkbutton(widgets_frame, text="Show Image Off/On", style="Switch", variable=show_image)
switch_image.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
# Switch
switch_detection = ttk.Checkbutton(widgets_frame, text="Show Detection Off/On", style="Switch", variable=show_detection)
switch_detection.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
# Switch
switch_onoff = ttk.Checkbutton(widgets_frame, text="Detection Off/On", style="Switch", variable=detection_on)
switch_onoff.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
# Label
label_onoff = ttk.Label(widgets_frame, text="...")
label_onoff.grid(row=4, column=0, padx=15, pady=(0, 10), sticky="ew")
# Label
label_detection= ttk.Label(widgets_frame, text="...")
label_detection.grid(row=5, column=0, padx=15, pady=(0, 10), sticky="ew")

# Create a Frame for input widgets
widgets_notebook = ttk.Frame(root, padding=(0, 0, 0, 0))
widgets_notebook.grid(row=0, column=1, padx=10, pady=(30, 10), sticky="nsew")
widgets_notebook.columnconfigure(index=0, weight=1)
# Notebook
notebook = ttk.Notebook(widgets_notebook)
# Tab #1
tab_1 = ttk.Frame(notebook)
notebook.add(tab_1, text="Detection 1")
# Combobox
combobox1 = ttk.Combobox(tab_1, values=combo_list1, textvariable=clase1)
#combobox1.current(0)
combobox1.grid(row=0, column=0, padx=5, pady=10,  sticky="ew")
# Label
label = ttk.Label(tab_1, text="Precision:", justify="left")
label.grid(row=1, column=0)
# Entry
entry1 = ttk.Entry(tab_1, textvariable=precision1)
#entry1.insert(0, "0.5")
entry1.grid(row=2, column=0, padx=5, pady=(0, 10), sticky="ew")
# Tab #2
tab_2 = ttk.Frame(notebook)
notebook.add(tab_2, text="Detection 2")
# Combobox
combobox2 = ttk.Combobox(tab_2, values=combo_list2, textvariable=clase2)
#combobox2.current(0)
combobox2.grid(row=0, column=0, padx=5, pady=10,  sticky="ew")
# Label
label = ttk.Label(tab_2, text="Precision:", justify="left")
label.grid(row=1, column=0)
# Entry
entry2 = ttk.Entry(tab_2, textvariable=precision2)
#entry2.insert(0)
entry2.grid(row=2, column=0, padx=5, pady=(0, 10), sticky="ew")
# Tab #3
tab_3 = ttk.Frame(notebook)
notebook.add(tab_3, text="Detection 3")
# Combobox
combobox3 = ttk.Combobox(tab_3, values=combo_list3, textvariable=clase3)
#combobox3.current(0)
combobox3.grid(row=0, column=0, padx=5, pady=10,  sticky="ew")
# Label
label = ttk.Label(tab_3, text="Precision:", justify="left")
label.grid(row=1, column=0)
# Entry
entry3 = ttk.Entry(tab_3, textvariable=precision3)
#entry3.insert(0, "0.5")
entry3.grid(row=2, column=0, padx=5, pady=(0, 10), sticky="ew")
notebook.pack(expand=True, fill="both", padx=5, pady=5)

# Create a Frame for the EVENTS
check_frame = ttk.LabelFrame(root, text="Events", padding=(20, 10))
check_frame.grid(row=1, column=1, padx=(20, 10), pady=(20, 10), sticky="nsew")
# Label
label = ttk.Label(check_frame, text="Email:", justify="left")
label.grid(row=1, column=0, padx=5, pady=10, sticky="nsew")
# Entry
entry_email = ttk.Entry(check_frame, textvariable=email)
entry_email.grid(row=2, column=0, padx=5, pady=(0, 10), sticky="ew")
# Label
label = ttk.Label(check_frame, text="File:", justify="left")
label.grid(row=3, column=0, padx=5, pady=10, sticky="nsew")
# Entry
entry_file = ttk.Entry(check_frame, textvariable=file)
entry_file.grid(row=4, column=0, padx=5, pady=(0, 10), sticky="ew")
# Label
label = ttk.Label(root, text="IP camera:")
label.grid(row=2, column=0, padx=15, pady=(0, 10), sticky="ew")
# Entry
entry_ip = ttk.Entry(root, textvariable=ip)
entry_ip.grid(row=3, column=0, padx=5, pady=(0, 10), sticky="ew")
# Button
button = ttk.Button(root, text="Exit", command=exit)
button.grid(row=4, column=1, padx=5, pady=10, sticky="nsew")

# Create a Frame for input widgets
image_frame = ttk.Frame(root, padding=(0, 0, 0, 0))
image_frame.grid(row=0, column=0, padx=10, pady=(30, 10), sticky="nsew")
image_frame.columnconfigure(index=0, weight=1)

# Crear una etiqueta de imagen en la ventana
label = tk.Label(image_frame)
label.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

# Iniciar la captura de video y mostrar la imagen en la ventana
show_frame()

# Sizegrip
sizegrip = ttk.Sizegrip(root)
sizegrip.grid(row=100, column=100, padx=(0, 5), pady=(0, 5))

# Center the window, and set minsize
root.update()
root.minsize(root.winfo_width(), root.winfo_height())
x_cordinate = int((root.winfo_screenwidth()/2) - (root.winfo_width()/2))
y_cordinate = int((root.winfo_screenheight()/2) - (root.winfo_height()/2))
root.geometry("+{}+{}".format(x_cordinate, y_cordinate))

# Start the main loop
root.mainloop()


# Detener la captura de video y liberar los recursos
cap.release()

