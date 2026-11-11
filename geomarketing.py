# ==============================================================================
# GeoMarket Analytics | Tarea GeoMarketing
# Herramienta con interfaz gráfica (Tkinter) para calcular el gasto de los
# hogares por Nivel Socioeconómico (NSE) y, ahora, también por ESTADO, a partir
# del "concentrado hogar" de la ENIGH (archivo CSV).
# Autor: Ulises De Jesús Carranza
# ==============================================================================

# --- Importación de librerías -------------------------------------------------
# tkinter: construcción de la interfaz gráfica; ttk: widgets con estilo moderno;
# filedialog: ventanas para abrir/guardar archivos; messagebox: avisos al usuario
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
# pandas: lectura del CSV y todos los cálculos (agrupaciones, sumas, etc.)
import pandas as pd

# --- Variables globales -------------------------------------------------------
# df  -> base de datos cargada desde el CSV
# out -> tabla de resultados por NSE (la que se exporta)
df = out = None
# out_edo -> tabla de resultados por ESTADO (NUEVO), se exporta por separado
out_edo = None

# vars_gasto -> un casillero (BooleanVar) por cada variable de gasto (NUEVO)
# Guarda qué gastos están marcados con checkbox: {"alimentos": BooleanVar, ...}
vars_gasto = {}

# Nombres amigables de cada variable de gasto (NUEVO)
# Traducen los códigos técnicos del CSV a palabras que cualquier persona entiende
NOMBRES = {
    "alimentos": "Alimentos y bebidas (total)", "ali_dentro": "Alimentos dentro del hogar",
    "cereales": "Cereales (tortilla, pan, arroz)", "carnes": "Carnes", "pescado": "Pescados y mariscos",
    "leche": "Leche y derivados", "huevo": "Huevo", "aceites": "Aceites y grasas",
    "tuberculo": "Papa y otros tubérculos", "verduras": "Verduras y legumbres", "frutas": "Frutas",
    "azucar": "Azúcar y mieles", "cafe": "Café, té y chocolate", "especias": "Especias y aderezos",
    "otros_alim": "Otros alimentos", "bebidas": "Bebidas (refrescos, jugos, etc.)",
    "ali_fuera": "Alimentos fuera del hogar", "tabaco": "Tabaco",
    "vesti_calz": "Vestido y calzado (total)", "vestido": "Ropa", "calzado": "Calzado",
    "vivienda": "Vivienda y servicios (total)", "alquiler": "Renta de la vivienda",
    "pred_cons": "Predial y conservación", "agua": "Agua", "energia": "Luz y combustibles (gas, leña)",
    "limpieza": "Limpieza de la casa", "cuidados": "Cuidados de la casa", "utensilios": "Utensilios domésticos",
    "enseres": "Muebles y enseres del hogar",
    "salud": "Salud (total)", "ambul_serv": "Consultas y servicios ambulatorios",
    "aten_hosp": "Atención hospitalaria", "medic_prod": "Medicinas y productos médicos",
    "transporte": "Transporte (total)", "publico": "Transporte público", "foraneo": "Transporte foráneo",
    "adqui_vehi": "Compra de vehículos", "mantenim": "Mantenimiento de vehículos",
    "refaccion": "Refacciones y accesorios", "combus": "Gasolina y combustibles",
    "comunica": "Comunicaciones (teléfono, internet)",
    "educa_espa": "Educación y esparcimiento (total)", "educacion": "Educación",
    "esparci": "Esparcimiento y cultura", "paq_turist": "Paquetes turísticos y hospedaje",
    "personales": "Cuidado personal (total)", "cuida_pers": "Cuidado personal",
    "acces_pers": "Accesorios personales", "otros_gas": "Otros gastos diversos",
    "transf_gas": "Transferencias de gasto",
}

