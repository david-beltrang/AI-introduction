% Posición de la bateria
bateria(3).
% Dimensiones de la habitacion
limite(10).
% estado(Posición Robot, Posición Caja, ¿Está sobre la caja?, ¿Tiene la batería?)
inicial(estado(1,1,no,no)).
% Estado meta (Tener batería, los otros no se especifican, aunque se conoce que en este estado, se encontrará sobre la caja y en la posición de bateria())
es_meta(estado(_,_,_,si)).

costo(mover_derecha,1).
costo(mover_izquierda,1).
costo(empujar_derecha,2).
costo(empujar_izquierda,2).
costo(subir_caja,1).
costo(agarrar_bateria,1).

% Mover derecha
accion(
        estado(PosRobot, PosCaja, no, TieneBateria),
                mover_derecha,
                estado(NuevaPosRobot, PosCaja, no, TieneBateria)
                ) :-
                limite(Limite),
                PosRobot < Limite,
                NuevaPosRobot is PosRobot + 1.

% Mover izquierda
accion(
        estado(PosRobot, PosCaja, no, TieneBateria),
                mover_izquierda,
                estado(NuevaPosRobot, PosCaja, no, TieneBateria)
                ) :-
                PosRobot > 1,
                NuevaPosRobot is PosRobot - 1.

% Empujar derecha
accion(
        estado(PosRobot, PosCaja, no, TieneBateria),
                empujar_derecha,
                estado(NuevaPosRobot, NuevaPosCaja, no, TieneBateria)
                ) :-
                limite(Limite),
                PosRobot < Limite,
                PosRobot =:= PosCaja,
                NuevaPosRobot is PosRobot + 1,
                NuevaPosCaja is PosCaja + 1.

% Empujar izquierda
accion(
        estado(PosRobot, PosCaja, no, TieneBateria),
                empujar_izquierda,
                estado(NuevaPosRobot, NuevaPosCaja, no, TieneBateria)
                ) :-
                PosRobot > 1,
                PosRobot =:= PosCaja,
                NuevaPosRobot is PosRobot - 1,
                NuevaPosCaja is PosCaja - 1.

% Subir a la Caja
accion(
        estado(PosRobot, PosCaja, no, TieneBateria),
                subir_caja,
                estado(PosRobot, PosCaja, si, TieneBateria)
                ) :-
                PosRobot =:= PosCaja.

% Agarrar Bateria
accion(
        estado(PosRobot, PosCaja, si, no),
                agarrar_bateria,
                estado(PosRobot, PosCaja, si, si)
                ) :-
                bateria(PosBateria),
                PosRobot =:= PosCaja,
                PosCaja =:= PosBateria.

% Si ya tiene la batería, su "distancia" al estado meta es 0
heuristica(estado(_, _, _, si), 0) :- !.

% Si ya está sobre la caja en la posición de la batería y aún no la ha tomado, su "distancia" al estado meta es 1
heuristica(estado(Robot,Caja,si,no),1) :-
    bateria(Bateria),
    Robot =:= Caja,
    Caja =:= Bateria, !.

heuristica(estado(Robot, Caja, Encima, no), H) :-
    bateria(B),
    DistCajaBateria is abs(Caja - B),
    DistRobotCaja is abs(Robot - Caja),
    (Encima == si -> Penalizacion = 0 ; Penalizacion = 1),
    (Robot =:= Caja -> JuntoCaja = 1 ; JuntoCaja = 0),
    H is DistCajaBateria + DistRobotCaja + Penalizacion + 1 - JuntoCaja.


% El algoritmo A* (A estrella) es un metodo de búsqueda informada utilizado comunmente para
% encontrar el camino mas corto o la ruta optima entre un nodo inicial y un nodo objetivo.
% f(n)=g(n)+h(n)

% Comienza desde un nodo inicial en un grafo y define el nodo objetivo al que quieres llegar.
% utiliza una función de evaluación f(n)=g(n)+h(n) para decidir qué nodo expandir a continuacion.
% Busca el camino que minimiza costo + heurística

% Lista abierta:

% Contiene nodos que deben evaluarse
% Ordenados por valor de f(n) (primero el mas bajo)
% Se añaden nuevos nodos a medida que se descubren

%Lista cerrada:

