RED = [1, 0, 0]
GREEN = [0, 1, 0]
BLUE = [0, 0, 1]

CYAN = [0, 1, 1]
MAGENTA = [1, 0, 1]
YELLOW = [1, 1, 0]

WHITE = [1, 1, 1]
BLACK = [0, 0, 0]

Axes = {
    'position': [
        -10, 0, 0,
        10, 0, 0,
        0, -10, 0,
        0, 10, 0,
        0, 0, -10,
        0, 0, 10 ],
    'color': [
        *RED,
        *RED,
        *GREEN,
        *GREEN,
        *BLUE,
        *BLUE ]
}

Triangle = {
    'position': [
        -0.5, -0.5, 0.0,
         0.5, -0.5, 0.0,
         0.0,  0.5, 0.0],
    'color': [
        *RED,
        *GREEN,
        *BLUE ],
}

Square = {
    'position': [
        -0.5, -0.5, 0.0,
         0.5, -0.5, 0.0,
         0.5,  0.5, 0.0,
        -0.5,  0.5, 0.0],
    'color': [
        *RED,
        *GREEN,
        *CYAN,
        *MAGENTA ],
    'indices': [
        0, 1, 2,
        2, 3, 0 ]
}

Cube = {
    'position': [
        # Cara frontal    
       -0.5, -0.5, 0.5,  
        0.5, -0.5, 0.5,  
        0.5,  0.5, 0.5,  
       -0.5,  0.5, 0.5,  
        # Cara trasera    
        0.5, -0.5, -0.5, 
       -0.5, -0.5, -0.5, 
       -0.5,  0.5, -0.5, 
        0.5,  0.5, -0.5, 
        # Cara izquierda  
       -0.5, -0.5, -0.5, 
       -0.5, -0.5,  0.5, 
       -0.5,  0.5,  0.5, 
       -0.5,  0.5, -0.5, 
        # Cara derecha    
        0.5, -0.5,  0.5,
        0.5, -0.5, -0.5,
        0.5,  0.5, -0.5,
        0.5,  0.5,  0.5,
        # Cara superior   
       -0.5,  0.5,  0.5, 
        0.5,  0.5,  0.5, 
        0.5,  0.5, -0.5, 
       -0.5,  0.5, -0.5, 
        # Cara inferior   
        0.5, -0.5,  0.5,
       -0.5, -0.5,  0.5,
       -0.5, -0.5, -0.5,
        0.5, -0.5, -0.5 ],
    'color': [
        # Cara frontal
        *BLUE,
        *BLUE,
        *BLUE,
        *BLUE,
        # Cara trasera
        *YELLOW,
        *YELLOW,
        *YELLOW,
        *YELLOW,
        # Cara izquierda
        *CYAN,
        *CYAN,
        *CYAN,
        *CYAN,
        # Cara derecha
        *RED,
        *RED,
        *RED,
        *RED,
        # Cara superior
        *GREEN,
        *GREEN,
        *GREEN,
        *GREEN,
        # Cara inferior
        *MAGENTA,
        *MAGENTA,
        *MAGENTA,
        *MAGENTA ],
    'indices': [
        # Cara frontal
        0, 1, 2,
        2, 3, 0,
        # Cara trasera
        4, 5, 6,
        6, 7, 4,
        # Cara izquierda
        8, 9, 10,
        10, 11, 8,
        # Cara derecha
        12, 13, 14,
        14, 15, 12,
        # Cara superior
        16, 17, 18,
        18, 19, 16,
        # Cara inferior
        20, 21, 22,
        22, 23, 20  ]
}

SquarePyramid = {
    'position': [
        # Cara frontal
        -0.5, -0.5,  0.5,
        0.5, -0.5,  0.5,
        0.0,  0.5,  0.0,
        # Cara trasera
        0.5, -0.5, -0.5,
       -0.5, -0.5, -0.5,
        0.0,  0.5,  0.0,
        # Cara izquierda
       -0.5, -0.5, -0.5,
       -0.5, -0.5,  0.5,
        0.0,  0.5,  0.0,
        # Cara derecha
        0.5, -0.5,  0.5,
        0.5, -0.5, -0.5,
        0.0,  0.5,  0.0,
        # Cara inferior
       -0.5, -0.5, -0.5,
        0.5, -0.5, -0.5,
        0.5, -0.5,  0.5,
       -0.5, -0.5,  0.5 ],
    'color': [
        # Cara frontal
        *BLUE,
        *BLUE,
        *GREEN,
        # Cara trasera
        *YELLOW,
        *YELLOW,
        *GREEN,
        # Cara izquierda
        *CYAN,
        *CYAN,
        *GREEN,
        # Cara derecha
        *RED,
        *RED,
        *GREEN,
        # Cara inferior
        *MAGENTA,
        *MAGENTA,
        *MAGENTA,
        *MAGENTA ],
    'indices': [
        # Cara frontal
        0, 1, 2,
        # Cara trasera
        3, 4, 5,
        # Cara izquierda
        6, 7, 8,
        # Cara derecha
        9, 10, 11,
        # Cara inferior
        12, 13, 14,
        14, 15, 12 ]
}

