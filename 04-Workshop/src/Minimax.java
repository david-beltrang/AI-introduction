import java.lang.reflect.Array;
import java.util.ArrayList;

public class Minimax {
    private int bestMove = 0;

    private int counter = 0;

    public int getBestMove(Marker[][] markers, int requester){
        bestMove = 0;
        counter = 0;
        minimax(markers, requester, true, 0, Integer.MIN_VALUE, Integer.MAX_VALUE);

        System.out.println("Minimax evaluó " + counter + " movimientos posibles");
        return bestMove;
    }

    private int minimax(Marker[][] markers, int requester, boolean requesterMove, int depth, int alpha, int beta){
        int winner = Checker.getWinType(markers);
        // Si hay un ganador o el tablero está lleno, devuelve el puntaje del estado actual del tablero para el jugador solicitante, utilizando la función de evaluación definida en getFieldScore
        if(winner >= 0 || getMarkersPlacedSize(markers) == Main.SIZE){
            return getFieldScore(markers, requester, depth);
        }

        ArrayList<Integer> scores = new ArrayList<Integer>();
        int[] openMoves = getOpenSpotsIndexes(markers);
        int score = 0;
        // Recorre todos los movimientos posibles, simulando cada movimiento y evaluando su puntaje utilizando recursión, para determinar el mejor movimiento para el jugador solicitante
        for (int i = 0; i < openMoves.length; i++){
            counter++;
            int x = openMoves[i] % Main.ROWS;
            int y = openMoves[i] / Main.ROWS;
            
            if(!requesterMove){
                depth++;
            }

            int marker = requesterMove ? requester : requester + 1;
            markers[x][y] = new Marker(marker);
            score = minimax(markers, requester, !requesterMove, depth, alpha, beta);
            scores.add(score);
            markers[x][y] = null;

            // Poda
            // Si es el turno del jugador solicitante, actualiza el valor de alpha y realiza la poda si el valor de alpha es mayor que beta, lo que indica que el jugador oponente no permitirá que se alcance ese puntaje
            if(requesterMove){
                int maxValue = Math.max(Integer.MIN_VALUE, score);
                alpha = Math.max(alpha, maxValue);
                // Si alpha es mayor que beta, se puede realizar la poda, ya que el jugador oponente no permitirá que se alcance ese puntaje
                if(alpha > beta){
                    return maxValue;
                }
            
            // Si es el turno del jugador oponente, actualiza el valor de beta y realiza la poda si el valor de beta es menor que alpha, lo que indica que el jugador solicitante no permitirá que se alcance ese puntaje
            } else {
                int minValue = Math.min(Integer.MAX_VALUE, score);
                beta = Math.min(beta, minValue);
                // Si beta es menor que alpha, se puede realizar la poda, ya que el jugador solicitante no permitirá que se alcance ese puntaje
                if(beta < alpha){
                    return minValue;
                }
            }
        }

        int scoreIndex = 0;
        // Si es el turno del jugador solicitante, selecciona el movimiento con el puntaje máximo, ya que el jugador solicitante busca maximizar su puntaje
        if(requesterMove){
            scoreIndex = getMax(scores);
        } else {
            scoreIndex = getMin(scores);
        }
        bestMove = openMoves[scoreIndex];

        return scores.get(scoreIndex);
    }

    // Devuelve el índice del movimiento con el puntaje máximo en la lista de puntajes, utilizado para seleccionar el mejor movimiento para el jugador solicitante
    private int getMax(ArrayList<Integer> scores){
        int index = 0;
        int max = 0;
        for (int i = 0; i < scores.size(); i++){
            if(scores.get(i) >= max){
                index = i;
                max = scores.get(i);
            }
        }
        return index;
    }

    // Devuelve el índice del movimiento con el puntaje mínimo en la lista de puntajes, utilizado para seleccionar el mejor movimiento para el jugador oponente
    private int getMin(ArrayList<Integer> scores){
        int index = 0;
        int min = 0;
        for (int i = 0; i < scores.size(); i++){
            if(scores.get(i) <= min){
                index = i;
                min = scores.get(i);
            }
        }
        return index;
    }

    // Evalúa el estado actual del tablero y devuelve un puntaje para el jugador solicitante, utilizando una función de evaluación que asigna puntajes positivos para estados favorables al jugador solicitante y puntajes negativos para estados desfavorables, teniendo en cuenta la profundidad de la recursión para favorecer movimientos que lleven a una victoria más rápida o a una derrota más tardía
    private int getFieldScore(Marker[][] markers, int requester, int depth){
        ArrayList<Marker> match = Checker.checkWin(markers);
        if(match == null){
            return 0;
        }

        if(match.get(0).getType() == requester){
            return Main.SIZE - depth;
        } 

        return (Main.SIZE * -1) + depth;
    }

    // Devuelve un arreglo con los índices de las posiciones abiertas en el tablero, utilizado para generar los movimientos posibles en la función minimax
    private int[] getOpenSpotsIndexes(Marker[][] markers){
        int[] openSpots = new int[Main.SIZE - getMarkersPlacedSize(markers)];
        int openSpotIndex = 0;
        for (int x = 0; x < markers.length; x++){
            for (int y = 0; y < markers[x].length; y++){
                if(markers[x][y] == null){
                    openSpots[openSpotIndex] = x + (y * Main.ROWS);
                    openSpotIndex++;
                }
            }
        }
        return openSpots;
    }

    // Devuelve el número de marcadores colocados en el tablero, utilizado para determinar el número de movimientos realizados y para evaluar el estado del tablero en la función getFieldScore
    private int getMarkersPlacedSize(Marker[][] markers){
        int result = 0;
        for (int x = 0; x < markers.length; x++){
            for (int y = 0; y < markers[x].length; y++){
                if(markers[x][y] != null){
                    result++;
                }
            }
        }
        return result;
    }
}
