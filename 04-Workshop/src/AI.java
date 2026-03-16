import java.awt.Graphics2D;

public class AI implements IGameObject {

    private Minimax minimax;
    private Grid grid;
    

    public AI(Grid grid){
        this.grid = grid;
        minimax = new Minimax();
    }

    public void makeMove(){
        grid.placeMarker(minimax.getBestMove(grid.getMarkers(), grid.getTurn()));
    }

    @Override
    public void update(float deltaTime) {
        // Aquí es donde se implementaría la lógica de la IA para tomar decisiones y realizar movimientos en el juego
    }

    @Override
    public void render(Graphics2D graphicsRender) {
        // La IA no necesita renderizar nada, ya que no tiene una representación visual en el juego
    }
    
}