% Contiene nodos ya evaluados
% Ayuda a evitar la reevaluación de nodos
% Se utiliza para reconstruir la trayectoria final

% El algoritmo selecciona continuamente el nodo con el valor mas bajo de f(n) mas bajo de la lista abierta, 
% lo evalua y lo mueve a la lista cerrada hasta que llega al nodo meta o determina que no existe ningun camino.

% Punto de entrada
a_estrella(Camino) :-
    % Evaluar estado inicial
    inicial(EstadoInicial),
    % Calcula la heurística para el nodo inicial
    heuristica(EstadoInicial, H),
    % Nodo: [F, G, Estado, Camino]; costo acumulado: 0 ; lista de nodos cerrados vacía
    a_estrella_loop([[H, 0, EstadoInicial, []]], [], Camino).

% a_estrella_loop recibe: lista abierta ; lista de nodos cerrados ;  espacio para el camino solución

% Caso meta: el primer nodo de la open list es la solución ; en ese caso el camino que tomó llegar hasta ahí es la solución
a_estrella_loop([[_F, _G, Estado, Camino] | _], _, Camino) :-
    % Verificar si estado recibido es meta
    es_meta(Estado), !.


% Caso general: expandir el nodo con menor f
a_estrella_loop([[_F, G, Estado, Camino] | Resto], Cerrados, Solucion) :-

    % 1. Verificar que nodo actual no esté en cerrados
    \+ member(Estado, Cerrados),

    % 2. Generar todos los sucesores
    findall(
        [F2, G2, EstadoSig, [Accion | Camino]],         % El camino para ese nodo se construye como camino del nodo anterior mas la acción a ejecutar
        (
            accion(Estado, Accion, EstadoSig),          % Transición válida
            \+ member(EstadoSig, Cerrados),             % No visitado
            costo(Accion, CostoAccion),                 % Costo del paso
            G2 is G + CostoAccion,                      % G acumulado
            heuristica(EstadoSig, H2),                  % Heuristica
            F2 is G2 + H2                               % f = g + h
        ),
        Sucesores
    ),

    % 3. Insertar sucesores en la open list ordenada por f
    insertar_ordenado(Sucesores, Resto, NuevaOpen),

    % 4. Continuar con el estado actual en cerrados
    a_estrella_loop(NuevaOpen, [Estado | Cerrados], Solucion).


% Si el nodo ya está en cerrados, saltarlo
a_estrella_loop([_ | Resto], Cerrados, Solucion) :-
    a_estrella_loop(Resto, Cerrados, Solucion).


% Insertar una lista de nodos en la open list, manteniendo orden por F

% Si no hay nuevos nodos sucesores, se retorna la misma lista
insertar_ordenado([], Lista, Lista).

%Insertar uno a uno la lista de suceros en la lista de nodos abiertos
insertar_ordenado([Nodo | Resto], Lista, Resultado) :-
    insertar_uno(Nodo, Lista, ListaTemp),
    insertar_ordenado(Resto, ListaTemp, Resultado).


% Insertar un nodo en su posición correcta según F
% Si la lista es vacía, será el único nodo
insertar_uno(Nodo, [], [Nodo]).

% Si es menor o igual que la cabeza de lista actual, queda en la cabeza
insertar_uno([F1|R1], [[F2|R2]|Resto], [[F1|R1], [F2|R2]|Resto]) :-
    F1 =< F2, !.

% Si es mayor que la cabeza de lista actual, se busca recursivamente la posición correcta
insertar_uno(Nodo, [Cabeza|Resto], [Cabeza|Resultado]) :-
    insertar_uno(Nodo, Resto, Resultado).

% Punto de entrada que devuelve el camino en orden correcto
resolver(CaminoFinal) :-
    a_estrella(CaminoInvertido),
    reverse(CaminoInvertido, CaminoFinal).


% Imprime la secuencia de acciones
imprimir_solucion :-
    resolver(Camino),
    length(Camino, N),
    format("Solución encontrada en ~w pasos:~n", [N]),
    imprimir_pasos(Camino, 1).

imprimir_pasos([], _).
imprimir_pasos([Accion | Resto], N) :-
    format("  Paso ~w: ~w~n", [N, Accion]),
    N1 is N + 1,
    imprimir_pasos(Resto, N1).