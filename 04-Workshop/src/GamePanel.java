import javax.swing.event.MouseInputListener;
import java.awt.*;
import java.awt.event.MouseEvent;

public class GamePanel extends Panel implements MouseInputListener {

    private Grid grid;
    private AI ai;

    // Inicializa el panel de juego, creando una instancia del tablero de juego y la inteligencia artificial, y configurando el color de fondo del panel
    public GamePanel(Color color){
        super(color);
        grid = new Grid();
        ai = new AI(grid);
    }

    @Override
    public void update(float deltaTime) {
        super.update(deltaTime);
        grid.update(deltaTime);

    }

    @Override
    public void render() {
        super.render();
        grid.render(graphicsRender);
        clear();
    }


    @Override
    public void mouseClicked(MouseEvent e) {

    }

    @Override
    public void mousePressed(MouseEvent e) {

    }

    // Maneja el evento de liberación del mouse, permitiendo al jugador realizar un movimiento en el tablero y luego permitiendo que la inteligencia artificial realice su movimiento si el juego no ha terminado
    @Override
    public void mouseReleased(MouseEvent e) {
        if(grid.isGameEnd()){
            grid.reset();
        }
        grid.mouseReleased(e);

        if(!grid.isGameEnd()){

            if(grid.getTurn() == 1){
                // 1 == O
                ai.makeMove();
            }
        }
    }

    @Override
    public void mouseEntered(MouseEvent e) {

    }

    @Override
    public void mouseExited(MouseEvent e) {

    }

    @Override
    public void mouseDragged(MouseEvent e) {

    }

    @Override
    public void mouseMoved(MouseEvent e) {
        grid.mouseMoved(e);
    }
}