# Agrupación de variables por tema, para mostrarlas ordenadas en la lista (NUEVO)
GRUPOS = {
    "ALIMENTOS Y BEBIDAS": ["alimentos", "ali_dentro", "cereales", "carnes", "pescado", "leche", "huevo",
                            "aceites", "tuberculo", "verduras", "frutas", "azucar", "cafe", "especias",
                            "otros_alim", "bebidas", "ali_fuera", "tabaco"],
    "VESTIDO Y CALZADO": ["vesti_calz", "vestido", "calzado"],
    "VIVIENDA Y SERVICIOS": ["vivienda", "alquiler", "pred_cons", "agua", "energia", "limpieza",
                             "cuidados", "utensilios", "enseres"],
    "SALUD": ["salud", "ambul_serv", "aten_hosp", "medic_prod"],
    "TRANSPORTE Y COMUNICACIONES": ["transporte", "publico", "foraneo", "adqui_vehi", "mantenim",
                                    "refaccion", "combus", "comunica"],
    "EDUCACIÓN Y ESPARCIMIENTO": ["educa_espa", "educacion", "esparci", "paq_turist"],
    "CUIDADO PERSONAL Y OTROS": ["personales", "cuida_pers", "acces_pers", "otros_gas", "transf_gas"],
}

# Variables "totales" de cada tema, para el botón "Solo categorías principales" (NUEVO)
PRINCIPALES = ["alimentos", "vesti_calz", "vivienda", "salud", "transporte", "educa_espa", "personales"]

# Catálogo oficial INEGI de entidades federativas (clave -> nombre) (NUEVO)
# La clave de estado son los 2 primeros dígitos de "ubica_geo" (ej. 15001 -> 15)
ESTADOS = {
    1: "Aguascalientes", 2: "Baja California", 3: "Baja California Sur",
    4: "Campeche", 5: "Coahuila", 6: "Colima", 7: "Chiapas", 8: "Chihuahua",
    9: "Ciudad de México", 10: "Durango", 11: "Guanajuato", 12: "Guerrero",
    13: "Hidalgo", 14: "Jalisco", 15: "México", 16: "Michoacán", 17: "Morelos",
    18: "Nayarit", 19: "Nuevo León", 20: "Oaxaca", 21: "Puebla",
    22: "Querétaro", 23: "Quintana Roo", 24: "San Luis Potosí", 25: "Sinaloa",
    26: "Sonora", 27: "Tabasco", 28: "Tamaulipas", 29: "Tlaxcala",
    30: "Veracruz", 31: "Yucatán", 32: "Zacatecas",
}

# --- Ventana principal --------------------------------------------------------
# Se crea la ventana, se define su título, tamaño y color de fondo
root = tk.Tk()
root.title("Herramienta de Análisis | Tarea GeoMarketing")
root.geometry("1120x740")
root.configure(bg="#dfe3e6")

# --- Estilos visuales ---------------------------------------------------------
# Tema "clam" y personalización de la tabla (Treeview) y los botones
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview",background="white",foreground="#263238",rowheight=27,fieldbackground="white")
style.configure("Treeview.Heading",background="#e4e8eb",foreground="#263238",font=("Segoe UI",9,"bold"))
style.configure("TButton",padding=6,font=("Segoe UI",9))
# Estilo destacado (verde) para los botones principales de acción (NUEVO)
style.configure("Accent.TButton",padding=7,font=("Segoe UI",9,"bold"),background="#2e7d6b",foreground="white")
style.map("Accent.TButton",background=[("active","#256858")])

# --------------------------------------------------------------------------------
# FUNCIONES AUXILIARES DE LA LISTA DE GASTOS (NUEVAS)
# Manejan los checkboxes: dibujar, buscar, marcar/quitar y contar selección
# --------------------------------------------------------------------------------
# Devuelve el nombre amigable de una variable (o el código si no tiene nombre)
def nombre(c):
    return NOMBRES.get(c,c)

# Devuelve los códigos de todas las variables que el usuario marcó
def seleccionados():
    return [c for c,v in vars_gasto.items() if v.get()]

# Indica si una variable coincide con lo escrito en el buscador
def coincide(c):
    f=busqueda.get().strip().lower()
    return f in nombre(c).lower() or f in c.lower()

# Actualiza el texto que dice cuántos gastos están marcados
def actualizar_contador():
    n=len(seleccionados())
    contador.config(text=f"{n} gasto{'s' if n!=1 else ''} marcado{'s' if n!=1 else ''}")

# Marca o desmarca de un solo clic todos los gastos de un tema (casilla del encabezado)
def marcar_grupo(visibles,gv):
    for c in visibles:vars_gasto[c].set(gv.get())
    actualizar_contador()

# Marca (True) o quita (False) todos los gastos visibles según el buscador
def marcar_todo(valor):
    for c in vars_gasto:
        if coincide(c):vars_gasto[c].set(valor)
    dibujar_lista()

