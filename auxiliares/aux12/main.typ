#import "@preview/enunciado-facil-fcfm:0.1.0" as template

#show: template.conf.with(
  titulo: "Auxiliar 12",
  subtitulo: "Repaso C2",
  departamento: template.departamentos.dcc,
  curso: [CC3501 --- Modelación y Computación Gráfica para Ingenieros],
)

#set heading(numbering: "1.")
#show link: x => text(fill: blue, underline(x))
// = Resumen
//
// = Problemas

#set enum(numbering: "P1) ")

+ *(P1 C2 2022 Primavera)* Iluminación local 

  _Cel-shading_ o _toon shading_ es una técnica de sombreado que da una apariencia de dibujo animado a los objetos. La siguiente imagen ejemplifica la diferencia entre el sombreado de Phong y el sombreado toon. En resumen, el sombreado estilo dibujo animado tiene dos características: primero, utiliza dos tonos de color; segundo, se delinean los bordes del objeto dibujado con un contorno de color negro.

  #align(center, image("p1.png"))

  #enum(numbering: "a.", 
  [Defina una ecuación del modelo de _toon shading_ (puede basarse en el modelo de iluminación de Phong) para las tonalidades de color. ], 
  [Describa en pseudo-código el vertex program y el fragment program que implementa las tonalidades y el delineamiento (hint: el contorno es calculado en el fragment program).])

+ Mallas geométricas 
  #enum(numbering: "i.",
  [
  *(P2 Examen 2022 Primavera)* Supongamos que tenemos un vértice $v$ en una estructura _Half-Edge_ y queremos dibujar el polígono indicado en la figura; es decir, un polígono cuyos vértices son los centros de los triángulos adyacentes a triángulos que contienen a $v$ (en algún orden consistente, no importa si está a favor o en contra de las agujas del reloj). ¿Cuál de los siguientes códigos no extraen correctamente los vértices blancos marcados?
  #grid(columns: (2fr, 1fr), [
  #enum(numbering: "a.", block(stroke: black + .5pt, inset: 10pt, [
    ```python
    P = []
    he = v.he
    P.append(he.next.twin.face.center)
    he = he.twin.next

    while (he != v.he):
      P.append(he.next.twin.face.center)
      he = he.twin.next
    ``` ]), 
      block(stroke: black + .5pt, inset: 10pt, [
    ```python
    P = []
    he = v.he.next.next
    P.append(he.next.next.twin.face.center)
    he = he.twin.next.next

    while (he != v.he.next.next):
      P.append(he.next.next.twin.face.center)
      he = he.twin.next.next
    ``` ]),
      block(stroke: black + .5pt, inset: 10pt, [
    ```python
    P = []
    he = v.he.next
    P.append(he.twin.face.center)
    he = he.next.twin.next

    while (he != v.he):
      P.append(he.twin.face.center)
      he = he.next.twin.next
    ``` ]),
      block(stroke: black + .5pt, inset: 10pt, [
    ```python
    P = []
    he = v.he.next.twin
    P.append(he.face.center)
    he = he.twin.next.twin.next.twin

    while (he != v.he.next.twin):
      P.append(he.face.center)
      he = he.twin.next.twin.next.twin
    ``` ]), [Todas las anteriores]
    )
  ], [
  #align(center, image("p2.png"))
  ])], 
  [ *(P3-1 C3 2019 Otoño)* Dibuje 2 árboles de geometría sólido constructiva que generen la figura siguiente. Considere que usted dispone de las figuras básicas círculo y triángulo. Su árbol debe ignorar las transformaciones lineales básicas.
  #align(center, image("p3.png", width: 80%))

  ])
  

+ *(P3 C2 2022 Primavera)* Física 

  Tenemos un sistema de péndulo 2D como el siguiente:

  #align(center, image("p4.png", width: 60%))

  Donde $O$ es el origen de coordenadas y $L$ es la longitud de la cuerda que sostiene a un cuerpo con masa. La fuerza que hace que el cuerpo quiera caer es $m g$ donde $m$ es la masa del objeto y $g$ es la aceleración de la gravedad. Si uno conoce el ángulo del péndulo en algún momento dado, entonces la posición del objeto se calcula como

  #align(center)[
  $x = L sin(theta)$

  $y = - L cos(theta)$
  ]
  
  El problema del péndulo se puede formular como una ecuación diferencial que depende del ángulo. La ecuación diferencial es la siguiente:

  #align(center)[
  $theta '' = - g/L theta$
  ]
  
  Escriba un algoritmo (o función de Python) que reciba como parámetros un ángulo inicial y genere la animación del péndulo. Use el método de Euler para resolver la ecuación y hacer su algoritmo.

  *Hint:* la ecuación es de segundo grado, por lo que puede servir formular la ecuación como dos ecuaciones de primer grado. En su algoritmo puede asumir que existe una función que dibuja un objeto en una posición dada.

+ *(P1 Examen 2016 Primavera)* Curvas 

  #enum(numbering: "a.", [
  *(Propuesto)* Clasifica los métodos de representación de curvas de cúbicas Naturales, Hermite, Cardinal splines y Bezier con respecto a si son (i) un método de aproximación o interpolación, (ii) si pasa por los puntos extremos o no, (iii) cuántos y cuáles parámetros necesita, (iv) facilidad/dificultad en que un usuario pueda especificar rapidamente los parámetros correctos para la figura deseada. Da un ranking para los métodos (1, 2, 3 y 4, donde 1 es el mas fácil y 4 el más difícil). Justifica tu respuesta.
  ], [
  Contruye el polinomio cúbico usando el método de Hermite entre los puntos $P_1$ $(1,1)$ y $P_2$ $(7,6)$, considerando que la derivada en $P_1$ es $(1,-1)$ y en $P_2$ es $(1,0)$. Dibuja los parámetros especificados. Usa los gráficos de las funciones de blending para evaluar el polinomio en $u=0$, $u=0.25$, $u=0.5$, $u=0.75$, y $u=1$. Dibuja aproximadamente la curva resultante.
  ], [
  Construye el polinomio cúbico usando las _splines_ de Catmull Rom#footnote("La versión original se hacia con la versión de Bézier") para los mismos puntos $P_1$ $(1,1)$, $P_2$ $(3,4)$ $P_3$ $(5,4)$ y $P_4$ $(7,6)$. Usa también los gráficos de las funciones de blending para evaluar en los valores de u especificados. Dibuja aproximadamente la curva resultante.
  ]
  )

