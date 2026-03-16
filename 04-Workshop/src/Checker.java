import java.util.ArrayList;

public class Checker {
    // Revisa si hay un ganador, devuelve una lista con los marcadores que forman la combinación ganadora, o null si no hay ganador
    public static ArrayList<Marker> checkWin(Marker[][] markers){
        ArrayList<Marker> match = null;
        for ( int i = 0; i < Main.SIZE; i++){
            int x = i % Main.ROWS;
            int y = i / Main.ROWS;
            //Diagonal abajo-izquierda a arriba-derecha
            match = checkMatch(x, y, 1, -1, i, markers);
            //Diagonal arriba-izquierda a abajo-derecha
            if(match == null){
                match = checkMatch(x, y, 1, 1, i, markers);
            }
            //Horizontal
            if(match == null){
                match = checkMatch(x, y, 0, 1, i, markers);
            }
            //Vertical
            if(match == null){
                match = checkMatch(x, y, 1, 0, i, markers);
            }
            if(match != null){
                break;
            }
        }
        return match;
    }

    // Revisa si hay una combinación ganadora en una dirección específica, devuelve una lista con los marcadores que forman la combinación ganadora, o null si no hay ganador
    private static ArrayList<Marker> checkMatch (int x, int y, int dX, int dY, int index, Marker[][] markers){
        ArrayList<Marker> match = new ArrayList<>(Main.MATCH);
        int type = -1;
        int checkCount = 0;
        // Recorre la dirección especificada, buscando marcadores del mismo tipo, hasta encontrar un marcador diferente o llegar al límite del tablero
        while(checkCount < Main.ROWS && index<Main.SIZE && x>=0 && x<= Main.ROWS -1 && y>=0 && y<= Main.ROWS -1){
            boolean found = false;
            Marker maker = markers[x][y];
            // Si encuentra un marcador, verifica si es del mismo tipo que los marcadores anteriores en la combinación 
            if(maker != null){
                if(type == -1){
                    type = maker.getType();
                }
                if(maker.getType() == type){
                    match.add(maker);
                    found = true;
                }
            }

            // Si encuentra un marcador diferente o no encuentra un marcador, reinicia la combinación
            if(!found && match.size() < Main.MATCH){
                match.clear();
                type = -1;
            }
            x += dX;
            y += dY;
            index ++;
            checkCount++;

        }
        return match.size() >= Main.MATCH ? match : null;
    }
}