# Marca solo las categorías principales (totales de cada tema), para empezar fácil
def marcar_principales():
    for c,v in vars_gasto.items():v.set(c in PRINCIPALES)
    dibujar_lista()

# Dibuja la lista: un encabezado por tema y un checkbox por cada gasto
def dibujar_lista():
    # Borra lo dibujado antes (útil al buscar o al cargar un archivo nuevo)
    for w in marco_checks.winfo_children():w.destroy()
    # Variables que no estén en ningún tema se agrupan en "OTROS"
    asignadas={c for cs in GRUPOS.values() for c in cs}
    grupos={k:[c for c in cs if c in vars_gasto] for k,cs in GRUPOS.items()}
    resto=[c for c in vars_gasto if c not in asignadas]
    if resto:grupos["OTROS"]=resto
    hay=False
    for grupo,cols in grupos.items():
        # Solo se muestran las que coinciden con el buscador
        vis=[c for c in cols if coincide(c)]
        if not vis:continue
        hay=True
        # Encabezado del tema con casilla para marcar todo el tema
        gv=tk.BooleanVar(value=all(vars_gasto[c].get() for c in vis))
        tk.Checkbutton(marco_checks,text=grupo,variable=gv,command=lambda v=vis,g=gv:marcar_grupo(v,g),bg="#e8f0ee",fg="#263238",font=("Segoe UI",8,"bold"),anchor="w",activebackground="#e8f0ee",bd=0,highlightthickness=0).pack(fill="x",pady=(6,1))
        # Un checkbox por cada gasto, con su nombre amigable
        for c in vis:
            tk.Checkbutton(marco_checks,text=nombre(c),variable=vars_gasto[c],command=actualizar_contador,bg="white",fg="#263238",font=("Segoe UI",9),anchor="w",justify="left",wraplength=200,activebackground="white",bd=0,highlightthickness=0).pack(fill="x",padx=(16,0))
    # Mensajes cuando la lista está vacía
    if not vars_gasto:
        tk.Label(marco_checks,text="Primero carga tu archivo CSV\n(Paso 1) y aquí aparecerán\nlos gastos disponibles.",bg="white",fg="#68777e",font=("Segoe UI",9),justify="center").pack(pady=20)
    elif not hay:
        tk.Label(marco_checks,text="No hay resultados para esa búsqueda.",bg="white",fg="#68777e",font=("Segoe UI",9)).pack(pady=20)
    actualizar_contador()

# --------------------------------------------------------------------------------
# FUNCIÓN 1: cargar()
# Abre el CSV, valida columnas, crea la columna NSE y crea la lista de checkboxes de gasto
# --------------------------------------------------------------------------------
def cargar():
    global df
    # Ventana para elegir el archivo; si se cancela, no se hace nada
    f=filedialog.askopenfilename(filetypes=[("Archivos CSV","*.csv")])
    if not f:return
    try:
        # Lee el CSV detectando el separador automáticamente (utf-8-sig quita el BOM)
        df=pd.read_csv(f,sep=None,engine="python",encoding="utf-8-sig")
        # Normaliza los nombres de columnas: sin espacios y en minúsculas
        df.columns=df.columns.str.strip().str.lower()
        # Valida que existan las columnas mínimas necesarias para el análisis
        if not {"est_socio","factor","alimentos","transf_gas"}.issubset(df.columns):raise ValueError("Faltan columnas requeridas.")
        # Convierte el estrato socioeconómico (1-4) a su etiqueta de NSE
        df["NSE"]=pd.to_numeric(df.est_socio,errors="coerce").map({1:"DE",2:"CD+",3:"CC-",4:"ABC+"})
        # Productos = columnas numéricas entre "alimentos" y "transf_gas"
        p=df.loc[:,"alimentos":"transf_gas"].select_dtypes("number").columns.tolist()
        # Crea un casillero (checkbox) desmarcado por cada variable de gasto y dibuja la lista
        vars_gasto.clear()
        for x in p:vars_gasto[x]=tk.BooleanVar(value=False)
        dibujar_lista()
        # Muestra en la barra de estado el resumen de la carga
        estado.config(text=f"● Base cargada | {len(df):,} registros | {len(p)} productos")
    # Cualquier error (archivo inválido, columnas faltantes) se muestra al usuario
    except Exception as e:messagebox.showerror("Error",str(e))

