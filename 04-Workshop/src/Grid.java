import java.awt.*;
import java.awt.event.MouseEvent;
import java.util.ArrayList;

public class Grid implements IGameObject {
    private ArrayList<Placement> placements = new ArrayList<>(Main.SIZE);
    private Marker[][] markers;
    private int gridThickness = 16;
    private int markerIndex = 0;
    private boolean gameEnd = false;
    private int winType=-1;

    // Inicializa el tablero de juego, creando las posiciones para colocar los marcadores y reiniciando el estado del juego
    public Grid() {
        markers = new Marker[Main.ROWS][Main.ROWS];
        // Crea las posiciones para colocar los marcadores, asignando las coordenadas y el tamaño de cada posición en función del tamaño del tablero y el número de filas
        for(int i=0; i < Main.SIZE; i++){
            int xIndex = i % Main.ROWS;
            int yIndex = i / Main.ROWS;
            int size = Main.WIDTH / Main.ROWS;
            placements.add(new Placement(xIndex * size, yIndex * size, xIndex, yIndex, size, size));
        }
        reset();
    }

    // Actualiza el estado del juego, actualizando cada posición de colocación y cada marcador en el tablero
    @Override
    public void update(float deltaTime) {
        for (Placement placement : placements) {
            placement.update(deltaTime);
        }
        for(int x=0; x < markers.length; x++){
            for(int y=0; y < markers[x].length; y++){
                if(markers[x][y] == null){
                    continue;
                }
                markers[x][y].update(deltaTime);
            }
        }
    }

    // Renderiza el tablero de juego, renderizando cada marcador en el tablero, cada posición de colocación y la cuadrícula del tablero
    @Override
    public void render(Graphics2D graphicsRender) {
        for(int x=0; x < markers.length; x++){
            for(int y=0; y < markers[x].length; y++){
                if(markers[x][y] == null){
                    continue;
                }
                markers[x][y].render(graphicsRender);
            }
        }

        for (Placement placement : placements) {
            placement.render(graphicsRender);
        }
        renderGrid(graphicsRender);
    }

    // Renderiza la cuadrícula del tablero, dibujando líneas verticales y horizontales para separar las celdas del tablero, y mostrando una superposición de fin de juego si el juego ha terminado
    private void renderGrid(Graphics2D graphicsRender) {
        graphicsRender.setColor(new Color(0x2e2e2e));

        int rowSize = Main.WIDTH / Main.ROWS;
        for (int i = 1; i < Main.ROWS+1; i++) {
            graphicsRender.fillRect(i * rowSize - (gridThickness / 2), 0, gridThickness, Main.WIDTH);
            for (int j = 1; j < Main.ROWS+1; j++) {
                graphicsRender.fillRect(0, j * rowSize - (gridThickness / 2), Main.WIDTH, gridThickness);

            }
        }

        graphicsRender.setColor(Color.white);
        if(gameEnd){
            drawEndGameOverLay(graphicsRender);
        }
    }

    // Dibuja una superposición de fin de juego, mostrando un mensaje indicando el resultado del juego (ganador o empate) y una invitación para reiniciar el juego
    private void drawEndGameOverLay(Graphics2D graphicsRender) {
        graphicsRender.setColor(new Color(0,0,0,(int)(225 * 0.5f)));

        graphicsRender.fillRect(0, 0, Main.WIDTH, Main.WIDTH);
        graphicsRender.setColor(Color.white);

        if(winType == -1){
            graphicsRender.drawString("Empate", 195, 235);
        } else {
            graphicsRender.drawString("Gana el jugador " + (winType == 0 ? "X" : "O"), 175, 235);
        }

        graphicsRender.drawString("Haz click para reiniciar", 125, 265);
    }

    // Maneja el evento de movimiento del mouse, verificando si el juego ha terminado y, si no es así, verificando si el mouse está sobre alguna posición de colocación para activar la interacción con esa posición
    public void mouseMoved(MouseEvent e) {
        if(gameEnd){
            return;
        }
        for (Placement placement : placements) {
            placement.checkCollision(e.getX(), e.getY() - 30);
        }
    }

    // Maneja el evento de liberación del mouse, verificando si el juego ha terminado y, si no es así, verificando si alguna posición de colocación está activa para colocar un marcador en esa posición, actualizar el estado del juego y verificar si hay un ganador o un empate
    public void mouseReleased(MouseEvent e) {
        for (Placement placement : placements){
            if(placement.isActive()){
                placement.set(true);
                int x = placement.getxIndex();
                int y = placement.getyIndex();
                markers[x][y] = new Marker(x, y, markerIndex);
                markerIndex++;

                ArrayList<Marker> winLine = Checker.checkWin(markers);
                if(winLine != null) {
                    winLine.forEach(marker -> marker.setWon(true));
                    winType = winLine.get(0).getType();
                    System.out.println("Gana el jugador " + (winType == 0 ? "X" : "O"));
                    gameEnd = true;
                } else if (markerIndex >= Main.SIZE) {
                    System.out.println("Empate");
                    gameEnd = true;
                }
            }
        }
    }

    // Reinicia el estado del juego, limpiando el tablero de marcadores, reiniciando las posiciones de colocación y restableciendo las variables de estado del juego a sus valores iniciales
    public void reset(){
        for(int x=0; x < markers.length; x++){
            for(int y=0; y < markers[x].length; y++){
                markers[x][y] = null;
            }
        }

        // Reinicia las posiciones de colocación
        for(Placement placement : placements){
            placement.set(false);
        }
        gameEnd = false;
        winType = -1;
        markerIndex=0;
    }

    public boolean isGameEnd() {
        return gameEnd;
    }
}