# --------------------------------------------------------------------------------
# FUNCIÓN 2: calcular()
# Calcula, por cada producto seleccionado y por NSE: gasto absoluto, número de
# hogares (expandido con el factor) y gasto relativo (gasto por hogar)
# --------------------------------------------------------------------------------
def calcular():
    global out
    # Validación: debe haber datos cargados y al menos un producto seleccionado
    if df is None or not seleccionados():return messagebox.showwarning("Aviso","Primero carga el archivo y marca al menos un gasto en la lista.")
    rows=[]
    # Recorre cada gasto marcado con checkbox
    for p in seleccionados():
        # Subconjunto con NSE, factor de expansión y el gasto del producto
        d=df[["NSE","factor",p]].copy()
        # Convierte a número y sustituye valores vacíos/erróneos por 0
        d["factor"]=pd.to_numeric(d.factor,errors="coerce").fillna(0)
        d[p]=pd.to_numeric(d[p],errors="coerce").fillna(0)
        # Agrupa por NSE: suma del gasto (Absoluto) y suma de factores (Hogares),
        # en el orden ABC+, CC-, CD+, DE
        t=d.groupby("NSE").agg(Absoluto=(p,"sum"),Hogares=("factor","sum")).reindex(["ABC+","CC-","CD+","DE"]).fillna(0)
        # Gasto relativo = gasto absoluto / hogares (evita dividir entre cero)
        t["Relativo"]=t.Absoluto.div(t.Hogares.replace(0,float("nan"))).fillna(0)
        # Agrega una fila por cada NSE y una de "Total general"; el producto se muestra con su nombre amigable
        for n,r in t.iterrows():rows.append([nombre(p),n,r.Absoluto,r.Relativo,r.Hogares])
        rows.append([nombre(p),"Total general",t.Absoluto.sum(),None,t.Hogares.sum()])
    # Guarda el resultado en un DataFrame (será el que se exporte)
    out=pd.DataFrame(rows,columns=["Producto","NSE","Absoluto","Relativo","Hogares"])
    # Limpia la tabla visual y la rellena con los nuevos resultados formateados
    tabla.delete(*tabla.get_children())
    for r in rows:tabla.insert("","end",values=(r[0],r[1],f"{r[2]:,.2f}", "" if r[3] is None else f"{r[3]:.9f}",f"{r[4]:,.0f}"))
    estado.config(text=f"● Análisis completado | {len(rows)} registros")

# --------------------------------------------------------------------------------
# FUNCIÓN 3: exportar()
# Guarda en un CSV la tabla de resultados por NSE
# --------------------------------------------------------------------------------
def exportar():
    # Validación: debe existir un análisis previo
    if out is None:return messagebox.showwarning("Aviso","Primero ejecuta el análisis.")
    # Pide la ruta de guardado y escribe el CSV (utf-8-sig para abrir bien en Excel)
    f=filedialog.asksaveasfilename(defaultextension=".csv",initialfile="GeoMarket_Resultados.csv",filetypes=[("CSV","*.csv")])
    if f:out.to_csv(f,index=False,encoding="utf-8-sig");messagebox.showinfo("Exportación","Archivo guardado correctamente.")

# --------------------------------------------------------------------------------
# FUNCIÓN 4 (NUEVA): generar_por_estado()
# Igual que calcular(), pero agrupando por ESTADO en lugar de por NSE.
# El estado se obtiene de "ubica_geo" (clave geoestadística de 5 dígitos:
# 2 de entidad + 3 de municipio). Ej.: 1001 -> 1 -> Aguascalientes;
# 15106 -> 15 -> México. Los resultados se muestran en una ventana propia.
# --------------------------------------------------------------------------------
def generar_por_estado():
    global out_edo
    # Validación: debe haber datos cargados y al menos un producto seleccionado
    if df is None or not seleccionados():return messagebox.showwarning("Aviso","Primero carga el archivo y marca al menos un gasto en la lista.")
    # Validación: se requiere la columna ubica_geo para identificar el estado
    if "ubica_geo" not in df.columns:return messagebox.showerror("Error","El CSV no contiene la columna 'ubica_geo'.")
    # Clave de estado = ubica_geo // 1000 (se lee como número, por eso se pierde
    # el cero inicial: 01001 -> 1001). Luego se traduce al nombre con el catálogo
    edo=(pd.to_numeric(df.ubica_geo,errors="coerce")//1000).map(ESTADOS)
    rows=[]
    # Recorre cada gasto marcado con checkbox
    for p in seleccionados():
        # Subconjunto con estado, factor de expansión y gasto del producto
        d=pd.DataFrame({"Estado":edo,"factor":pd.to_numeric(df.factor,errors="coerce").fillna(0),p:pd.to_numeric(df[p],errors="coerce").fillna(0)})
        # Agrupa por estado: suma del gasto (Absoluto) y de factores (Hogares),
        # ordenado según la clave oficial de entidad (1 a 32)
        t=d.groupby("Estado").agg(Absoluto=(p,"sum"),Hogares=("factor","sum")).reindex(list(ESTADOS.values())).fillna(0)
        # Gasto relativo = gasto absoluto / hogares (evita dividir entre cero)
        t["Relativo"]=t.Absoluto.div(t.Hogares.replace(0,float("nan"))).fillna(0)
        # Agrega una fila por estado y una fila de "Total general" por producto
        for n,r in t.iterrows():rows.append([nombre(p),n,r.Absoluto,r.Relativo,r.Hogares])
        rows.append([nombre(p),"Total general",t.Absoluto.sum(),None,t.Hogares.sum()])
    # Guarda el resultado en un DataFrame (será el que se exporte)
    out_edo=pd.DataFrame(rows,columns=["Producto","Estado","Absoluto","Relativo","Hogares"])

    # --- Ventana secundaria con la tabla por estado ---
    win=tk.Toplevel(root)
    win.title("Tabla por estado | GeoMarket Analytics")
    win.geometry("900x600")
    win.configure(bg="#dfe3e6")
    # Marco contenedor de la tabla (mismo estilo que la tabla principal)
    marco=tk.LabelFrame(win,text="  Resultados por estado  ",bg="#f5f6f7",fg="#35444c",font=("Segoe UI",9,"bold"),padx=7,pady=7)
    marco.pack(fill="both",expand=True,padx=9,pady=(9,4))
    # Nota explicativa para quien no conoce los términos (NUEVO)
    tk.Label(win,text="Absoluto = gasto total de los hogares del estado (pesos por trimestre) · Hogares = hogares que representa · Relativo = gasto promedio por hogar",bg="#dfe3e6",fg="#52636b",font=("Segoe UI",8),wraplength=860,justify="left").pack(side="bottom",anchor="w",padx=9)
    # Tabla (Treeview) con sus columnas y anchos
    cols_e=("Producto","Estado","Absoluto","Relativo","Hogares")
    tabla_e=ttk.Treeview(marco,columns=cols_e,show="headings")
    for c,w in zip(cols_e,(150,160,160,160,140)):tabla_e.heading(c,text=c);tabla_e.column(c,width=w,anchor="center")
    # Barra de desplazamiento vertical enlazada a la tabla
    scroll_e=ttk.Scrollbar(marco,orient="vertical",command=tabla_e.yview);tabla_e.configure(yscrollcommand=scroll_e.set)
    tabla_e.pack(side="left",fill="both",expand=True);scroll_e.pack(side="right",fill="y")
    # Llena la tabla con los resultados formateados (igual que en calcular)
    for r in rows:tabla_e.insert("","end",values=(r[0],r[1],f"{r[2]:,.2f}", "" if r[3] is None else f"{r[3]:.9f}",f"{r[4]:,.0f}"))

    # Función interna: exporta la tabla por estado a CSV
    def exportar_estado():
        f=filedialog.asksaveasfilename(parent=win,defaultextension=".csv",initialfile="GeoMarket_Resultados_Estado.csv",filetypes=[("CSV","*.csv")])
        if f:out_edo.to_csv(f,index=False,encoding="utf-8-sig");messagebox.showinfo("Exportación","Archivo guardado correctamente.",parent=win)
    # Botón de exportación dentro de la ventana de estados
    ttk.Button(win,text="⇩  Exportar tabla por estado CSV",command=exportar_estado).pack(fill="x",padx=9,pady=(4,9))
    # Actualiza la barra de estado de la ventana principal
    estado.config(text=f"● Tabla por estado generada | {len(rows)} registros")

# --------------------------------------------------------------------------------
# CONSTRUCCIÓN DE LA INTERFAZ (widgets de la ventana principal)
# --------------------------------------------------------------------------------
# Encabezado superior con el nombre de la herramienta y su versión
header=tk.Frame(root,bg="#f5f6f7",height=43);header.pack(fill="x")
tk.Label(header,text="▦  GeoMarket Analytics",bg="#f5f6f7",fg="#263238",font=("Segoe UI",12,"bold")).pack(side="left",padx=14,pady=9)
tk.Label(header,text="HERRAMIENTA DE ANÁLISIS  |  v1.1",bg="#f5f6f7",fg="#65747d",font=("Segoe UI",8)).pack(side="right",padx=14)
# Créditos del autor
tk.Label(root,text="Autor: Ulises De Jesús Carranza",bg="#dfe3e6",fg="#59666e",font=("Segoe UI",8)).pack(anchor="e",padx=12)
# Contenedor principal: panel izquierdo (parámetros) y panel derecho (resultados)
body=tk.Frame(root,bg="#dfe3e6");body.pack(fill="both",expand=True,padx=9,pady=5)

# --- Panel izquierdo: guiado en 3 pasos para que sea fácil de usar ---
left=tk.LabelFrame(body,text="  Parámetros de procesamiento  ",bg="#f5f6f7",fg="#35444c",font=("Segoe UI",9,"bold"),width=300,padx=10,pady=9);left.pack(side="left",fill="y",padx=(0,7));left.pack_propagate(False)
# PASO 1: cargar el archivo CSV y ver el estado de la carga
tk.Label(left,text="PASO 1  ·  Carga tu archivo",bg="#f5f6f7",fg="#2e7d6b",font=("Segoe UI",9,"bold")).pack(anchor="w",pady=(2,3))
ttk.Button(left,text="▤  Cargar concentrado hogar",command=cargar).pack(fill="x",pady=3)
estado=tk.Label(left,text="○ Aún no has cargado ningún archivo",bg="#f5f6f7",fg="#68777e",font=("Segoe UI",8),wraplength=265,justify="left");estado.pack(anchor="w",pady=4)
ttk.Separator(left).pack(fill="x",pady=5)
# PASO 2: elegir los gastos con checkboxes (con buscador y atajos)
tk.Label(left,text="PASO 2  ·  Marca los gastos a analizar",bg="#f5f6f7",fg="#2e7d6b",font=("Segoe UI",9,"bold")).pack(anchor="w",pady=(2,3))
# Buscador: filtra la lista mientras se escribe
busqueda=tk.StringVar();busqueda.trace_add("write",lambda *a:dibujar_lista())
tk.Label(left,text="Buscar un gasto (ej. carne, luz, salud):",bg="#f5f6f7",fg="#52636b",font=("Segoe UI",8)).pack(anchor="w")
ttk.Entry(left,textvariable=busqueda).pack(fill="x",pady=(1,4))
# Atajos: marcar todo, quitar todo y solo categorías principales
fila=tk.Frame(left,bg="#f5f6f7");fila.pack(fill="x")
ttk.Button(fila,text="Marcar todo",command=lambda:marcar_todo(True)).pack(side="left",expand=True,fill="x",padx=(0,2))
ttk.Button(fila,text="Quitar todo",command=lambda:marcar_todo(False)).pack(side="left",expand=True,fill="x",padx=(2,0))
ttk.Button(left,text="Solo categorías principales",command=marcar_principales).pack(fill="x",pady=(3,4))
# Zona con scroll que contiene los checkboxes (Canvas + barra + marco interior)
caja=tk.Frame(left,bg="white",relief="solid",borderwidth=1);caja.pack(fill="both",expand=True)
canvas_checks=tk.Canvas(caja,bg="white",highlightthickness=0,height=120)
barra=ttk.Scrollbar(caja,orient="vertical",command=canvas_checks.yview);canvas_checks.configure(yscrollcommand=barra.set)
barra.pack(side="right",fill="y");canvas_checks.pack(side="left",fill="both",expand=True)
marco_checks=tk.Frame(canvas_checks,bg="white")
ventana_checks=canvas_checks.create_window((0,0),window=marco_checks,anchor="nw")
# Ajusta el área desplazable y el ancho del marco cuando cambia el tamaño
marco_checks.bind("<Configure>",lambda e:canvas_checks.configure(scrollregion=canvas_checks.bbox("all")))
canvas_checks.bind("<Configure>",lambda e:canvas_checks.itemconfig(ventana_checks,width=e.width))
# Permite desplazar la lista con la rueda del mouse cuando el cursor está encima
def rueda(e):
    canvas_checks.yview_scroll(int(-e.delta/120) if e.delta else (-1 if e.num==4 else 1),"units")
for ev in ("<MouseWheel>","<Button-4>","<Button-5>"):
    canvas_checks.bind(ev,rueda);marco_checks.bind(ev,rueda)
canvas_checks.bind("<Enter>",lambda e:[canvas_checks.bind_all(ev,rueda) for ev in ("<MouseWheel>","<Button-4>","<Button-5>")])
canvas_checks.bind("<Leave>",lambda e:[canvas_checks.unbind_all(ev) for ev in ("<MouseWheel>","<Button-4>","<Button-5>")])
# Contador de gastos marcados
contador=tk.Label(left,text="0 gastos marcados",bg="#f5f6f7",fg="#35444c",font=("Segoe UI",8,"bold"));contador.pack(anchor="w",pady=(3,0))
ttk.Separator(left).pack(fill="x",pady=5)
# PASO 3: obtener resultados (por nivel socioeconómico o por estado) y exportar
tk.Label(left,text="PASO 3  ·  Obtén tus resultados",bg="#f5f6f7",fg="#2e7d6b",font=("Segoe UI",9,"bold")).pack(anchor="w",pady=(2,3))
ttk.Button(left,text="▶  Ver resultados por nivel socioeconómico",style="Accent.TButton",command=calcular).pack(fill="x",pady=2)
ttk.Button(left,text="▶  Ver resultados por estado",style="Accent.TButton",command=generar_por_estado).pack(fill="x",pady=2)
ttk.Button(left,text="⇩  Guardar resultados en CSV",command=exportar).pack(fill="x",pady=2)
# Dibuja la lista vacía inicial con su mensaje de ayuda
dibujar_lista()

# --- Panel derecho: tabla de resultados por NSE ---
right=tk.LabelFrame(body,text="  Tabla de resultados  ",bg="#f5f6f7",fg="#35444c",font=("Segoe UI",9,"bold"),padx=7,pady=7);right.pack(side="left",fill="both",expand=True)
# Guía "¿Cómo leer esta tabla?" para personas sin conocimientos del tema (NUEVO)
guia=tk.LabelFrame(right,text="  ¿Cómo leer esta tabla?  ",bg="#f5f6f7",fg="#35444c",font=("Segoe UI",8,"bold"),padx=8,pady=4);guia.pack(side="bottom",fill="x",pady=(6,0))
tk.Label(guia,text=("• NSE (nivel socioeconómico del hogar): ABC+ = alto · CC- = medio · CD+ = medio bajo · DE = bajo.\n"
    "• Absoluto: dinero total que gastan en ese concepto todos los hogares del grupo (pesos por trimestre).\n"
    "• Hogares: cuántos hogares representa ese grupo en el país.\n"
    "• Relativo: gasto promedio por hogar (Absoluto ÷ Hogares)."),bg="#f5f6f7",fg="#52636b",font=("Segoe UI",8),justify="left",anchor="w",wraplength=700).pack(anchor="w")
# Columnas de la tabla y su ancho; todas centradas
cols=("Producto","NSE","Absoluto","Relativo","Hogares")
tabla=ttk.Treeview(right,columns=cols,show="headings")
for c,w in zip(cols,(150,100,160,160,140)):tabla.heading(c,text=c);tabla.column(c,width=w,anchor="center")
# Barra de desplazamiento vertical enlazada a la tabla
scroll=ttk.Scrollbar(right,orient="vertical",command=tabla.yview);tabla.configure(yscrollcommand=scroll.set)
tabla.pack(side="left",fill="both",expand=True);scroll.pack(side="right",fill="y")
# Pie de página
footer=tk.Label(root,text="GEOMARKET ANALYTICS  |  ANÁLISIS SOCIOECONÓMICO Y GEOGRÁFICO",bg="#cbd2d6",fg="#52616a",font=("Segoe UI",8,"bold"),pady=6);footer.pack(fill="x",side="bottom")

# --- Inicio de la aplicación --------------------------------------------------
# Mantiene la ventana abierta escuchando los eventos del usuario
root.mainloop()